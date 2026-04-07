#!/bin/bash
# Auto upload reports to GitHub

cd /workspace

# GitHub Token
TOKEN="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"
REPO="https://YuruiZhu9:${TOKEN}@github.com/YuruiZhu9/Maxclaw-.git"

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

# 推送到GitHub
git push "$REPO" master

echo "Reports uploaded at $DATE"
