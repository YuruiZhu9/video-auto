#!/bin/bash
set -e
cd /workspace

# 任务1: push 语音克隆方案报告
echo "=== [任务1] Push 语音克隆方案报告 ==="
git push maxclaw- master && echo "✅ push 成功" || echo "⚠️ push 失败，retrying..."
git push maxclaw- master && echo "✅ push 成功" || echo "❌ push 失败"

# 任务2: 修复 cron job (ID: 1280bc4a-6791-4a8e-8c1b-436744c601c2)
echo "=== [任务2] 修复 03:00 同步 cron job ==="
CRON_ID="1280bc4a-6791-4a8e-8c1b-436744c601c2"
CRON_FILE="/root/.openclaw/cron/jobs.json"
NEW_MSG="执行以下命令完成 Git 仓库每日同步：

1. /workspace/agents/video-auto → YuruiZhu9/video-auto (master)
2. /workspace/AI-music-score-featch → YuruiZhu9/AI-music-score-featch (main)
3. /workspace → YuruiZhu9/Maxclaw- (master)

如果脚本不存在，手动执行：
\`\`\`bash
TOKEN=\$(cat /workspace/.github-token 2>/dev/null || echo \"\")
BASE=\"https://YuruiZhu9:\${TOKEN}@github.com\"
cd /workspace/agents/video-auto && git remote set-url origin \"\${BASE}/YuruiZhu9/video-auto.git\" && git add -A && git diff --cached --quiet || { git commit -m \"Auto sync \$(date)\"; git push origin master; }
cd /workspace/AI-music-score-featch && git remote set-url origin \"\${BASE}/YuruiZhu9/AI-music-score-featch.git\" && git add -A && git diff --cached --quiet || { git commit -m \"Auto sync \$(date)\"; git push origin main; }
cd /workspace && git remote set-url maxclaw- \"\${BASE}/YuruiZhu9/Maxclaw-.git\" && git add -A && git diff --cached --quiet || { git commit -m \"Workspace auto sync \$(date)\"; git push maxclaw- master; }
\`\`\`

同步完成后把结果追加到 /workspace/memory/git-sync.log"

python3 -c "
import json

with open('$CRON_FILE', 'r') as f:
    data = json.load(f)

for job in data['jobs']:
    if job['id'] == '$CRON_ID':
        old_msg = job['payload']['message']
        job['payload']['message'] = '''$NEW_MSG'''
        print(f'✅ 找到并更新 cron job: {job[\"name\"]}')
        print(f'   旧消息前60字: {old_msg[:60]}...')
        print(f'   新消息前60字: {job[\"payload\"][\"message\"][:60]}...')
        break
else:
    print('❌ 未找到 cron job: $CRON_ID')

with open('$CRON_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('✅ jobs.json 已保存')
"

echo "=== 全部完成 ==="
