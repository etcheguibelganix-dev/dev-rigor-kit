---
name: auto-compact
description: >
  Monitore automatiquement l'utilisation du contexte de session et compacte a ~50% de capacite.

  DECLENCHEURS -- invocation initiale :
  "/auto-compact", "demarre le moniteur de contexte", "lance l'auto-compact",
  "active la surveillance du contexte", "demarre la veille de contexte",
  "start auto-compact", "watch context".

  DECLENCHEUR -- wakeup interne (NE PAS modifier) :
  "auto-compact: controle contexte" -- emis automatiquement par ScheduleWakeup
  a chaque reveil du loop. Ce prompt doit toujours reinvoquer ce skill.

  Comportement :
  - Loop autonome via ScheduleWakeup (270 secondes, dans la fenetre de cache)
  - Estimation du niveau de contexte a chaque wakeup
  - A ~50% : alerte + lancement de /compact (compacts 1 et 2)
  - Au 3eme declenchement : alerte + validation utilisateur + session-finalize
  - Ne jamais agir si une action multi-etapes est en cours
---

# Auto-Compact -- Moniteur de contexte de session

Surveille silencieusement le niveau de contexte et compacte automatiquement avant
que le contexte ne soit plein. Protege les sessions longues sans interrompre le travail.

Generique -- fonctionne sur tout projet utilisant le dev-rigor-kit.

---

## Fichier d'etat

Le fichier d'etat est dans le dossier Claude Code de l'utilisateur.
Chemin calcule dynamiquement : `os.path.join(os.path.expanduser("~"), ".claude", "auto-compact-state.json")`

Structure :
```json
{
  "loop_started": "2026-05-19T14:30:00",
  "compact_count": 0,
  "last_compact": null,
  "last_wakeup": null
}
```

---

## PHASE 1 -- Demarrage (invocation directe par l'utilisateur)

Executer a chaque fois que l'utilisateur invoque le skill par une des phrases de demarrage.

### 1a -- Lire ou initialiser l'etat

```bash
python -c "
import json, os
from datetime import datetime, timezone

sf = os.path.join(os.path.expanduser('~'), '.claude', 'auto-compact-state.json')

if os.path.exists(sf):
    state = json.load(open(sf))
    started = datetime.fromisoformat(state['loop_started'])
    elapsed_h = (datetime.now(timezone.utc) - started.replace(tzinfo=timezone.utc)).total_seconds() / 3600
    if elapsed_h > 3:
        state = None
else:
    state = None

if state is None:
    state = {'loop_started': datetime.now().isoformat(), 'compact_count': 0, 'last_compact': None, 'last_wakeup': None}
    open(sf, 'w').write(json.dumps(state, indent=2))
    print('NEW session:', state)
else:
    print('CONTINUE session compact_count=' + str(state['compact_count']))
"
```

- Si nouvelle session : fichier cree avec `compact_count = 0`
- Si session en cours (< 3h) : utiliser l'etat existant

### 1b -- Afficher la confirmation

```
Moniteur de contexte demarre
   compact_count : N  |  session : HH:MM
   Prochain controle dans 270s
```

### 1c -- Planifier le premier wakeup

```
ScheduleWakeup(
  delaySeconds=270,
  reason="Controle niveau contexte session (auto-compact)",
  prompt="auto-compact: controle contexte"
)
```

**S'arreter ici.** Le loop prend le relais a chaque reveil.

---

## PHASE 2 -- Wakeup (loop autonome)

Executer a chaque reception du prompt `"auto-compact: controle contexte"`.

### 2a -- Lire l'etat

```bash
python -c "
import json, os
sf = os.path.join(os.path.expanduser('~'), '.claude', 'auto-compact-state.json')
state = json.load(open(sf))
print(json.dumps(state))
"
```

Extraire : `compact_count`, `loop_started`.

### 2b -- Estimer le niveau de contexte

Utiliser les signaux suivants, par ordre de priorite :

**Signal 1 -- Alerte systeme 70-80% deja emise**
Si le message `"Alerte memoire"` est visible dans le contexte recent : niveau > 65%.
-> Agir immediatement (seuil depasse, ne pas attendre).

**Signal 2 -- Duree de session**
Calculer `elapsed = maintenant - loop_started` en minutes :
- < 20 min : niveau ~20-30% -> pas encore, reschedule
- 20-35 min : niveau ~30-45% -> surveiller, reschedule
- 35-55 min : niveau ~45-65% -> seuil d'action atteint
- > 55 min : niveau > 65% -> agir immediatement

