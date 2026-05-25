# Changelog -- dev-rigor-kit

## v1.0.0 -- 2026-05-25

Premiere release publique. Extrait de CustomsIQ (Phases 1-22).

### Contenu

- `session-finalize` : skill CORE generique (Etapes 0-7)
  - **Etape 0** : sync automatique depuis ce repo avant chaque finalisation de session
  - Etape 4 : hook projet (sous-skill specifique declare dans CLAUDE.md)
  - Etape 7 : push toujours sur `develop` (jamais `main`)
- `auto-compact` : skill de surveillance du contexte (cross-platform, paths dynamiques via expanduser)
- `block-env-edits.py` : hook PreToolUse qui bloque tout edit `.env*` non `.example`
- `auto-unit-tests.py` : hook PostToolUse qui lance les tests @unit (a adapter par projet)
- `sync-plugin-skills.py` : hook PostToolUse qui sync les SKILL.md vers le cache Claude Code (a adapter)
- `CLAUDE.md.template` : template a remplir par projet (placeholders {{PROJECT_NAME}}, etc.)
- `.claude/settings.json` : config hooks Claude Code
- `.mcp.json.example` : template config MCP GitHub + PostgreSQL
- `.github/PULL_REQUEST_TEMPLATE.md` : template PR
- `quickstart/dobix-quickstart.md` : guide d'installation Dobix (premier projet cible)

### Conventions incluses

- Branching : develop/main, PR obligatoire pour main
- Commit messages : Conventional Commits (feat/fix/docs/chore/refactor/test)
- Tests : @unit / @integration / @regression
- Securite : jamais de .env* committe, .mcp.json gitignored

### Architecture session-finalize (core + sous-skill)

Le CORE (ce repo) gere la sequence generique.
Les docs specifiques au projet sont delegues a un sous-skill declare dans CLAUDE.md du projet :

```
## Session finalize -- hook projet
Skill projet : `session-finalize-[projet]`
```

Ce sous-skill est cree par chaque projet -- pas versionne dans ce repo.

### Mecanisme de sync automatique (Etape 0)

A chaque `session-finalize`, Etape 0 :
1. Telecharge les fichiers generiques depuis ce repo via MCP GitHub
2. Remplace directement `block-env-edits.py` et `auto-compact/SKILL.md` si changes
3. Fusionne `session-finalize/SKILL.md` en preservant le bloc PROJECT_CONFIG du projet
4. Rapporte les mises a jour ou confirme que tout est a jour
