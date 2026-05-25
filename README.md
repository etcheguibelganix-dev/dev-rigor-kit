# dev-rigor-kit

Kit de rigueur de developpement avec Claude Code.
Extrait de CustomsIQ (Phases 1-22), concu pour etre partage entre projets.

**Repo :** `etcheguibelganix-dev/dev-rigor-kit`
**Version :** voir `VERSION`

---

## Ce que ce kit apporte

- **Skill `session-finalize`** : cloture de session automatisee (memoire, docs, commit, push)
- **Skill `auto-compact`** : surveillance du contexte + compactage automatique a ~50%
- **Hook `block-env-edits`** : bloque tout edit Claude sur les fichiers `.env*`
- **Hook `auto-unit-tests`** : lance les tests @unit apres chaque edit de source
- **Hook `sync-plugin-skills`** : synchronise les SKILL.md vers le cache Claude Code
- **Conventions** : branching develop/main, Conventional Commits, tests @unit/@integration/@regression
- **Templates** : CLAUDE.md, .mcp.json, PR GitHub

---

## Structure du repo

```
dev-rigor-kit/
  VERSION                              # Version du kit (ex: 1.0.0)
  CHANGELOG.md                         # Historique des versions
  README.md                            # Ce fichier
  CLAUDE.md.template                   # Template CLAUDE.md a remplir par projet
  .mcp.json.example                    # Template MCP GitHub + PostgreSQL
  .github/
    PULL_REQUEST_TEMPLATE.md           # Template PR
  .claude/
    settings.json                      # Config hooks Claude Code
    hooks/
      block-env-edits.py               # SYNCED -- generique, aucune adaptation
      auto-unit-tests.py               # INSTALL-ONCE -- adapter SOURCE_DIRS et TEST_COMMAND
      sync-plugin-skills.py            # INSTALL-ONCE -- adapter SKILL_CACHE_MAP
    skills/
      session-finalize/
        SKILL.md                       # SYNCED (avec fusion config projet)
      auto-compact/
        SKILL.md                       # SYNCED -- generique cross-platform
  quickstart/
    dobix-quickstart.md                # Guide installation Dobix
    [projet]-quickstart.md             # Ajouter un guide par projet
```

### SYNCED vs INSTALL-ONCE

| Fichier | Comportement | Raison |
|---------|-------------|--------|
| `block-env-edits.py` | **SYNCED** automatiquement | Logique 100% generique |
| `auto-compact/SKILL.md` | **SYNCED** automatiquement | Logique generique, paths dynamiques |
| `session-finalize/SKILL.md` | **SYNCED** avec fusion | Logique generique + config projet preservee |
| `auto-unit-tests.py` | **INSTALL-ONCE** | SOURCE_DIRS specifique au projet |
| `sync-plugin-skills.py` | **INSTALL-ONCE** | SKILL_CACHE_MAP specifique au projet |
| `settings.json` | **INSTALL-ONCE** | Peut avoir des overrides projet |

---

## Mecanisme de sync automatique

A chaque `session-finalize`, l'**Etape 0** :

1. Telecharge les fichiers SYNCED depuis ce repo via MCP GitHub
2. **Groupe A** (remplacement direct) : `block-env-edits.py`, `auto-compact/SKILL.md`
3. **Groupe B** (fusion) : `session-finalize/SKILL.md`
   - Extrait le bloc `<!-- PROJECT_CONFIG_BEGIN -->...<!-- PROJECT_CONFIG_END -->` du fichier local
   - Telecharge la version kit
   - Remplace le bloc config dans la version kit par le bloc local
   - Ecrit le resultat si different
4. Rapporte en une ligne : `Kit v1.0.0 -- a jour` ou `Kit v1.0.0 -- N fichier(s) mis a jour`

**Prerequis :** MCP GitHub configure dans `.mcp.json` du projet.
Si absent, l'Etape 0 est silencieusement ignoree.

---

## Installation sur un nouveau projet

### Etape 1 -- Copier les fichiers

