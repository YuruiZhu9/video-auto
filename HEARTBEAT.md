---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 01e52fad52f2a29d6ff29fe54e37a30b
    PropagateID: 01e52fad52f2a29d6ff29fe54e37a30b
    ReservedCode1: 304402201b42b6b72d8e639aac8f276461206ec71b966541697c9772a82a91438a564da402204231b7cfd6279f7b33966fce20a914540ee312b7e246ae91a5efd3237f8e548d
    ReservedCode2: 3045022100bf122c3fa632c0b3db14f592fee6f28023ef5f915f6ae7454c62d35d1703e93c0220727d7eef164c0ba0cb3c7b2f80e3031e91160ae9b32b29ae8cdf723a4d4379f9
---

# Heartbeat 配置

## 执行频率
每 **1 小时** 自动触发一次

## 核心任务：检查未完成的定时任务

### 步骤 1：读取 cron 任务状态
调用 `cron(action=list)` 获取所有定时任务状态

### 步骤 2：识别问题任务
满足以下任一条件视为"未完成"：
- `lastStatus == "error"` 且 `lastRunStatus == "error"`
- `lastRunStatus == "ok"` 但 `lastDelivered == false` 且距上次运行超过 48 小时
- `lastRunAtMs` 早于当前时间 2 倍调度周期（任务漏跑了）

### 步骤 3：触发重新执行
对识别出的问题任务：
1. 使用 `openclaw cron run <jobId> --timeout <ms>` 触发（注意：不带 `--channel dingtalk`，该flag仅对edit有效）
2. timeout 建议：简单任务 90s，复杂任务 120-180s
3. 每次最多并行 5 个，超出的排队

### 步骤 4：更新 HEARTBEAT 状态
将本次检查结果追加写入 `/workspace/memory/heartbeat-state.json`
```json
{
  "lastCheck": <当前时间戳ms>,
  "issuesFound": [
    {
      "jobId": "xxx",
      "name": "任务名称",
      "issue": "上次状态",
      "action": "已触发/已排队"
    }
  ]
}
```

### 步骤 5：长期未交付任务上报
如果某个任务连续 3 次心跳检查都失败，发钉钉通知提醒用户：
```
⚠️ 定时任务持续失败：{任务名}
连续失败次数：{次数}
上次错误：{lastError}
建议手动检查任务配置
```

## 约束
- 心跳不执行内容生产任务，只负责监控和补救
- 每次心跳最多触发 5 个重新运行任务
- 连续重复失败的任务（consecutiveErrors > 10）不反复触发，改为上报用户
