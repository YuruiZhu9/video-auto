# OpenClaw 配置审查报告

> 生成时间：2026-03-27 04:36 GMT+8  
> OpenClaw 版本：2026.2.15（CLI 2026.3.3）  
> 参考文档：https://docs.openclaw.ai/gateway/configuration  

---

## 一、当前配置概览

配置文件：`/root/.openclaw/openclaw.json`

| 配置区段 | 状态 | 备注 |
|---------|------|------|
| `meta` | ✅ | 版本信息完整 |
| `wizard` | ✅ | wizard 元数据正常 |
| `logging` | ⚠️ | 仅有 `file`，缺少 `level`/`consoleLevel` |
| `auth` | ✅ | Minimax auth profile 正常 |
| `models` | ✅ | Minimax provider 已配置 |
| `agents` | ⚠️ | 基础配置可用，缺少高级选项 |
| `tools` | 🔴 | **媒体工具完全禁用**；网络工具禁用 |
| `messages` | ⚠️ | 仅配置 `ackReactionScope`，缺少队列/TTS等 |
| `commands` | ✅ | native/auto 正常 |
| `session` | ✅ | `dmScope: per-channel-peer` 配置正确 |
| `channels` | ✅ | 钉钉已启用 |
| `gateway` | ⚠️ | 基础正常，缺少 `trustedProxies`/`controlUi` |
| `plugins` | ✅ | 5个插件正常加载 |

---

## 二、逐项分析与优化建议

### 2.1 `logging` — 日志配置（建议优化）

**当前状态：**
```json
"logging": {
  "file": "/tmp/claw_logs/openclaw-2026-03-25.log"
}
```

**文档标准选项：**
| 选项 | 默认值 | 说明 |
|------|--------|------|
| `level` | `"info"` | 全局日志级别 |
| `consoleLevel` | `"info"` | 控制台日志级别 |
| `consoleStyle` | `"pretty"` | 控制台样式 |
| `redactSensitive` | `"tools"` | 敏感信息脱敏模式 |
| `redactPatterns` | `[]` | 自定义脱敏正则 |
| `file` | - | 日志文件路径 |

**建议配置：**
```json
"logging": {
  "file": "/tmp/claw_logs/openclaw-2026-03-25.log",
  "level": "info",
  "consoleLevel": "warn",
  "redactSensitive": "tools",
  "redactPatterns": ["sk-.*", "ghFrmLNRUb3.*"]
}
```

**理由：**
- `consoleLevel: "warn"` 减少主控台噪音，便于专注核心输出
- 自定义脱敏正则保护 API Key 和 Secret 不出现在日志中
- 当前仅设置 `file`，日志级别默认为 info，可能产生过多日志

---

### 2.2 `tools` — 工具配置（🔴 关键问题）

**当前状态：**
```json
"tools": {
  "deny": ["image", "web_search", "web_fetch"],
  "web": { "search": { "enabled": false }, "fetch": { "enabled": false } },
  "media": { "image": { "enabled": false } }
}
```

**问题分析：**
根据 USER.md 和内存日志，用户已部署了三个定时 AI Agent：
- **信息抓取助手**：需要 `web_search` 和 `web_fetch` 抓取 AI 资讯
- **技术前沿分析师**：需要从 arXiv、招聘网站抓取内容
- **商业需求洞察分析师**：需要从 Product Hunt、V2EX 等抓取商机

**当前配置完全禁用了这些能力。**

**文档标准选项（`tools.web`）：**
| 选项 | 类型 | 默认值 |
|------|------|--------|
| `search.enabled` | boolean | - |
| `search.apiKey` | string | - |
| `search.maxResults` | number | 5 |
| `search.timeoutSeconds` | number | 30 |
| `search.cacheTtlMinutes` | number | 15 |
| `fetch.enabled` | boolean | true |
| `fetch.maxChars` | number | 50000 |
| `fetch.timeoutSeconds` | number | 30 |
| `fetch.cacheTtlMinutes` | number | 15 |
| `fetch.readability` | boolean | true |
| `fetch.firecrawl.enabled` | boolean | - |
| `fetch.firecrawl.apiKey` | string | - |

**文档标准选项（`tools.media`）：**
| 选项 | 类型 | 默认值 |
|------|------|--------|
| `concurrency` | number | 2 |
| `image.enabled` | boolean | - |
| `audio.enabled` | boolean | - |
| `video.enabled` | boolean | - |
| `image.maxBytes` | number | 10485760 (10MB) |
| `audio.maxBytes` | number | 20971520 (20MB) |
| `video.maxBytes` | number | 52428800 (50MB) |

