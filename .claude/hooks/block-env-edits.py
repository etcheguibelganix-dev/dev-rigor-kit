"""
Hook PreToolUse -- Blocage des fichiers .env
Bloque toute tentative de Write/Edit sur un fichier .env* (sauf .env*.example).
Generique -- aucune adaptation necessaire.

Protocole Claude Code hooks :
  - Lit le JSON de l'appel outil depuis stdin
  - Exit 0 = autoriser
  - Exit 1 + message sur stdout = bloquer avec message
"""
import json
import sys

try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    # Normaliser les separateurs
    file_path = file_path.replace("\\", "/")

    is_env_file = ".env" in file_path.split("/")[-1]
    is_example  = file_path.endswith(".example")

    if is_env_file and not is_example:
        print(
            f"BLOQUE : {file_path} est un fichier .env sensible.\n"
            "Les fichiers .env ne doivent jamais etre modifies par Claude.\n"
            "Modifie manuellement si necessaire, puis verifie qu'il n'est pas dans git status."
        )
        sys.exit(1)

except Exception:
    # En cas d'erreur de parsing, laisser passer (ne pas bloquer par erreur)
    pass

sys.exit(0)
