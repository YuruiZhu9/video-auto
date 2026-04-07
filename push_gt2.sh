#!/bin/bash
set -e
cd /workspace/AI-music-score-featch
git config user.email "agent@openclaw.ai"
git config user.name "AI Guitar Tab Dev Agent"

# 删除旧的前端（已合并到 ai-guitar-tab-frontend）
rm -rf frontend 2>/dev/null || true

# 添加并提交
git add -A
git commit -m "feat: 完善前端组件 + 修复路由 + 添加GTAViewer

✅ 新增/更新文件:
- ai-guitar-tab-frontend/src/App.tsx (完整路由+导航栏)
- ai-guitar-tab-frontend/src/pages/Home.tsx (路由跳转修复)
- ai-guitar-tab-frontend/src/pages/Result.tsx (完整结果展示页)
- ai-guitar-tab-frontend/src/components/GTAViewer.tsx (GTA文本谱渲染)
- backend/core/downloader.py (yt-dlp视频URL下载器)

✅ 主要修复:
- Home→Result 路由改用 query param (?taskId=)
- App.tsx 添加 BrowserRouter 路由配置
- 删除重复的 frontend/ 目录

🤖 定时任务超时已调整为25分钟"

git -c http.postBuffer=524288000 push \
  https://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@github.com/YuruiZhu9/AI-music-score-featch.git main
echo "PUSH_OK"
