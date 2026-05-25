---
name: session-finalize
description: >
  Finalise proprement une session de developpement {{PROJECT_NAME}}. Declenche sur : "Finalise la session",
  "cloture la session", "termine la session", "mets a jour les docs et pousse", "commits et push la session",
  ou toute formulation indiquant que l'utilisateur veut clore une session de travail sur {{PROJECT_NAME}}
  (memoire + docs + git push). Si le contexte est ambigu, demande confirmation avant de declencher.
  NE PAS declencher pour des demandes ponctuelles de commit seul, push seul, ou mise a jour d'un seul fichier.

  Ce skill automatise la sequence complete : sync kit -> snapshot git -> mise a jour memoire -> rapport de run
  -> hook projet (docs specifiques) -> CLAUDE.md -> commit docs -> push origin/develop.
  Generique -- specificites projet deleguees au skill declare dans CLAUDE.md (section "Session finalize -- hook projet").
---

# Session Finalize -- CORE (generique)

Sequence de cloture de session. Execute les etapes dans l'ordre.
Si une information manque, demande a l'utilisateur plutot qu'inventer.

<!-- PROJECT_CONFIG_BEGIN -->
**Projet :** `{{PROJECT_PATH}}`
**Memoire :** `{{MEMORY_PATH}}`
**DB prod :** `{{PROD_DB}}` -- ne jamais toucher pendant les tests
**DB test :** `{{TEST_DB}}` -- utilisee par la suite de tests
**Commande tests :** `{{TEST_COMMAND}}`
<!-- PROJECT_CONFIG_END -->

---

## Regles absolues (verifier avant chaque action)

- Ne jamais modifier ni supprimer de sections historiques -- **ajouter seulement**
- Ne jamais committer `tests/.env.test` ni aucun fichier `.env*`
- Ne jamais toucher la **DB prod** (voir PROJECT_CONFIG ci-dessus) -- les tests utilisent la DB test
- Toujours pousser sur `develop`, jamais sur `main` directement
- Si une information cle manque (phase, nombre de tests, decisions) : **demander a l'utilisateur**

---

## Etape 0 -- Sync depuis dev-rigor-kit

Mettre a jour les fichiers generiques locaux depuis le kit avant de commencer.

**Kit :** `etcheguibelganix-dev/dev-rigor-kit` (GitHub public)
**Prerequis :** MCP GitHub dans `.mcp.json`. Si absent : afficher `Sync kit ignore` et passer a l'Etape 1.

### Fichiers synchronises

**Groupe A -- remplacement direct (contenu 100% generique) :**

| Fichier dans le kit | Fichier local |
|---|---|
| `.claude/hooks/block-env-edits.py` | `.claude/hooks/block-env-edits.py` |
| `.claude/skills/auto-compact/SKILL.md` | `.claude/skills/auto-compact/SKILL.md` |

Pour chaque fichier du Groupe A :
1. Telecharger : `mcp__github__get_file_contents(owner="etcheguibelganix-dev", repo="dev-rigor-kit", path="<chemin>")`
2. Lire la version locale (Read tool)
3. Si contenu different : ecrire (Write tool). Pour SKILL.md : copier aussi vers le cache Claude Code.
4. Si identique : continuer silencieusement.

**Groupe B -- fusion (preserve la config projet) :**

| Fichier dans le kit | Fichier local |
|---|---|
| `.claude/skills/session-finalize/SKILL.md` | `.claude/skills/session-finalize/SKILL.md` (ce fichier) |

Pour le Groupe B :
1. Lire le fichier local. Extraire le bloc entre `<!-- PROJECT_CONFIG_BEGIN -->` et `<!-- PROJECT_CONFIG_END -->` (les deux lignes de commentaire incluses). Appeler ce bloc `LOCAL_CONFIG`.
2. Telecharger le fichier kit : `mcp__github__get_file_contents(owner="etcheguibelganix-dev", repo="dev-rigor-kit", path=".claude/skills/session-finalize/SKILL.md")`
3. Dans le contenu kit, remplacer le bloc `<!-- PROJECT_CONFIG_BEGIN -->...<!-- PROJECT_CONFIG_END -->` par `LOCAL_CONFIG`.
4. Si le resultat differe de la version locale actuelle : ecrire (Write). Copier aussi vers le cache.
5. Si identique : continuer silencieusement.

Lire aussi `VERSION` depuis le kit : `mcp__github__get_file_contents(owner="etcheguibelganix-dev", repo="dev-rigor-kit", path="VERSION")`

### Affichage du resultat

| Cas | Affichage |
|-----|-----------|
| 0 changement | `Kit v[VERSION] -- a jour` |
| N changements | `Kit v[VERSION] -- N fichier(s) mis a jour : [liste]. Hooks actifs immediatement. Core actif a la prochaine invocation.` |
| MCP absent / erreur | `Sync kit ignore (MCP GitHub indisponible)` |

**Ne jamais bloquer** la suite en cas d'erreur de sync.

---

## Etape 1 -- Snapshot de la session

```bash
git log --oneline origin/develop..HEAD
git log --oneline -8
git status
git diff --name-only origin/develop..HEAD
```