**Signal 3 -- Densite de la conversation observable**
Si plusieurs lectures de fichiers > 500 lignes, nombreux diffs, appels imbriques :
-> Reduire les seuils de 10 minutes.

**Decision finale :**
- Niveau < 50% : `action = "wait"`, reschedule 270s
- Niveau >= 50% et pas d'action en cours : `action = "compact"`
- Incertitude : `action = "wait"`, reschedule 120s

### 2c -- Verifier qu'aucune action n'est en cours

**NE PAS compacter si** :
- Milieu d'une sequence multi-etapes (migration DB, tests, build, ingestion)
- Dernier message Claude contient "je continue...", "etape N/M...", "en cours..."

Si incertain : `action = "wait"`, reschedule 120s.

### 2d -- Brancher selon `compact_count`

#### Si `action = "wait"` :

```
ScheduleWakeup(delaySeconds=270, reason="Contexte <50% ou action en cours", prompt="auto-compact: controle contexte")
```

Mettre a jour `last_wakeup` dans le fichier d'etat. Mode silencieux.

#### Si `action = "compact"` et `compact_count < 2` (1er ou 2eme compact) :

-> Executer la **PHASE 3 -- Compact automatique**

#### Si `action = "compact"` et `compact_count >= 2` (3eme declenchement) :

-> Executer la **PHASE 4 -- Fin de session**

---

## PHASE 3 -- Compact automatique (compacts 1 et 2)

### 3a -- Afficher l'alerte

```
--------------------------------------
CONTEXTE ~50% -- Compact automatique #N
   Session : Xh Ymin  |  compact_count : N -> N+1
--------------------------------------
```

### 3b -- Mettre a jour l'etat

```bash
python -c "
import json, os
from datetime import datetime
sf = os.path.join(os.path.expanduser('~'), '.claude', 'auto-compact-state.json')
state = json.load(open(sf))
state['compact_count'] += 1
state['last_compact'] = datetime.now().isoformat()
open(sf, 'w').write(json.dumps(state, indent=2))
print('compact_count now:', state['compact_count'])
"
```

### 3c -- Lancer le compact

```
Skill(skill="compact")
```

Si le skill `compact` n'est pas disponible : afficher `/compact` et attendre que l'utilisateur l'execute.

### 3d -- Reschedule post-compact

```
ScheduleWakeup(delaySeconds=270, reason="Post-compact #N -- reprise surveillance", prompt="auto-compact: controle contexte")
```

---

## PHASE 4 -- Fin de session (3eme declenchement)

### 4a -- Afficher l'alerte de fin de session

```
==========================================
CONTEXTE CRITIQUE -- 3eme compact detecte

   La session approche de sa limite. Il est temps de finaliser.

   Confirme qu'aucune action n'est en cours, puis :
   -> "ok" / "go" / "c'est bon" pour lancer session-finalize
   -> "attends" / "plus tard" / "pas maintenant" pour reporter 5 min
==========================================
```

**NE PAS reschedule immediatement. Attendre la reponse de l'utilisateur.**

### 4b -- Brancher sur la reponse

**Reponse positive** ("ok", "go", "oui", "c'est bon", "lance") :

1. Mettre a jour l'etat : `compact_count += 1`
2. Invoquer le skill de finalisation :
   ```
   Skill(skill="session-finalize")
   ```

**Reponse negative** ("attends", "plus tard", "pas maintenant", "stop") :

1. Reschedule dans 300s
2. Afficher : `Finalisation reportee -- controle dans 5 min`

---

## Regles absolues

- **JAMAIS interrompre** une sequence multi-etapes active
- **JAMAIS agir** si incertitude sur les actions en cours
- **TOUJOURS reschedule** apres chaque wakeup (sauf attente reponse Phase 4)
- `compact_count` repart a 0 si `loop_started` a > 3h
- Mode silencieux pendant les wakeups sans action
- Wakeup a 270s (< 300s) pour rester dans la fenetre de cache

---

## Frequence recommandee selon le type de session

| Type de session | Seuil 50% estime | Wakeups avant action |
|----------------|-----------------|---------------------|
| Dense (gros fichiers, diffs, tests) | ~30-35 min | ~7 wakeups |
| Normale (developpement standard) | ~45-50 min | ~10 wakeups |
| Legere (questions, review) | ~70-80 min | ~16 wakeups |

Ces estimations sont calibrees pour un contexte de ~200K tokens (Claude Sonnet).

---

## Demarrage recommande en debut de session

Au debut de chaque session de developpement, invoquer le skill :
```
/auto-compact
```
Ou dire : "demarre le moniteur de contexte"
