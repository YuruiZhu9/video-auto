#!/bin/bash
set -e
cd /workspace/AI-music-score-featch

echo "=== Step 1: Clean up duplicate frontend directories ==="
# Remove the incomplete manual frontend dir if it exists alongside the init'd one
if [ -d "frontend" ] && [ -d "ai-guitar-tab-frontend" ]; then
    echo "Removing duplicate frontend/ (keeping ai-guitar-tab-frontend/)"
    rm -rf frontend
fi

echo "=== Step 2: Git identity ==="
git config user.email "agent@openclaw.ai"
git config user.name "AI Guitar Tab Dev Agent"

echo "=== Step 3: Stage all files ==="
git add -A

echo "=== Step 4: Commit ==="
git commit -m "feat: 完成后端核心模块 + 前端初始化（开发Agent首批交付）

✅ 后端模块:
- backend/core/bpm_detector.py (librosa 节拍/BPM 检测)
- backend/core/score_generator.py (GTA文本谱+PDF生成)
- backend/core/config.py (环境变量配置)
- backend/models/schemas.py (Pydantic数据模型)
- backend/main.py (FastAPI 入口，含全部API路由)

✅ 前端模块 (ai-guitar-tab-frontend/):
- src/pages/Home.tsx (上传页面)
- src/components/FileUploader.tsx (拖拽上传)
- src/components/ProgressBar.tsx (实时进度条)
- src/components/ChordViewer.tsx (和弦时间轴)
- src/api/client.ts (Axios API客户端)

✅ README.md (Vibe Coding开发流程文档)

🤖 Agent运行时间: 10分钟 | 状态: 超时，核心模块已完成"

echo "=== Step 5: Push ==="
git -c http.postBuffer=524288000 push \
  https://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@github.com/YuruiZhu9/AI-music-score-featch.git main

echo "=== DONE ==="
git log --oneline -3
