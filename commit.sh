#!/bin/bash
set -e
cd /workspace/AI-music-score-featch
git config user.email "agent@openclaw.ai"
git config user.name "AI Guitar Tab Dev Agent"
echo "identity set"
git add -A
git status --short
