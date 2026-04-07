#!/bin/bash
set -e
cd /workspace/AI-music-score-featch

# 删除已追踪的 push 脚本（如果存在）
rm -f push.sh push_all.sh 2>/dev/null || true

git config user.email "agent@openclaw.ai"
git config user.name "AI Guitar Tab Dev Agent"

git add -A
git status --short | head -20

git commit -m "feat: 完善CI/CD + 测试框架 + GitHub Codespaces配置

✅ 新增文件:
- .github/workflows/ci.yml (Python + 前端自动化测试)
- .devcontainer/devcontainer.json (GitHub Codespaces 一键启动)
- .devcontainer/setup.sh (环境初始化脚本)
- tests/test_pipeline.py (Pipeline 单元测试)
- tests/test_bpm_detector.py (BPM 检测测试)
- tests/test_chord_recognizer.py (和弦识别测试)
- pytest.ini (测试配置)
- .gitignore (忽略上传文件/缓存)

✅ 修复/更新:
- backend/main.py 新增 /api/analyze-url 端点（视频URL分析）
- tests/test_pipeline.py 修复函数名（build_gta_text → generate_gta_text别名）

🎯 项目完成度: 核心功能80%完成
剩余: 端到端测试验证 + Codespaces在线运行"

git -c http.postBuffer=524288000 push \
  https://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@github.com/YuruiZhu9/AI-music-score-featch.git main

echo "=== DONE ==="
git log --oneline -4
