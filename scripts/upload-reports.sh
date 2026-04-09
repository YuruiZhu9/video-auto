#!/bin/bash
# Auto upload reports to GitHub
# Token 从环境变量 GITHUB_TOKEN 读取，请勿硬编码

cd /workspace

REPO="https://github.com/YuruiZhu9/Maxclaw-.git"

# 确认有 token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN environment variable not set"
    exit 1
fi

# 添加四个报告文件夹
git add reports/news/ reports/tech/ reports/business/ reports/openclaw/

# 检查是否有更改
if git diff --staged --quiet; then
    echo "No changes to commit"
    exit 0
fi

# 提交更改
DATE=$(date "+%Y-%m-%d %H:%M")
git commit -m "Update reports - $DATE"

# 推送到GitHub（token 从 ~/.git-credentials 自动读取）
git push "$REPO" master

echo "Reports uploaded at $DATE"
