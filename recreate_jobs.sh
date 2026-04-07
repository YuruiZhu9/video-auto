#!/bin/bash
echo "=== Recreating Job 1 ==="
openclaw cron add \
  --name "AI协作视频制作Agent" \
  --cron "0 20 * * *" \
  --session isolated \
  --message "执行AI协作视频制作任务...\n\n详细任务见 /workspace/agents/video-workflow-prompt.md" \
  --timeout-seconds 600 \
  --announce \
  --channel dingtalk \
  --to "03003745585526383319" \
  --agent main \
  --json

echo ""
echo "=== Running new Job 1 ==="
NEW_JOB1=$(openclaw cron list --json 2>/dev/null | grep -o '"id": "[^"]*免费语音克隆方案Agent"' | head -1 | grep -o '[0-9a-f-]\{36\}')
echo "Job1 ID: $NEW_JOB1"
openclaw cron run "$NEW_JOB1" 2>&1

echo ""
echo "=== Running Job 2 ==="
NEW_JOB2=$(openclaw cron list --json 2>/dev/null | grep -o '"id": "[^"]*AI协作视频制作Agent"' | head -1 | grep -o '[0-9a-f-]\{36\}')
echo "Job2 ID: $NEW_JOB2"
openclaw cron run "$NEW_JOB2" 2>&1
