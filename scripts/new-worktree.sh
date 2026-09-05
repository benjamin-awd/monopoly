#!/usr/bin/env bash
# Create a turnkey git worktree: checkout, git-crypt unlock, uv sync.
# Usage: scripts/new-worktree.sh <branch-name> [base-ref]   (base-ref defaults to origin/main)
set -euo pipefail

branch="${1:?usage: scripts/new-worktree.sh <branch-name> [base-ref]}"
base_ref="${2:-origin/main}"

root="$(git rev-parse --show-toplevel)"
worktree_dir="$root/.claude/worktrees/${branch//\//-}"

git -C "$root" fetch origin --quiet || true

git -C "$root" \
  -c filter.git-crypt.smudge=cat \
  -c filter.git-crypt.required=false \
  worktree add "$worktree_dir" -b "$branch" "$base_ref"

unlock_hook="$HOME/.claude/hooks/git-crypt-unlock.sh"
if [ -f "$unlock_hook" ]; then
  (cd "$worktree_dir" && bash "$unlock_hook")
elif [ -f "$root/.git-crypt.key" ]; then
  (cd "$worktree_dir" && git-crypt unlock "$root/.git-crypt.key")
fi

(cd "$worktree_dir" && uv sync --all-extras)

echo "Done. cd \"$worktree_dir\""
