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
| `{{SOURCE_DIRS}}` | `"api/", "core/", "services/"` (a ajuster selon structure reelle) |
| `{{TEST_COMMAND}}` | `pytest -m unit -q --tb=line --no-header` (ou equivalent stack Dobix) |
| `{{PROD_DB}}` | Nom de la DB prod Dobix |
| `{{TEST_DB}}` | Nom de la DB test Dobix |
| `{{DATE}}` | Date du jour |

---

## Installation pas-a-pas

### 1. Depuis la racine du repo Dobix

```powershell
# PowerShell -- depuis la racine du repo Dobix
$kit = "C:\Users\etche\Documents\GitHub\customsiq-mvp\docs\Technical\dev-rigor-kit"

# Copier les dossiers .claude et .github
xcopy /E /I "$kit\.claude" ".claude"
xcopy /E /I "$kit\.github" ".github"
copy "$kit\CLAUDE.md.template" "CLAUDE.md"
copy "$kit\.mcp.json.example" ".mcp.json.example"
```

Ou, si tu utilises directement le repo GitHub :
```bash
git clone https://github.com/etcheguibelganix-dev/dev-rigor-kit.git _kit
cp -r _kit/.claude ./
cp -r _kit/.github ./
cp _kit/CLAUDE.md.template ./CLAUDE.md
cp _kit/.mcp.json.example ./.mcp.json.example
rm -rf _kit
```

### 2. Adapter session-finalize/SKILL.md (bloc PROJECT_CONFIG)

Ouvrir `.claude/skills/session-finalize/SKILL.md`.
Remplacer UNIQUEMENT le bloc entre `<!-- PROJECT_CONFIG_BEGIN -->` et `<!-- PROJECT_CONFIG_END -->` :

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

Ouvrir `.claude/hooks/auto-unit-tests.py` et mettre a jour :
```python
SOURCE_DIRS = (
    "api/",        # adapter aux dossiers source Dobix reels
    "core/",
    # ...
)
TEST_COMMAND = ["python", "-m", "pytest", "-m", "unit", "-q", "--tb=line", "--no-header"]
```

### 4. Adapter sync-plugin-skills.py

Si Dobix a un sous-skill projet specifique (ex: `session-finalize-dobix`), ajouter a `SKILL_CACHE_MAP` :
```python
SKILL_CACHE_MAP = {
    "session-finalize": os.path.join(_CACHE_BASE, "session-finalize", ...),
    "auto-compact": os.path.join(_CACHE_BASE, "auto-compact", ...),
    "session-finalize-dobix": os.path.join(_CACHE_BASE, "session-finalize-dobix", ...),  # si applicable
}
```

### 5. Remplir CLAUDE.md

Adapter `CLAUDE.md` avec la stack reelle Dobix (Docker, ports, dependances, etc.).
S'assurer que la section "Session finalize -- hook projet" est presente si Dobix a des docs specifiques :

```markdown
## Session finalize -- hook projet

Skill projet : `session-finalize-dobix`
```

Ou la supprimer si Dobix n'a pas de sous-skill specifique.

### 6. Ajouter au .gitignore

```
.mcp.json
tests/.env.test
lib/
```

### 7. Creer la structure memoire

Dans le projet Claude Code Dobix, creer :
```
memory/
  project_dobix.md    # Contexte projet (description, stack, phases)
  MEMORY.md           # Index pointant vers project_dobix.md
```

### 8. Configurer MCP GitHub

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

### 9. Synchroniser le skill session-finalize vers le cache

```powershell
# PowerShell
$src = ".claude\skills\session-finalize\SKILL.md"
$dst = "$env:APPDATA\..\Local\.claude\plugins\cache\local\session-finalize\unknown\skills\session-finalize\SKILL.md"
New-Item -ItemType Directory -Force -Path (Split-Path $dst)
Copy-Item $src $dst
Write-Host "Sync OK"
```

Idem pour auto-compact :
```powershell
$src = ".claude\skills\auto-compact\SKILL.md"
$dst = "$env:APPDATA\..\Local\.claude\plugins\cache\local\auto-compact\unknown\skills\auto-compact\SKILL.md"
New-Item -ItemType Directory -Force -Path (Split-Path $dst)
Copy-Item $src $dst
```

### 10. Creer les branches develop et main sur GitHub

```bash
git checkout -b develop
git push origin develop
# main est la branche par defaut sur GitHub
```

### 11. Verifier les hooks dans Claude Code

Au prochain demarrage Claude Code sur Dobix, verifier que :
- L'edition d'un fichier `.env` est bloquee
- L'edition d'un fichier source `.py` declenche les tests
- `session-finalize` pousse sur `develop` (pas `main`)
- Etape 0 de `session-finalize` se connecte au repo `dev-rigor-kit` et rapporte "Kit v1.0.0 -- a jour"

---

## Ce qui sera maintenu automatiquement

Une fois installe, a chaque `session-finalize` :

| Fichier | Comportement |
|---------|-------------|
| `.claude/hooks/block-env-edits.py` | Mis a jour depuis le kit si change |
| `.claude/skills/auto-compact/SKILL.md` | Mis a jour depuis le kit si change |
| `.claude/skills/session-finalize/SKILL.md` | Logique mise a jour, config Dobix preservee |

| Fichier | Comportement |
|---------|-------------|
| `.claude/hooks/auto-unit-tests.py` | **Non sync** -- specifique Dobix (SOURCE_DIRS) |
| `.claude/hooks/sync-plugin-skills.py` | **Non sync** -- specifique Dobix (SKILL_CACHE_MAP) |
| `.claude/skills/session-finalize-dobix/SKILL.md` | **Non sync** -- sous-skill projet Dobix |

---

## Points d'attention specifiques Dobix

D'apres la memoire CustomsIQ sur Dobix :
- Stack : Docker, Tailscale, scripts, roadmap phases 1-6
- Repo GitHub prive
- Migration serveur en cours

Verifier avant installation :
- [ ] Python disponible dans le PATH (`python --version`)
- [ ] pytest installe dans le venv Dobix
- [ ] Docker Desktop en route pour les tests d'integration
- [ ] Structure de dossiers source a confirmer pour `auto-unit-tests.py`
