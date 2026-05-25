"""
Hook PostToolUse -- Auto-run tests @unit apres edition de fichiers Python source.

ADAPTER pour le projet cible :
  - SOURCE_DIRS : dossiers contenant les fichiers source a surveiller
  - SKIP_PATTERNS : dossiers a exclure du declenchement
  - TEST_COMMAND : commande pytest a lancer

Declenche les tests uniquement si le fichier modifie appartient a un module
source cle. Ne se declenche PAS sur les fichiers de test, docs, ou scripts.

Exit code non-zero = warning (pas de blocage, hook en mode "warn").
"""
import json
import subprocess
import sys

# ============================================================
# ADAPTER CES VALEURS POUR LE PROJET CIBLE
# ============================================================

# Dossiers source a surveiller (toute edition dans ces dossiers declenche les tests)
SOURCE_DIRS = (
    "api/",
    "core/",
    "services/",
    # Ajouter les dossiers source du projet ici
)

# Dossiers a exclure (meme si dans SOURCE_DIRS par transitivite)
SKIP_PATTERNS = (
    "tests/",
    "docs/",
    "front/",
    "scripts/",
    ".claude/",
    "__pycache__",
)

# Commande de test a lancer (modifier selon le projet)
TEST_COMMAND = ["python", "-m", "pytest", "-m", "unit", "-q", "--tb=line", "--no-header"]

# ============================================================


def should_run(file_path: str) -> bool:
    path = file_path.replace("\\", "/")
    if not path.endswith(".py"):
        return False
    if any(skip in path for skip in SKIP_PATTERNS):
        return False
    return any(src in path for src in SOURCE_DIRS)


try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")

    if should_run(file_path):
        print(f"[auto-test] Edition detectee : {file_path}")
        print(f"[auto-test] Lancement : {' '.join(TEST_COMMAND)} ...")
        result = subprocess.run(TEST_COMMAND, capture_output=False)
        if result.returncode != 0:
            print("[auto-test] Des tests sont en echec -- verifier avant de continuer.")
            sys.exit(1)

except Exception as e:
    print(f"[auto-test] Erreur hook : {e}")

sys.exit(0)
