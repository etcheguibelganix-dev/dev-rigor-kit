---
name: session-start
description: >
  Synchronise une session de developpement au demarrage ou apres une pause.
  Declenche sur : "synchronise la session", "reprend le projet", "demarre la session",
  "charge le contexte", "remets-toi au contexte", "session start", "reprend le travail",
  ou toute formulation indiquant que l'utilisateur veut demarrer ou reprendre le travail.
  NE PAS declencher pour des questions ponctuelles ou des demandes de code.

  Ce skill verifie l'etat de l'environnement au demarrage : git pull -> memoire -> HANDOFF.md
  -> checks environnement -> resume. Generique -- specificites projet via PROJECT_CONFIG et CLAUDE.md.
  Seul commit autorise : mise a jour du HANDOFF.md (chore atomique).
---

# Session Start -- Synchronisation (generique)

Sequence de demarrage/reprise de session. Execute les etapes dans l'ordre.
Aucun commit de code -- seul HANDOFF.md produit un commit chore atomique.

<!-- PROJECT_CONFIG_BEGIN -->
**Projet :** `{{PROJECT_PATH}}`
**Branche :** `develop`
**Memoire :** `{{MEMORY_PATH}}`
**Appareil :** lire `.device` a la racine (ex: pc_fixe | laptop). Si absent : utiliser `socket.gethostname()`.
<!-- PROJECT_CONFIG_END -->

---

## Regles absolues

- Jamais de commit de code dans ce skill (seul HANDOFF.md chore est autorise)
- Si git pull echoue (conflits) : alerter, ne pas continuer sans accord utilisateur
- Mode informatif : signaler, ne pas modifier sans demande explicite

---

## Etape 1 -- Git pull

```bash
git pull origin [branche]
git log --oneline -5
git status
```

Traiter les resultats :
- **A jour** : continuer
- **N nouveaux commits** : lister SHAs + messages (travail de l'autre appareil depuis le dernier pull)
- **Conflits** : lister les fichiers conflictuels, **alerter, attendre instruction avant de continuer**
- **Dirty tree** : lister les fichiers modifies non commites (informatif, ne pas bloquer)
- **En avance sur origin** : signaler les commits non pushes (oubli de push?)

---

## Etape 2 -- Resume memoire

La memoire est deja chargee automatiquement dans le contexte de session (system-reminder).
Cette etape produit un resume condense actif pour ancrer la session.

Lire `MEMORY.md` (index) puis les fichiers memoire pertinents listes.

Afficher :
```
Memoire :
  Phase courante    : Phase N -- [description]
  Derniere decision : [decision cle la plus recente]
  Contrainte cle    : [invariant important : ex: append-only, jamais .env, port 5433]
```

---

## Etape 3 -- HANDOFF.md

### Si `HANDOFF.md` existe a la racine

#### 3a -- Lire

Extraire :
- Table "Sync des appareils" : quelle est la date de derniere sync de l'autre appareil?
- "Sessions recentes" : y a-t-il des actions en attente sur l'appareil courant?

#### 3b -- Detecter l'appareil courant

```python
import os, socket
device = open('.device').read().strip() if os.path.exists('.device') else socket.gethostname()
```

#### 3c -- Mettre a jour la table Sync

Remplacer la ligne de l'appareil courant :
```
| [device] | YYYY-MM-DD HH:MM | [branche] |
```
Laisser les autres lignes intactes.

#### 3d -- Committer la mise a jour

```bash
git add HANDOFF.md
git commit -m "chore: [device] sync YYYY-MM-DD"
git push origin [branche]
```

Afficher :
```
Handoff :
  Autre appareil : [nom] -- derniere sync [date ou "jamais"]
  Actions en attente ici : [liste items checkbox ou "aucune"]
```

### Si `HANDOFF.md` absent

Signaler : "HANDOFF.md absent -- lancer /session-finalize pour le creer."

---

## Etape 4 -- Checks environnement

### 4a -- Branche git

Depuis `git branch --show-current` (ou `git log` Etape 1) :
- `develop` : OK
- `main` ou `master` : **WARNING** -- tout le travail va sur `develop`, pas directement sur main
- Branche `feature/*` : signaler, normal si travail en cours

### 4b -- Fichiers locaux non commites

Depuis `git status` (Etape 1). Si des fichiers modifies non commites existent :
- Lister les fichiers
- Mentionner : "Travail en cours? Verifier avant de coder."
- Ne pas bloquer.

### 4c -- Hook de protection .env present

Verifier que `.claude/hooks/block-env-edits.py` existe.
Si absent : `WARNING -- hook block-env-edits manquant. Lancer sync-skills.bat pour restaurer.`

### 4d -- Remote control configure

Lire `.claude/settings.json`. Verifier `"remoteControlAtStartup": true`.
**Note : verifie la presence de la config uniquement, pas l'etat runtime.**
Si absent : `WARNING -- remoteControlAtStartup manquant dans .claude/settings.json`

### 4e -- Checks additionnels projet (optionnel)

Lire `CLAUDE.md` a la racine. Si la section suivante existe, executer les checks listes :
```
## Session start -- checks additionnels
```
Si absente : passer silencieusement.

---

## Resume final

```
Session synchronisee -- [PROJECT_NAME] ([device] / [branche])

Git :
  [a jour | N nouveaux commits depuis [autre appareil] | N commits locaux non pushes]

Memoire :
  Phase courante : Phase N -- [description]
  [contrainte ou decision cle]

Handoff :
  [autre appareil] : derniere sync [date ou "jamais"]
  En attente ici   : [actions ou "aucune"]

Checks :
  Branche     : [develop OK | WARNING main | feature/xxx en cours]
  Local dirty : [propre | N fichiers modifies]
  Hook env    : [OK | WARNING block-env-edits manquant]
  Remote ctrl : [config OK | WARNING absent]
  [checks additionnels projet si applicable]
```
