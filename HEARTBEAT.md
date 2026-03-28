# Video-Auto 心跳配置

> 与主 HEARTBEAT.md 完全隔离，独立运行
> 每 6 小时检查一次是否有待处理的内容生成任务

## 执行频率
每天 **4 次**：06:00 / 12:00 / 18:00 / 00:00（Asia/Shanghai）

## 核心任务

### 检查待处理任务
调用 `cron(action=list)` 获取当前会话中是否有 video-auto 相关任务的 pending 状态。

### 触发流水线条件
满足以下任一条件时，自动触发 video-auto 完整流水线：
- `input_topic` 文件存在（`/workspace/agents/video-auto/input/topic.txt`）
- `input_material` 文件存在（`/workspace/agents/video-auto/input/material.md`）

### 流水线执行（自动模式）
1. 读取 topic + material
2. 执行声音克隆（Fish Audio / TTS 备选）
3. 内容扩展（GLM-4-Flash）
4. 生成 HTML Slide（ppt-html-generator Skill）
5. 合成视频
6. 推送到 GitHub

### 无任务时
回复 `HEARTBEAT_OK`，不做任何操作。

## 约束
- 使用 `sessionTarget: isolated`，与主会话完全隔离
- 每次心跳最多运行 1 个 video-auto 流水线
- 连续失败 3 次后停止自动触发，改为通知用户
