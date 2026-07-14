#!/usr/bin/env bash
set -euo pipefail

# Safe deploy to GitHub Pages via isolated gh-pages branch.
# This script runs on the main branch and pushes only the Zola build output
# (public/) to the orphan gh-pages branch, leaving main clean of generated files.

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

# Create isolated git repo for gh-pages.
mkdir -p "$TEMP_DIR/gh-pages"
cd "$TEMP_DIR/gh-pages"
git init -q
git remote add origin "$REMOTE_URL"
git checkout -q -b gh-pages

# Copy build output into the root of the temp repo.
cp -a "$PUBLIC_DIR"/. .

# GitHub Pages needs a .nojekyll file to skip Jekyll processing.
touch .nojekyll

git add -A
git -c user.email="deploy@rio-makerspace" -c user.name="Deploy Script" \
  commit -q -m "Deploy site to GitHub Pages ($(date -u +'%Y-%m-%d %H:%M:%S UTC'))"

# Force push only the gh-pages branch.
echo "Pushing to origin/gh-pages..."
git push -q origin gh-pages --force

echo "Deploy complete. Set GitHub Pages source to branch 'gh-pages' / folder '/'"