```bash
git clone https://github.com/etcheguibelganix-dev/dev-rigor-kit.git _kit
cp -r _kit/.claude ./
cp -r _kit/.github ./
cp _kit/CLAUDE.md.template ./CLAUDE.md
cp _kit/.mcp.json.example ./.mcp.json.example
rm -rf _kit
```

Ou depuis un autre projet CustomsIQ sur la meme machine (Windows) :
```powershell
$kit = "C:\Users\etche\Documents\GitHub\customsiq-mvp\docs\Technical\dev-rigor-kit"
xcopy /E /I "$kit\.claude" ".claude"
xcopy /E /I "$kit\.github" ".github"
```

### Etape 2 -- Remplir le bloc PROJECT_CONFIG

Dans `.claude/skills/session-finalize/SKILL.md`, remplacer uniquement le bloc entre les delimiteurs :
```
<!-- PROJECT_CONFIG_BEGIN -->
**Projet :** `CHEMIN_ABSOLU_DU_REPO`
**Memoire :** `CHEMIN_MEMOIRE_CLAUDE_CODE`
**DB prod :** `NOM_DB_PROD`
**DB test :** `NOM_DB_TEST`
**Commande tests :** `pytest -m unit -q`
<!-- PROJECT_CONFIG_END -->
```

Ne pas toucher au reste -- il sera maintenu automatiquement par l'Etape 0.

### Etape 3 -- Adapter les hooks projet

- `auto-unit-tests.py` : mettre a jour `SOURCE_DIRS` et `TEST_COMMAND`
- `sync-plugin-skills.py` : ajouter les skills specifiques du projet dans `SKILL_CACHE_MAP`

### Etape 4 -- Remplir CLAUDE.md

Adapter le template avec la stack, les phases, les regles specifiques du projet.
Si le projet a des docs specifiques a mettre a jour en fin de session, ajouter :

```markdown
## Session finalize -- hook projet

Skill projet : `session-finalize-[projet]`
```

Et creer `.claude/skills/session-finalize-[projet]/SKILL.md` avec les etapes specifiques.

### Etape 5 -- Configurer MCP GitHub

Copier `.mcp.json.example` en `.mcp.json` et remplir le PAT GitHub.
Ajouter `.mcp.json` au `.gitignore`.

### Etape 6 -- Sync initial vers le cache Claude Code

```powershell
# Windows -- a adapter selon l'OS
foreach ($skill in @("session-finalize", "auto-compact")) {
    $src = ".claude\skills\$skill\SKILL.md"
    $dst = "$env:APPDATA\..\Local\.claude\plugins\cache\local\$skill\unknown\skills\$skill\SKILL.md"
    New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    Copy-Item $src $dst
    Write-Host "Sync OK: $skill"
}
```

### Etape 7 -- Creer les branches develop et main

```bash
git checkout -b develop
git push origin develop
```

---

## Architecture session-finalize (core + sous-skill)

```
session-finalize (CORE -- ce repo)
  Etape 0 : sync kit depuis GitHub
  Etapes 1-3 : snapshot, memoire, rapport tests
  Etape 4 : lit CLAUDE.md -> invoque le sous-skill projet si declare
      |
      v
  session-finalize-[projet] (SOUS-SKILL -- cree par le projet)
      Steps A-Z : mise a jour docs specifiques (HTML, MD, etc.)
      Pas de commit, pas de push -- retourne au core
  Etapes 5-7 : CLAUDE.md, commit docs, push develop
```

---

## Quickstarts disponibles

| Projet | Guide |
|--------|-------|
| Dobix | `quickstart/dobix-quickstart.md` |

Pour ajouter un guide pour un nouveau projet : copier `dobix-quickstart.md`, adapter les valeurs.

---

## Contribuer / Mettre a jour le kit

Pour ameliorer le kit (correction dans session-finalize, nouvelle convention, etc.) :
1. Editer directement sur `main` de ce repo (ou via PR si modification majeure)
2. Bumper la version dans `VERSION` et documenter dans `CHANGELOG.md`
3. Tous les projets recevront la mise a jour a leur prochaine `session-finalize`
