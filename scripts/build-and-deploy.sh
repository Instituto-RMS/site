#!/usr/bin/env bash
# Builda o site localmente e publica na branch gh-pages.
#
# Uso:
#   source .env && ./scripts/build-and-deploy.sh
#
# O script faz:
#   1. Notion sync (python scripts/sync_notion.py)
#   2. Tailwind build (bun run build)
#   3. Zola build (zola build)
#   4. Publica o conteúdo de public/ na branch gh-pages e faz push
#
# Requer:
#   - zola
#   - bun
#   - python3 + requests
#   - Variáveis de ambiente: NOTION_TOKEN, NOTION_PROJECTS_DB_ID, NOTION_EVENTS_DB_ID

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PUBLIC_DIR="${REPO_ROOT}/public"
BUILD_BRANCH="gh-pages"

cd "${REPO_ROOT}"

# Verifica dependências
command -v zola >/dev/null 2>&1 || { echo "Erro: zola não encontrado no PATH"; exit 1; }
command -v bun >/dev/null 2>&1 || { echo "Erro: bun não encontrado no PATH"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Erro: python3 não encontrado no PATH"; exit 1; }

# Verifica variáveis do Notion
for var in NOTION_TOKEN NOTION_PROJECTS_DB_ID NOTION_EVENTS_DB_ID; do
    if [[ -z "${!var:-}" ]]; then
        echo "Erro: variável ${var} não está definida."
        echo "Rode: source .env && ./scripts/build-and-deploy.sh"
        exit 1
    fi
done

# 1. Sync Notion
python3 "${SCRIPT_DIR}/sync_notion.py"

# 2. Build Tailwind
bun run build

# 3. Build Zola
rm -rf "${PUBLIC_DIR}"
zola build

# 4. Publica na branch gh-pages
if git show-ref --verify --quiet "refs/heads/${BUILD_BRANCH}"; then
    git branch -D "${BUILD_BRANCH}"
fi

# Cria branch orfã com o conteúdo de public/
git checkout --orphan "${BUILD_BRANCH}"
git rm -rf . >/dev/null 2>&1 || true

# Move tudo de public/ para a raiz
cp -a "${PUBLIC_DIR}/." .
rm -rf "${PUBLIC_DIR}"

# Limpa artefatos que não devem ir pro Pages
rm -rf node_modules .env .env.local .gitignore
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -delete 2>/dev/null || true

# Adiciona .nojekyll para GitHub Pages não tentar processar com Jekyll
touch .nojekyll

# Commita apenas arquivos do site
git add -A
git commit -m "Deploy site $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true

echo ""
echo "Build concluído. Para publicar, rode:"
echo "  git push origin ${BUILD_BRANCH} --force"
echo ""
echo "Ou, para enviar agora, descomente a linha abaixo no script."
# git push origin "${BUILD_BRANCH}" --force