**建议配置（按需启用）：**
```json
"tools": {
  "deny": [],
  "web": {
    "search": {
      "enabled": true,
      "maxResults": 10,
      "timeoutSeconds": 30,
      "cacheTtlMinutes": 60
    },
    "fetch": {
      "enabled": true,
      "maxChars": 100000,
      "timeoutSeconds": 30,
      "cacheTtlMinutes": 30,
      "readability": true
    }
  },
  "media": {
    "concurrency": 4,
    "image": { "enabled": true },
    "audio": { "enabled": true },
    "video": { "enabled": true }
  }
}
```

**特别说明：**
- TOOLS.md 中已有 `batch_web_search`（博查AI搜索 API Key: `sk-7aa8fbfa43534a9e8fb26a3d1ab74b6a`），该工具通过 exec + curl 调用，不依赖 `tools.web.search`
- 但 `images_understand`、`videos_understand`、`extract_content_from_websites` 等工具依赖 `tools.media` 的启用状态
- 当前 `image` 禁用状态下，`images_understand` 工具可能受影响

---

### 2.3 `agents` — Agent 配置（⚠️ 建议增强）

**当前状态：**
```json
"agents": {
  "defaults": {
    "workspace": "/workspace",
    "compaction": { "mode": "safeguard" },
    "timeoutSeconds": 300,
    "maxConcurrent": 4,
    "subagents": { "maxConcurrent": 8 }
  },
  "list": [{ "id": "main", "default": true, "subagents": { "allowAgents": ["*"] } }]
}
```

**文档标准选项（`agents.defaults`）：**
| 选项 | 默认值 | 当前值 | 建议 |
|------|--------|--------|------|
| `workspace` | `~/.openclaw/workspace` | `/workspace` | ✅ 正确 |
| `repoRoot` | auto-detect | 未设置 | 建议添加 |
| `bootstrapMaxChars` | 20000 | 未设置 | ✅ 默认 |
| `userTimezone` | host timezone | 未设置 | 建议设为 `"Asia/Shanghai"` |
| `timeFormat` | `"auto"` | 未设置 | ✅ 默认 |
| `model.primary` | - | 未设置 | 建议设为 `"minimax/auto"` |
| `model.fallbacks` | - | 未设置 | 可选 |
| `contextPruning` | - | 未设置 | 建议配置 |
| `compaction` | - | `safeguard` | ✅ 正确 |
| `maxConcurrent` | 1 | 4 | ✅ 合理 |
| `thinkingDefault` | - | 未设置 | 可选 |
| `verboseDefault` | - | 未设置 | 可选 |
| `elevatedDefault` | - | 未设置 | 可选 |
| `timeoutSeconds` | 600 | 300 | ⚠️ 见下方说明 |
| `mediaMaxMb` | 5 | 未设置 | 建议设为 20 |
| `heartbeat` | - | 未设置 | 建议配置 |
| `subagents.maxConcurrent` | - | 8 | ✅ 合理 |
| `exec` | - | 未设置 | 建议配置 |
| `contextTokens` | 200000 | 未设置 | 建议确认 |

**超时问题：**
根据 memory/2026-03-26.md 记录，技术追踪 Agent 多次因超时（300s）失败。文档默认 600s，建议：
```json
"timeoutSeconds": 600
```

**主 Agent Identity（建议新增）：**
```json
"identity": {
  "name": "小M",
  "emoji": "🤖",
  "theme": "专业、干练、直接、有主见的AI助手"
}
```

**Context Pruning（建议启用）：**
```json
"contextPruning": {
  "mode": "heuristic",
  "aggressiveToolTruncation": true,
  "aggressiveToolTruncationChars": 3000
}
```

**Heartbeat（建议配置）：**
```json
"heartbeat": {
  "enabled": true,
  "intervalMs": 300000,
  "file": "HEARTBEAT.md"
}
```

**Exec 配置（建议配置）：**
```json
"exec": {
  "maxConcurrent": 4,
  "defaultTimeoutMs": 60000,
  "elevated": {
    "enabled": true
  }
}
```

**Subagent 安全增强：**
`allowAgents: ["*"]` 允许所有 subagent 类型，建议保留（当前环境已通过 matrix-claw-enhancement 插件实现能力边界保护）。

---

### 2.4 `messages` — 消息配置（⚠️ 建议增强）

**当前状态：**
```json
"messages": {
  "ackReactionScope": "group-mentions"
}
```

