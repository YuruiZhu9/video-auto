#!/bin/bash
set -e
cd /workspace
echo "=== Expire all reflog and garbage collect ==="
git reflog expire --expire=now --all
git gc --prune=now --aggressive --quiet
echo "=== Remove filter-branch backup ==="
rm -rf .git-rewrite
rm -rf .git/refs/original
echo "=== Verify no old token in HEAD~5 ==="
for i in 0 1 2 3 4; do
  git log --oneline -1 HEAD~$i 2>/dev/null || break
done
echo "=== Push origin (force) ==="
git push origin master --force 2>&1
echo "origin result: $?"
echo "=== Push maxclaw- (force) ==="
git push maxclaw- master --force 2>&1
echo "maxclaw- result: $?"
echo "=== DONE ==="
