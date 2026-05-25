# Dobix -- Quickstart installation du dev-rigor-kit

Guide specifique Dobix. Remplace tous les placeholders {{...}} avec les valeurs ci-dessous.

---

## Table de remplacement des placeholders

| Placeholder | Valeur Dobix |
|-------------|-------------|
| `{{PROJECT_NAME}}` | `Dobix` |
| `{{PROJECT_NAME_LOWER}}` | `dobix` |
| `{{PROJECT_PATH}}` | `C:\Users\etche\Documents\GitHub\dobix` |
| `{{MEMORY_PATH}}` | `C:\Users\etche\.claude\projects\C--Users-etche-Documents-GitHub-dobix\memory\` |
| `{{SOURCE_DIRS}}` | `()` -- vide jusqu'a Phase 7 (pas de tests automatises avant) |
| `{{TEST_COMMAND}}` | N/A jusqu'a Phase 7 -- validation manuelle par phase |
| `{{PROD_DB}}` | N/A -- Dobix n'a pas de DB relationnelle (phases 1-6) |
| `{{TEST_DB}}` | N/A -- idem |
| `{{DATE}}` | Date du jour |

---

## Installation pas-a-pas

### 1. Depuis la racine du repo Dobix

Cloner le kit depuis GitHub et copier les fichiers necessaires :

```bash
# bash (Git Bash ou WSL)
git clone https://github.com/etcheguibelganix-dev/dev-rigor-kit.git _kit
cp -r _kit/.claude ./
cp _kit/CLAUDE.md.template ./CLAUDE.md
cp _kit/.mcp.json.example ./.mcp.json.example
rm -rf _kit
```

Ou en PowerShell :
```powershell
git clone https://github.com/etcheguibelganix-dev/dev-rigor-kit.git _kit
xcopy /E /I "_kit\.claude" ".claude"
copy "_kit\CLAUDE.md.template" "CLAUDE.md"
copy "_kit\.mcp.json.example" ".mcp.json.example"
Remove-Item -Recurse -Force _kit
```

> Note : ne pas pointer vers un autre projet local (ex: customsiq-mvp) -- toujours cloner depuis GitHub pour garantir la version a jour.

### 2. Adapter session-finalize/SKILL.md (bloc PROJECT_CONFIG)

Ouvrir `.claude/skills/session-finalize/SKILL.md`.
Remplacer UNIQUEMENT le bloc entre `<!-- PROJECT_CONFIG_BEGIN -->` et `<!-- PROJECT_CONFIG_END -->` :

**Si le projet n'a pas de DB (comme Dobix phases 1-6) :**
```markdown
<!-- PROJECT_CONFIG_BEGIN -->
**Projet :** `C:\Users\etche\Documents\GitHub\dobix`
**Memoire :** `C:\Users\etche\.claude\projects\C--Users-etche-Documents-GitHub-dobix\memory\`
**Tests :** aucun automatise (phases 1-6 manuels) -- Etape 3 : noter l'etat des phases seulement, pas de rapport de tests ni compteur
<!-- PROJECT_CONFIG_END -->
```

**Si le projet a une DB (convention a activer quand Dobix aura une DB) :**
```markdown
<!-- PROJECT_CONFIG_BEGIN -->
**Projet :** `C:\Users\etche\Documents\GitHub\dobix`
**Memoire :** `C:\Users\etche\.claude\projects\C--Users-etche-Documents-GitHub-dobix\memory\`
**DB prod :** `dobix` -- ne jamais toucher pendant les tests
**DB test :** `dobix_test` -- utilisee par la suite de tests
**Commande tests :** `pytest -m unit -q --tb=line --no-header`
<!-- PROJECT_CONFIG_END -->
```

Ne pas modifier le reste du fichier -- il sera mis a jour automatiquement par l'Etape 0.

### 3. Adapter auto-unit-tests.py

Ouvrir `.claude/hooks/auto-unit-tests.py` et mettre a jour `SOURCE_DIRS`.

**Si le projet n'a pas de tests automatises (comme Dobix phases 1-6) :**
```python
SOURCE_DIRS = ()  # Hook dormant -- activer quand les tests automatises existent
```
Le hook s'activera silencieusement sans rien lancer. Revenir ici et configurer les dossiers reels quand les tests arrivent (ex: Phase 7).

**Si le projet a des tests automatises :**
```python
SOURCE_DIRS = (
    "api/",        # adapter aux dossiers source reels
    "core/",
    # ...
)
TEST_COMMAND = ["python", "-m", "pytest", "-m", "unit", "-q", "--tb=line", "--no-header"]
```

### 4. Adapter sync-plugin-skills.py

Si le projet a un sous-skill specifique (ex: `session-finalize-dobix`), ajouter a `SKILL_CACHE_MAP` :
```python
SKILL_CACHE_MAP = {
    "session-finalize": os.path.join(_CACHE_BASE, "session-finalize", "unknown", "skills", "session-finalize", "SKILL.md"),
    "auto-compact": os.path.join(_CACHE_BASE, "auto-compact", "unknown", "skills", "auto-compact", "SKILL.md"),
    "session-finalize-dobix": os.path.join(_CACHE_BASE, "session-finalize-dobix", "unknown", "skills", "session-finalize-dobix", "SKILL.md"),
}
```

