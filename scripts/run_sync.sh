#!/usr/bin/env bash
# Facilitador para rodar o sync Notion -> Zola.
#
# Uso:
#   ./scripts/run_sync.sh                            # sync completo
#   ./scripts/run_sync.sh --page <slug>               # sync de uma pagina so
#   ./scripts/run_sync.sh --page-id <notion-page-id> # sync por id do Notion
#
# Cria o .venv automaticamente na primeira execucao e instala as dependencias
# listadas em scripts/requirements.txt. Carrega variaveis do .env se existir.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Cria o venv se ainda nao existir.
if [ ! -d "$ROOT/.venv" ]; then
    echo ">> Criando .venv ..."
    python3 -m venv "$ROOT/.venv"
fi

# Ativa e instala dependencias (silencioso, so instala se faltar algo).
source "$ROOT/.venv/bin/activate"
pip install -q --disable-pip-version-check -r "$ROOT/scripts/requirements.txt"

# Carrega .env se existir (exporta as variaveis para o processo filho).
if [ -f "$ROOT/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$ROOT/.env"
    set +a
fi

python -m scripts.sync_notion "$@"