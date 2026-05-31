#!/usr/bin/env bash
set -euo pipefail

REPO_FULL_NAME="${1:-Akanom/universal-output-hub}"
REPO_URL="https://github.com/${REPO_FULL_NAME}.git"

if [ ! -d .git ]; then
  git init
fi

git add .
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "Initial release: universal output hub"
fi

git branch -M main
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git push -u origin main