### 5. Remplir CLAUDE.md

Adapter `CLAUDE.md` avec la stack reelle Dobix (Docker, ports, dependances, etc.).

Si le projet a des docs specifiques a maintenir en session (comme Dobix), creer le sous-skill projet et declarer le hook dans CLAUDE.md :

```markdown
## Session finalize -- hook projet

Skill projet : `session-finalize-dobix`
```

Si aucun sous-skill projet n'est necessaire, omettre cette section.

### 6. Creer le sous-skill projet (si applicable)

Pour Dobix, le sous-skill `session-finalize-dobix` couvre :
- `docs/Product/dobix-capabilities.md` -- features delivrees par phase
- `docs/Product/dobix-roadmap-decisions.md` -- decisions datees
- `docs/Sessions/session-reports/session-YYYY-MM-DD.md` -- rapport session
- `docs/Technical/dobix-technical-ref.html` -- conditonnel si infra modifiee

Creer `.claude/skills/session-finalize-dobix/SKILL.md` base sur les docs reelles du projet.
Puis ajouter une entree dans `sync-plugin-skills.py` (cf. etape 4) et syncer manuellement :

```python
python -c "
import os, shutil
HOME = os.path.expanduser('~')
src = '.claude/skills/session-finalize-dobix/SKILL.md'
dst = os.path.join(HOME, '.claude', 'plugins', 'cache', 'local', 'session-finalize-dobix', 'unknown', 'skills', 'session-finalize-dobix', 'SKILL.md')
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.copy2(src, dst)
print('Sync OK ->', dst)
"
```

### 7. Ajouter au .gitignore

```
.mcp.json
tests/.env.test
lib/
```

### 8. Creer la structure memoire

Dans le projet Claude Code Dobix, creer :
```
memory/
  project_dobix.md    # Contexte projet (description, stack, phases)
  MEMORY.md           # Index pointant vers project_dobix.md
```

### 9. Configurer MCP GitHub

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_ton_token_ici"
      }
    }
  }
}
```

Ajouter `.mcp.json` au `.gitignore`.

### 10. Synchroniser les skills vers le cache

```python
python -c "
import os, shutil
HOME = os.path.expanduser('~')
skills = ['session-finalize', 'auto-compact']
for s in skills:
    src = f'.claude/skills/{s}/SKILL.md'
    dst = os.path.join(HOME, '.claude', 'plugins', 'cache', 'local', s, 'unknown', 'skills', s, 'SKILL.md')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'Sync OK : {s}')
"
```

Faire de meme pour le sous-skill projet si applicable (cf. etape 6).

### 11. Creer les branches develop et main sur GitHub

```bash
git checkout -b develop
git push origin develop
# main est la branche par defaut sur GitHub
```

### 12. Verifier les hooks dans Claude Code

Au prochain demarrage Claude Code sur Dobix, verifier que :
- L'edition d'un fichier `.env` est bloquee
- L'edition d'un fichier source `.py` declenche les tests (ou que le hook est silencieux si SOURCE_DIRS vide)
- `session-finalize` pousse sur `develop` (pas `main`)
- Etape 0 de `session-finalize` se connecte au repo `dev-rigor-kit` et rapporte "Kit v1.0.0 -- a jour"

---

## Ce qui sera maintenu automatiquement

Une fois installe, a chaque `session-finalize` :

| Fichier | Comportement |
|---------|-------------|
| `.claude/hooks/block-env-edits.py` | Mis a jour depuis le kit si change |
| `.claude/skills/auto-compact/SKILL.md` | Mis a jour depuis le kit si change |
| `.claude/skills/session-finalize/SKILL.md` | Logique mise a jour, config projet preservee |

| Fichier | Comportement |
|---------|-------------|
| `.claude/hooks/auto-unit-tests.py` | **Non sync** -- specifique projet (SOURCE_DIRS) |
| `.claude/hooks/sync-plugin-skills.py` | **Non sync** -- specifique projet (SKILL_CACHE_MAP) |
| `.claude/skills/session-finalize-dobix/SKILL.md` | **Non sync** -- sous-skill projet |

---

## Points d'attention specifiques Dobix

Etat actuel Dobix (2026-05-25) :
- Phases 1-5 terminees (Stack, Gmail, Repo app client, Agent fichiers PC fixe, Agent fichiers laptop)
- Phase 5 laptop : cloner repo + executer install.bat sur le laptop
- Sous-skill `session-finalize-dobix` installe et configure
- Pas de tests automatises avant Phase 7 (validation manuelle par phase)
- Pas de DB relationnelle dans la stack Dobix (phases 1-6) -- convention DB a activer si DB ajoutee

Verifier avant installation :
- [ ] Python disponible dans le PATH (`python --version`)
- [ ] Git configure (`git config user.name`)
- [ ] Docker Desktop accessible (pour lancer la stack)
- [ ] Tailscale connecte (pour les tests d'acces distant)
- [ ] SOURCE_DIRS laisse vide jusqu'a Phase 7 (pas de tests automatises)
