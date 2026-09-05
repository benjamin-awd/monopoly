#!/usr/bin/env bash
# Create a turnkey git worktree: checkout + git-crypt unlock.
# The venv is provisioned by .envrc (uv sync) on first `cd` into the worktree.
# Usage: scripts/new-worktree.sh <branch-name> [base-ref]   (base-ref defaults to origin/main)
set -euo pipefail

branch="${1:?usage: scripts/new-worktree.sh <branch-name> [base-ref]}"
base_ref="${2:-origin/main}"

root="$(git rev-parse --show-toplevel)"
worktree_dir="$root/.claude/worktrees/${branch//\//-}"

git -C "$root" fetch origin --quiet || true

# Create -b for a new branch; reuse the branch if it already exists.
if git -C "$root" show-ref --quiet --verify "refs/heads/$branch"; then
  new_branch_args=("$branch")
else
  new_branch_args=(-b "$branch" "$base_ref")
fi

# smudge=cat lets encrypted files check out verbatim before git-crypt is unlocked.
git -C "$root" \
  -c filter.git-crypt.smudge=cat \
  -c filter.git-crypt.required=false \
  worktree add "$worktree_dir" "${new_branch_args[@]}"

unlock_hook="$HOME/.claude/hooks/git-crypt-unlock.sh"
if [ -f "$unlock_hook" ]; then
  (cd "$worktree_dir" && bash "$unlock_hook")
elif [ -f "$root/.git-crypt.key" ]; then
  (cd "$worktree_dir" && git-crypt unlock "$root/.git-crypt.key")
fi

# Allow direnv so .envrc provisions the venv on entry (no-op if direnv absent).
if command -v direnv >/dev/null 2>&1; then
  direnv allow "$worktree_dir"
fi

echo "Done. cd \"$worktree_dir\""
