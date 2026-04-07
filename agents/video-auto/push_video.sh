#!/bin/bash
set -e
cd /workspace/agents/video-auto

echo "=== Adding video files to git ==="
git add video/ 2>/dev/null || true

echo "=== Checking what will be committed ==="
git status --short video/ | head -20

echo "=== Checking git user ==="
git config user.name || git config --global user.name "OpenClaw Agent"
git config user.email || git config --global user.email "agent@openclaw.ai"

echo "=== Committing changes ==="
git commit -m "Add 2026-03-29 video project (slides, TTS, HTML player, README)" 2>/dev/null || echo "Nothing to commit or commit failed"

echo "=== Pushing to remote ==="
git push origin master 2>&1 | tail -10

echo "=== Verify push ==="
echo "Done! Check GitHub for updates."
