#!/bin/bash
set -e
cd /workspace/AI-music-score-featch
echo "Local HEAD: $(git rev-parse HEAD)"
echo "Remote HEAD: $(git rev-parse origin/main)"
echo "Ahead: $(git rev-list --count origin/main..HEAD)"
git log --oneline origin/main..HEAD | head -5