**文档标准选项：**
| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `ackReaction` | string | `👀` | 确认反应 emoji |
| `ackReactionScope` | string | `"group-mentions"` | ✅ 已配置 |
| `removeAckAfterReply` | boolean | false | 回复后移除确认 |
| `responsePrefix` | string | - | 出站前缀 |
| `queue.mode` | string | `"collect"` | 队列模式 |
| `queue.debounceMs` | number | 1000 | 队列防抖 |
| `queue.cap` | number | 20 | 队列上限 |
| `queue.drop` | string | `"summarize"` | 丢弃策略 |
| `queue.byChannel` | object | - | 按渠道配置 |
| `inbound.debounceMs` | number | 2000 | 入站防抖 |
| `inbound.byChannel` | object | - | 按渠道入站配置 |
| `groupChat.historyLimit` | number | - | 群聊历史限制 |
| `tts` | object | - | TTS 配置 |

**TTS 配置（建议启用）：**
USER.md 和 SOUL.md 均提到 TTS 能力：
```json
"tts": {
  "auto": "tagged",
  "mode": "final",
  "maxTextLength": 4000,
  "timeoutMs": 30000
}
```
- `auto: "tagged"`：仅在文本包含特定标签时触发 TTS，避免每次回复都语音播报
- `auto: "always"`：每次回复都 TTS（可能干扰用户）

**消息队列（建议配置）：**
```json
"queue": {
  "mode": "collect",
  "debounceMs": 2000,
  "cap": 30,
  "drop": "summarize"
}
```
- 对于定时任务触发多条消息的场景，`collect` 模式可合并响应
- `debounceMs: 2000` 防止消息过于频繁

**群聊历史（建议配置）：**
```json
"groupChat": {
  "historyLimit": 50
}
```

---

### 2.5 `session` — 会话配置（✅ 良好）

**当前状态：**
```json
"session": {
  "dmScope": "per-channel-peer"
}
```

**建议增强：**
```json
"session": {
  "dmScope": "per-channel-peer",
  "reset": {
    "mode": "daily",
    "atHour": 4
  },
  "store": null,
  "mainKey": "main",
  "agentToAgent": {
    "maxPingPongTurns": 5
  },
  "typingMode": "partial",
  "typingIntervalSeconds": 6
}
```

**说明：**
- `reset.mode: "daily"` 每天凌晨自动重置会话，防止上下文无限膨胀
- `reset.atHour: 4` 选在凌晨4点（低峰期）执行重置
- `agentToAgent` 支持未来的多 Agent 协作场景

---

### 2.6 `gateway` — 网关配置（⚠️ 建议增强）

**当前状态：**
```json
"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "loopback",
  "auth": { "mode": "token", "token": "minimax-agent" },
  "tailscale": { "mode": "off", "resetOnExit": false },
  "reload": { "mode": "hot", "debounceMs": 300 },
  "nodes": {
    "denyCommands": ["camera.snap", "camera.clip", "screen.record", "calendar.add", "contacts.add", "reminders.add"]
  }
}
```

**建议新增：**
```json
"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "loopback",
  "auth": { "mode": "token", "token": "minimax-agent" },
  "tailscale": { "mode": "off", "resetOnExit": false },
  "reload": { "mode": "hot", "debounceMs": 300 },
  "nodes": {
    "denyCommands": ["camera.snap", "camera.clip", "screen.record", "calendar.add", "contacts.add", "reminders.add"]
  },
  "trustedProxies": ["127.0.0.1", "::1"],
  "controlUi": {
    "basePath": "/",
    "allowInsecureAuth": false
  }
}
```

**说明：**
- `trustedProxies`：在有反向代理（如 nginx/Caddy）的环境下防止 IP 伪造
- `controlUi.basePath`：默认根路径，适合当前环境

---

### 2.7 `channels` — 渠道配置（✅ 已完善）

**当前状态：** 钉钉已配置并启用。

**飞书渠道：** 虽然插件已加载（`plugins.load.paths` 中有 feishu），但 `channels` 中未配置飞书。根据 USER.md，飞书为常用渠道，建议补充：

```json
"channels": {
  "dingtalk": {
    "clientId": "dingplpxy12c9b5divsd",
    "clientSecret": "ghFrmLNRUb3ynoPKEHRnpe-NcT_CO7nt6wG_HS8dJ37L_rsvMKw0wQiONl80pmoj",
    "enabled": true,
    "dmPolicy": "pairing"
  },
  "feishu": {
    "enabled": true,
    "dmPolicy": "pairing"
  }
}
```

**飞书配置说明：**
- 飞书插件已加载，渠道配置参考飞书官方文档补充 App ID 和 App Secret
- `dmPolicy: "pairing"` 要求用户先发起配对，安全且可控

---

### 2.8 `plugins` — 插件配置（✅ 良好）

**当前状态：** 5个插件正常加载。

