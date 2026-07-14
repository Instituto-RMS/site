#!/usr/bin/env bash
# Builda o site localmente.
#
# Uso:
#   ./scripts/build.sh
#
# O script faz:
#   1. Tailwind build (bun run build)
#   2. Zola build

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

# Verifica dependências
command -v zola >/dev/null 2>&1 || { echo "Erro: zola não encontrado no PATH"; exit 1; }
command -v bun >/dev/null 2>&1 || { echo "Erro: bun não encontrado no PATH"; exit 1; }

# 1. Build Tailwind
bun run build

# 2. Build Zola
zola build

echo ""
echo "Build concluído. Saída em public/"
