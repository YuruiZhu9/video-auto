---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 03683cab6924d6b5bdabf5ee039b9191
    PropagateID: 03683cab6924d6b5bdabf5ee039b9191
    ReservedCode1: 3044022058e6da3e5a58d8e2f7fb0e2ebb8a83ab739c397f94ce9d75fcb76de5b8b49def02202401e1ccd1b8448a9f424dd214a34aa2f14af6aee163011ce78642722be2204d
    ReservedCode2: 3046022100dbd0bb6da29ecf7e31a19af8f3cf937b2bc2b7635846ee27223e5f2f9c649f6e022100a718a0ea8f87c6e12ccac0cd2f71b5d6e45fb94a2968f974f89a84d6067d68e3
---

# OpenClaw 使用心得与训练指南

本文档记录 OpenClaw 的使用心得、训练技巧和最佳实践。

---

## OpenClaw 训练大师

> 来源：用户分享的智能体 Prompt，已适配到当前环境

你是一位专业的 OpenClaw 训练专家，致力于帮助用户将 OpenClaw 打造成更强大、更智能的个人 AI 代理。

### 核心身份

你是用户的 **OpenClaw 增强顾问**，具备以下专长：
- 深入理解 OpenClaw 的架构（Model、Agent、Skill、MCP 模块化设计）
- 精通 SKILL.md 和 AGENTS.md 的编写规范
- 熟悉各种 MCP（Model Context Protocol）服务器的配置与集成
- 擅长解决本地部署和跨平台交互的技术问题
- 善于发现创新的自动化场景和工作流程

### 工作原则

1. **启发式引导** - 不要只是回答问题，要引导用户思考更深层的可能性
2. **实战导向** - 每个建议都要附带可执行的步骤
3. **问题解决专家** - 系统性诊断技术问题的根因
4. **持续进化思维** - 鼓励用户记录和沉淀最佳实践

### 核心能力模块

| 模块 | 说明 |
|------|------|
| 配置优化 | 环境配置诊断与优化、模型选择建议、性能调优 |
| 技能开发 | SKILL.md 文件结构设计、技能模块化和复用设计 |
| MCP 集成 | MCP 服务器选择和配置、多 MCP 协同工作流设计 |
| 场景创新 | 日常自动化场景挖掘、跨平台工作流设计 |
| 问题诊断 | 常见错误排查指南、日志分析和调试技巧 |

---

## 当前环境档案

### 硬件配置
- **设备**: Linux 服务器 (非 Mac mini)
- **模型**: MiniMax-M2.1 (MiniMax API)
- **上下文窗口**: 200k tokens

### 软件环境
- **OpenClaw**: 2026.2.15+
- **Node.js**: v22.22.0

### 已启用消息通道
- 钉钉 (DingTalk) - 主要入口
- 飞书 (Feishu)
- 其他通道待配置

### 常用 Skills
| 技能 | 用途 |
|------|------|
| weather | 天气查询 |
| coding-agent | 编程代理 |
| healthcheck | 系统健康检查 |
| minimax-docx | Word文档生成 |
| minimax-pdf | PDF生成 |
| minimax-xlsx | Excel生成 |

---

## 使用心得

### 1. 会话隔离配置

通过 `session.dmScope` 配置实现多通道会话隔离：
- `main` - 所有渠道共享同一会话
- `per-channel-peer` - 每个渠道独立会话（推荐）

配置示例：
```json
{
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

### 2. 定时任务

可用于：
- 定期抓取信息（AI资讯、技术文章）
- 定时提醒
- 周期性数据分析
- 自动报告生成

### 3. 消息通道

| 通道 | 用途 | 配置要点 |
|------|------|----------|
| 钉钉 | 日常对话、提醒 | 需要 clientId + clientSecret |
| 飞书 | 文档协作 | 需要 App ID + Secret |
| 网页端 | 主会话 | 默认启用 |

### 4. 记忆机制

- **MEMORY.md** - 长期记忆（主会话专用）
- **memory/YYYY-MM-DD.md** - 每日记录
- 文件记忆跨渠道共享，会话记忆隔离

---

## 进阶技巧

### 技能开发

创建自定义 Skill：
1. 在 `/workspace` 或 `/root/.openclaw/skills/` 目录创建技能文件夹
2. 编写 `SKILL.md` 定义技能行为
3. 配置技能入口和参数

### 定时任务

使用 Cron jobs 实现自动化：
```javascript
{
  "schedule": { "kind": "cron", "expr": "0 9 * * *" },
  "payload": { "kind": "agentTurn", "message": "任务描述" },
  "sessionTarget": "isolated"
}
```

### 消息发送

跨渠道发送消息：
```javascript
{
  "action": "send",
  "channel": "dingtalk",
  "message": "内容",
  "target": "用户ID"
}
```

---

## 常见问题

### Q: 多个渠道同时使用会共享会话吗？
A: 取决于 `session.dmScope` 配置。设置为 `per-channel-peer` 可实现隔离。

### Q: 如何配置新的消息通道？
A: 在 `openclaw.json` 的 `channels` 或 `plugins.entries` 中添加对应配置。

### Q: 定时任务失败怎么办？
A: 检查 cron 表达式、payload 内容，以及目标渠道的连接状态。

---

## 待探索方向

- [ ] MCP 服务器集成
- [ ] 更多自动化工作流
- [ ] 跨平台数据联动
- [ ] 自定义 Skill 开发

---

*最后更新: 2026-03-04*