Extraire et memoriser :
- **Phase courante** : depuis les messages de commit (`feat(phase8):`, `fix(phase8):`, etc.)
- **Nombre de tests** : depuis le dernier rapport dans `docs/Tests/test-reports/` ou demander
- **Nouveaux fichiers / endpoints / decisions** : synthese commits + diff
- **Flags conditionnels** : front modifie ? Decision produit prise ?

Si phase ou nombre de tests incertains : demander confirmation avant de continuer.

---

## Etape 2 -- Mise a jour memoire

### `memory/project_{{PROJECT_NAME_LOWER}}.md`

Mettre a jour sans supprimer l'historique :

1. **En-tete** : date du jour + resume de la phase livree
2. **Tableau des phases** (`## Etat des phases`) : ajouter la ligne Phase N si absente
3. **Section decisions cles Phase N** : decisions techniques importantes
4. **Compteurs** : mettre a jour "Total", "@unit", "@integration+regression"

### `memory/MEMORY.md` (index)

- Modifier "phases 1->N-1" en "phases 1->N"
- Actualiser le resume si fonctionnalites notables ajoutees

---

## Etape 3 -- Rapport de run

Creer `docs/Tests/test-reports/run-YYYY-MM-DD.md` (date du jour).
Si le fichier existe deja pour aujourd'hui : demander a l'utilisateur avant d'ecraser.

```markdown
# {{PROJECT_NAME}} -- Rapport de run tests -- YYYY-MM-DD

## Resume
| Metrique | Valeur |
|---------|--------|
| Date | YYYY-MM-DD |
| Phase | Phase N -- [description courte] |
| Total tests | **TOTAL** |
| PASS | **TOTAL** |
| FAIL | **0** |

## Commande
```bash
{{TEST_COMMAND}}
```

## Nouveaux tests Phase N
[Table : Test | Resultat]

## Changements livres
[Description technique]

## Decisions techniques Phase N
[Table : Decision | Valeur | Raison]
```

---

## Etape 4 -- Hook projet (docs specifiques)

Lire `CLAUDE.md` a la racine du projet. Chercher :

```
## Session finalize -- hook projet
Skill projet : `<nom-du-skill>`
```

**Si present :** invoquer `Skill(skill="<nom-du-skill>")`.
Ce skill gere les docs specifiques au projet. Il ne fait PAS de commit.
Attendre la fin avant de continuer.

**Si absent :** passer directement a l'Etape 4.5.

---

## Etape 4.5 -- Rappel audit CLAUDE.md

`/claude-md-improver` ne peut pas etre invoque automatiquement.
Rappel affiche dans le resume final.

---

## Etape 5 -- CLAUDE.md

Modifier sans supprimer l'historique :

1. **Ligne `> Derniere mise a jour`** : nouvelle date + resume de la phase
2. **Section `Etat des phases`** : ajouter Phase N si absente
3. **Section `Suite de tests`** : mettre a jour total, @unit, @integration, @regression
4. **Section `Phase N -- Fichiers implements / modifies`** : ajouter apres les autres phases

---

## Etape 6 -- Commit docs

Verifier qu'aucun fichier sensible n'est inclus :
```bash
git status   # verifier absence de .env*
```

Si un `.env*` apparait : ne pas committer, alerter l'utilisateur.

```bash
git add CLAUDE.md \
        "docs/Tests/test-reports/run-YYYY-MM-DD.md" \
        [tous les fichiers docs modifies par le hook projet -- d'apres git status]
```

Message de commit :
```
docs: Phase N - [resume en une ligne]

- CLAUDE.md : Phase N ajoutee, tests TOTAL/TOTAL
- docs/Tests/test-reports/run-YYYY-MM-DD.md : rapport Phase N
[- lignes pour chaque fichier modifie par le hook projet]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## Etape 6.5 -- Code review avant PR (optionnel)

```bash
git diff --name-only origin/develop..HEAD | grep -vE "^(docs/|\.claude/)"
```

Criteres (1 point chacun) :
- Plus de 3 fichiers source modifies
- Au moins un fichier API touche
- Au moins un fichier SQL de migration ajoute
- Un nouveau module cree
- Des fichiers de tests d'integration ou regression modifies

**Score >= 2 -> review recommandee.** Afficher et attendre "ok" / "skip".

---

## Etape 7 -- Push origin/develop

Convention : toujours `develop`, jamais `main`.
`main` = stable/production, alimente uniquement via PR `develop` -> `main`.

```bash
git push origin develop
```

En cas d'erreur : rapporter, ne pas forcer.

```bash
git log --oneline origin/develop~6..origin/develop
```

---

## Resume final

```
Session Phase N finalisee -- origin/develop a jour

Commits pousses :
  [liste des SHAs + messages]

Docs mis a jour :
  - memory/project_{{PROJECT_NAME_LOWER}}.md + MEMORY.md
  - docs/Tests/test-reports/run-YYYY-MM-DD.md     (cree)
  - CLAUDE.md                                      (Phase N + tests TOTAL/TOTAL)
  [docs specifiques mis a jour par le hook projet]

Total tests : TOTAL/TOTAL PASS | Phase N | YYYY-MM-DD

----------------------------------------------
Actions manuelles recommandees :

  /claude-md-improver   -> audite CLAUDE.md contre le codebase reel
  PR develop -> main    -> si la phase est prete pour production
----------------------------------------------
```
