#!/usr/bin/env bash
# Builda o site localmente.
#
# Uso:
#   ./scripts/build.sh
#
# O script faz:
#   1. Tailwind build (bun run build)
#   2. Zola build
#
# Depois é só commitar o public/ junto com as alterações de código.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PUBLIC_DIR="${REPO_ROOT}/public"

cd "${REPO_ROOT}"

# Verifica dependências
command -v zola >/dev/null 2>&1 || { echo "Erro: zola não encontrado no PATH"; exit 1; }
command -v bun >/dev/null 2>&1 || { echo "Erro: bun não encontrado no PATH"; exit 1; }

# 1. Build Tailwind
bun run build

# 2. Build Zola
rm -rf "${PUBLIC_DIR}"
zola build

echo ""
echo "Build concluído. Commit o public/ junto com suas alterações."
