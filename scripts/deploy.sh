#!/usr/bin/env bash
set -euo pipefail

# Safe deploy to GitHub Pages with incremental history preservation.
# This script runs on the main branch, preserves the existing gh-pages branch
# (including CNAME and other GitHub Pages settings), and adds a new commit
# containing only the current Zola build output.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUBLIC_DIR="$REPO_ROOT/public"
TEMP_DIR="$(mktemp -d)"
REMOTE_URL="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"

# Cleanup temp directory on exit.
trap 'rm -rf "$TEMP_DIR"' EXIT

cd "$REPO_ROOT"

# Safety checks
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  echo "Error: must be on main branch (current: $CURRENT_BRANCH)" >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Error: working tree has uncommitted changes. Commit or stash first." >&2
  exit 1
fi

# Build
./scripts/build.sh

# Verify public/ exists and is clean of secrets/build artifacts.
if [[ ! -d "$PUBLIC_DIR" ]]; then
  echo "Error: public/ directory not found after build" >&2
  exit 1
fi

for forbidden in .env .env.local .env.local.example node_modules .git; do
  if [[ -e "$PUBLIC_DIR/$forbidden" ]]; then
    echo "Error: forbidden item found in public/: $forbidden" >&2
    exit 1
  fi
done

# Prepare isolated git repo for gh-pages, preserving existing branch history.
mkdir -p "$TEMP_DIR/gh-pages"
cd "$TEMP_DIR/gh-pages"
git init -q
git remote add origin "$REMOTE_URL"

# Try to fetch the existing gh-pages branch so we can preserve its history.
if git fetch -q origin gh-pages 2>/dev/null; then
  git checkout -q gh-pages
else
  git checkout -q -b gh-pages
fi

# Replace the working tree contents with the fresh build output, but keep
# tracked files (e.g. CNAME, .nojekyll, custom 404s) if they still exist.
# First remove all tracked files so deleted source files are reflected.
git rm -rf -q . 2>/dev/null || true

# Copy build output into the root of the temp repo.
cp -a "$PUBLIC_DIR"/. .

# GitHub Pages needs a .nojekyll file to skip Jekyll processing.
touch .nojekyll

# Stage everything: existing preserved files plus fresh build output.
git add -A

# Only commit if there are actual changes to deploy.
if git diff --cached --quiet; then
  echo "No changes to deploy."
  exit 0
fi

git -c user.email="deploy@rio-makerspace" -c user.name="Deploy Script" \
  commit -q -m "Deploy site to GitHub Pages ($(date -u +'%Y-%m-%d %H:%M:%S UTC'))"

# Push the gh-pages branch (non-force to preserve history).
echo "Pushing to origin/gh-pages..."
git push -q origin gh-pages

echo "Deploy complete. GitHub Pages source should be branch 'gh-pages' / folder '/'"
echo "If this is the first deploy, ensure the Custom domain field in GitHub Pages settings matches the CNAME."
