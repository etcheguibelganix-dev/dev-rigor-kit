"""
Hook PostToolUse -- Sync automatique des skills repo vers le cache Claude Code.

Declenche uniquement si le fichier modifie est un SKILL.md dans .claude/skills/.
Copie silencieuse vers le cache correspondant.

ADAPTER : mettre a jour SKILL_CACHE_MAP si vous ajoutez des skills locaux.

Mapping repo -> cache (Windows) :
  .claude/skills/session-finalize/SKILL.md
    -> %APPDATA%\..\Local\.claude\plugins\cache\local\session-finalize\unknown\skills\session-finalize\SKILL.md
  .claude/skills/auto-compact/SKILL.md
    -> %APPDATA%\..\Local\.claude\plugins\cache\local\auto-compact\unknown\skills\auto-compact\SKILL.md

Exit code non-zero = warning (pas de blocage).
"""
import json
import os
import shutil
import sys

# Chemin de base du cache Claude Code
_HOME = os.path.expanduser("~")
_CACHE_BASE = os.path.join(_HOME, ".claude", "plugins", "cache", "local")

# Mapping : nom du skill -> chemin complet dans le cache
# ADAPTER si vous ajoutez des skills locaux supplementaires
SKILL_CACHE_MAP = {
    "session-finalize": os.path.join(
        _CACHE_BASE, "session-finalize", "unknown", "skills", "session-finalize", "SKILL.md"
    ),
    "auto-compact": os.path.join(
        _CACHE_BASE, "auto-compact", "unknown", "skills", "auto-compact", "SKILL.md"
    ),
}


def get_skill_name(file_path: str):
    """Retourne le nom du skill si le fichier est un SKILL.md versionne, None sinon."""
    path = file_path.replace("\\", "/")
    if ".claude/skills/" not in path or not path.endswith("/SKILL.md"):
        return None
    parts = path.split(".claude/skills/")
    if len(parts) < 2:
        return None
    skill_name = parts[1].split("/")[0]
    return skill_name if skill_name in SKILL_CACHE_MAP else None


try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    skill_name = get_skill_name(file_path)
    if skill_name:
        dst = SKILL_CACHE_MAP[skill_name]
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(file_path, dst)
        print(f"[sync-skills] {skill_name} -> cache mis a jour")

except Exception as e:
    print(f"[sync-skills] Erreur sync : {e}")
    sys.exit(1)

sys.exit(0)
