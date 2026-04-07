#!/bin/bash
echo "=== 开始恢复 cron 任务 ==="
date

# 检查 f5afdfd6 - AI协作视频制作Agent
echo "--- 任务1: f5afdfd6 ---"
result=$(curl -s -X POST http://127.0.0.1:18789/api/cron/run \
  -H "Authorization: Bearer minimax-agent" \
  -H "Content-Type: application/json" \
  -d '{"jobId":"f5afdfd6-068f-4518-80f8-fdf5f8741c1b"}')
echo "结果: $result"

sleep 2

# 检查 45edfdae - 小红书内容运营
echo "--- 任务2: 45edfdae ---"
result=$(curl -s -X POST http://127.0.0.1:18789/api/cron/run \
  -H "Authorization: Bearer minimax-agent" \
  -H "Content-Type: application/json" \
  -d '{"jobId":"45edfdae-32cc-4f50-be01-83adbb462f03"}')
echo "结果: $result"

sleep 2

# 跳过 68507237 - 已在运行

# 检查 78df27ac - 跨Agent新技术同步中心
echo "--- 任务4: 78df27ac ---"
result=$(curl -s -X POST http://127.0.0.1:18789/api/cron/run \
  -H "Authorization: Bearer minimax-agent" \
  -H "Content-Type: application/json" \
  -d '{"jobId":"78df27ac-3dfa-4070-adae-c4bb661ac3ed"}')
echo "结果: $result"

sleep 2

# 检查 f040a62b - LlamaFactory论文资源
echo "--- 任务5: f040a62b ---"
result=$(curl -s -X POST http://127.0.0.1:18789/api/cron/run \
  -H "Authorization: Bearer minimax-agent" \
  -H "Content-Type: application/json" \
  -d '{"jobId":"f040a62b-b27f-40dd-8e5b-c35f80728afb"}')
echo "结果: $result"

echo "=== 完成 ==="
date
