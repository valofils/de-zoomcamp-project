#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GITHUB_USER="valofils"
REPO_NAME="de-zoomcamp-project"
REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
COMMIT_MSG="${1:-feat: module 1 - docker, postgres, terraform setup}"

cd "$ROOT_DIR"

echo "=== GitHub Push ==="
echo "Repo: $REMOTE_URL"
echo ""

git add .
git status --short

echo ""
echo "Committing: '$COMMIT_MSG'"
git commit -m "$COMMIT_MSG" || echo "(nothing new to commit)"

echo ""
echo "Pushing to origin/main..."
git push -u origin main

echo ""
echo "✅ Pushed to https://github.com/${GITHUB_USER}/${REPO_NAME}"