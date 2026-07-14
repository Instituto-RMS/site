"""Stub de compatibilidade: delega para o pacote scripts.sync_notion.

Mantem o comando historico funcionando:
    source .env && python scripts/sync_notion.py

Preferimos chamar via modulo para usar o package:
    python -m scripts.sync_notion
mas este arquivo garantia que scripts antigos e docs nao quebrem.
"""

import sys
from pathlib import Path

# Garante que o diretorio raiz do repo esteja no sys.path para que
# `scripts.sync_notion` seja importavel quando executado como script solto.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.sync_notion.__main__ import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())