**建议新增 `allow` 白名单（安全增强）：**
```json
"plugins": {
  "enabled": true,
  "allow": [
    "claw-bridge",
    "feishu",
    "dingtalk",
    "matrix-mcp",
    "matrix-claw-enhancement"
  ],
  "load": {
    "paths": [
      "/app/openclaw/extensions/claw-bridge",
      "/app/openclaw/extensions/feishu",
      "/app/openclaw/extensions/dingtalk",
      "/app/openclaw/extensions/matrix-mcp",
      "/app/claw/plugins/matrix-claw-enhancement"
    ]
  },
  "entries": {
    "claw-bridge": { "config": { "verbose": false } },
    "dingtalk": {
      "enabled": true,
      "config": {
        "enabled": true,
        "clientId": "dingplpxy12c9b5divsd",
        "clientSecret": "ghFrmLNRUb3ynoPKEHRnpe-NcT_CO7nt6wG_HS8dJ37L_rsvMKw0wQiONl80pmoj",
        "debug": false
      }
    }
  }
}
```

**说明：**
- `allow` 白名单明确只加载受信任的插件，防止未来意外加载恶意插件
- 插件配置中移除 debug 模式，减少日志噪音

---

### 2.9 缺失的高级配置区段（建议评估后添加）

| 配置路径 | 说明 | 优先级 |
|---------|------|--------|
| `agents.defaults.contextTokens` | 上下文 token 上限（默认 200k） | 中 |
| `agents.defaults.mediaMaxMb` | 媒体大小限制（当前默认 5MB） | 中 |
| `skills.load.extraDirs` | 额外技能目录 | 低 |
| `cron.maxConcurrentRuns` | Cron 并发数限制（默认 2） | 中 |
| `ui.assistant.name` | UI 显示名称 | 低 |
| `ui.seamColor` | UI 主题色 | 低 |
| `canvasHost` | Canvas 文件服务配置 | 低 |
| `env.shellEnv.enabled` | Shell 环境变量加载 | 低 |
| `discovery.mdns.mode` | mDNS 发现模式 | 低 |

---

## 三、配置变更操作指南

> ⚠️ **重要提醒**：配置变更必须通过 `gateway` 工具（`config.patch`）操作，禁止直接编辑 `openclaw.json`。详见平台安全规则。

### 推荐变更优先级

**P0（立即建议）：**
1. 启用 `tools.media.image.enabled` — 影响图片理解工具
2. 启用 `tools.web.fetch` — 信息抓取助手需要
3. 将 `agents.defaults.timeoutSeconds` 调整为 `600` — 防止定时任务超时
4. 添加 `logging.level` 和脱敏正则 — 安全性提升

**P1（近期建议）：**
5. 配置 `agents.defaults.heartbeat` — 心跳机制稳定
6. 配置 `messages.tts` — TTS 语音播报能力
7. 配置 `messages.queue` — 消息合并防抖
8. 添加 `session.reset` 策略 — 防止上下文无限膨胀

**P2（可选优化）：**
9. 添加主 Agent `identity` — 个性化展示
10. 补充飞书渠道配置
11. 添加 `plugins.allow` 白名单
12. 调整 `logging.consoleLevel` 为 `warn`

### 操作示例（config.patch）

```json
{
  "raw": {
    "logging": {
      "level": "info",
      "consoleLevel": "warn",
      "redactPatterns": ["sk-.*", "ghFrmLNRUb3.*"]
    },
    "tools": {
      "deny": [],
      "web": {
        "search": { "enabled": true, "maxResults": 10, "timeoutSeconds": 30, "cacheTtlMinutes": 60 },
        "fetch": { "enabled": true, "maxChars": 100000, "timeoutSeconds": 30, "cacheTtlMinutes": 30, "readability": true }
      },
      "media": {
        "concurrency": 4,
        "image": { "enabled": true },
        "audio": { "enabled": true },
        "video": { "enabled": true }
      }
    },
    "agents": {
      "defaults": {
        "timeoutSeconds": 600,
        "mediaMaxMb": 20,
        "userTimezone": "Asia/Shanghai",
        "contextPruning": { "mode": "heuristic", "aggressiveToolTruncation": true, "aggressiveToolTruncationChars": 3000 },
        "heartbeat": { "enabled": true, "intervalMs": 300000 }
      }
    }
  },
  "note": "P0配置优化：日志增强、工具启用、超时调整",
  "restartDelayMs": 3000
}
```

---

## 四、配置变更历史

| 日期 | 版本 | 变更内容 | 操作人 |
|------|------|---------|--------|
| 2026-03-05 | 2026.2.15 | 初始配置版本 | - |
| 2026-03-27 | 审查 | 生成配置审查报告，识别优化点 | 小M (subagent) |

---

*本文档由 OpenClaw 配置专家自动生成，基于 OpenClaw 2026.3.3 官方文档（https://docs.openclaw.ai/gateway/configuration）*
