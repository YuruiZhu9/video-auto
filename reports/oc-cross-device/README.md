# OpenClaw 跨设备控制框架 (clawctl)

> 轻量级 · 安全 · 随时可达 — 用手机/平板/Siri 随时控制服务器上的 OpenClaw

**当前版本：v2.11.0** | 2026-04-12 更新

---

## 核心能力

```
手机 Siri  ──→  快捷指令  ──→  clawctl API  ──→  OpenClaw Agent
Telegram  ──→  Bot 命令   ──→  clawctl API  ──→  OpenClaw Agent
微信/订阅号 ──→ 文字/语音 ──→  clawctl API  ──→  OpenClaw Agent
语音输入  ──→  Whisper   ──→  clawctl API  ──→  OpenClaw Agent
定时触发  ──→  Cron Job   ──→  clawctl API  ──→  OpenClaw Agent
Webhook   ──→  任意事件   ──→  clawctl API  ──→  OpenClaw Agent
手机浏览器 ──→ Web Admin  ──→  clawctl API  ──→  OpenClaw Agent（实时推送）
自然语言  ──→  NL Parser  ──→  clawctl API  ──→  OpenClaw Agent（v2.5 新增）
```

### v2.6.0 新增：🎙 自然语言任务接口（完整实现）

**一句话控制 OpenClaw，无需记住命令格式：**

```bash
# 方式一：POST（推荐）
curl -X POST http://localhost:8081/api/v1/nl \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-oc-execute-xxx" \
  -d '{"text": "帮我查一下今天有啥AI新闻", "channel": "dingtalk"}'

# 方式二：快捷指令 GET（直接在 Siri/快捷指令中调用）
http://localhost:8081/api/v1/nl/cmd?q=生成今日技术简报&channel=dingtalk&api_key=sk-xxx

# → 自动识别为 trigger_fetch，spawn info-fetcher，钉钉通知结果
# → {"success": true, "intent": "trigger_fetch", "task_id": "nl-xxx", "message": "收到！..."}
```

**5 个 NL 端点**：
- `POST /api/v1/nl` — 自然语言 → 自动解析执行
- `POST /api/v1/nl/preview` — 预览解析结果（不执行）
- `GET /api/v1/nl/intents` — 列出支持的 13 种意图及示例
- `POST /api/v1/nl/batch` — 批量自然语言解析
- `GET /api/v1/nl/cmd` — 快捷指令专用 GET 入口
```

支持 13 种意图：**生成报告 / 资讯抓取 / 技术分析 / 全量扫描 / 系统状态 / 任务查询 / 历史记录 / 取消任务 / 暂停定时 / 恢复定时 / 发送消息 / 自由提问 / 搜索查询**

### 新版本亮点（v2.8.0）
- 📱 **iOS/Android 快捷指令深度集成** — 对 Siri 说"AI简报"直接触发 OpenClaw 执行任务，13 个预设快捷指令模板，可一键导入
- 🤖 **NL + LLM 双引擎（v2.7）** — 规则引擎兜底 + GLM-4 语义增强，复杂指令零门槛解析，置信度 < 0.55 自动调用大模型
- 🏢 **多实例管理** — 注册多个 OpenClaw 实例，三种路由策略（轮询/最低负载/主备），熔断器自动故障转移
- 📊 **实时监控** — CPU/内存/磁盘/OpenClaw指标/P95延迟，5秒采集，1小时滑动窗口，SSE 实时推送
- 🚨 **智能告警** — 可配置阈值规则（gt/lt/gte/lte/eq），分级告警（info/warning/critical），冷却防抖，多通道通知
- 💬 **微信订阅号接入** — 文字/语音消息自动识别，14个快捷命令，客服消息主动推送
- 🎤 **全平台语音控制** — Whisper API / 本地 Whisper 多后端，唤醒词检测，TTS 语音播报
- 🌊 **流式执行** — SSE 实时推送任务输出，Web Admin v3 日志面板实时可见
- 🧠 **自然语言任务解析** — 13 种意图全覆盖，时间词/紧急度/技术关键词自动识别
- 🔀 **DAG 任务编排** — 多步骤任务自动串联，支持并行/串行/分支
- 🪝 **Webhook 回调** — 任务完成/失败自动回调（签名验证+重试）
- 📱 **PWA 移动端** — 可安装到主屏幕，底部 Tab 导航，实时日志
- 📲 **iOS 快捷指令** — Siri 语音一句话触发任务

---

## 快速开始

```bash
# 1. 安装依赖（使用 /app/.venv 虚拟环境）
cd /workspace/reports/oc-cross-device/代码实现
/app/.venv/bin/pip install -r fastapi_server/requirements.txt

# 2. 配置环境变量
export OPENCLAW_URL=http://localhost:18789
export OPENCLAW_TOKEN=your_token_here
export DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx

# 3. 启动服务（FastAPI，推荐）
/app/.venv/bin/python -m fastapi_server.main --port 8081

# 4. Web 管理界面
open http://localhost:8081/admin/
# 移动端优化版
open http://localhost:8081/admin/index_v2.html

# 5. 自然语言测试
curl -X POST http://localhost:8081/api/v1/nl \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{"text": "帮我查一下今天有啥AI新闻", "channel": "dingtalk"}'
```

# 4. Docker 部署
cd ../docker
docker-compose up --build -d
```

---

## 架构一览

```
clawctl/
├── core/                      # 核心模块
│   ├── client.py              # OpenClaw API 客户端（含 Gateway 全 API）
│   ├── task.py                # 任务定义与执行引擎
│   ├── auth.py                # API Key 认证 + 操作审计
│   ├── config.py              # YAML 配置加载
│   ├── database.py            # SQLite 任务历史库
│   ├── scheduler.py          # 定时任务调度器 (APScheduler)
│   ├── template_loader.py     # YAML 模板加载 + 热加载
│   ├── stream_manager.py      # SSE 流式执行引擎
│   ├── task_dag.py           # DAG 任务编排引擎
│   ├── multi_instance.py     # 多实例管理器 + 熔断器（v2.4 新增）
│   └── monitor.py            # 实时监控 + 告警引擎（v2.4 新增）
├── handlers/
│   ├── http_handler.py        # HTTP REST API
│   ├── sse_handler.py         # SSE 实时推送
│   ├── stream_routes.py       # 流式执行 API
│   ├── dag_routes.py          # DAG 管理 API
│   ├── telegram_bot.py        # Telegram Bot（Polling/Webhook）
│   ├── webhook_handler.py     # Webhook 触发
│   ├── voice_handler.py       # 语音控制（Whisper + TTS）
│   ├── voice_routes.py        # 语音 API
│   ├── wechat_handler.py      # 微信公众号处理器
│   ├── monitor_routes.py     # 监控 + 告警 + 多实例 API（v2.4 新增）
│   └── callback_handler.py    # 回调处理
├── notify/
│   ├── dingtalk.py            # 钉钉推送
│   ├── feishu.py              # 飞书推送
│   ├── telegram.py            # Telegram 推送
│   ├── wecom.py               # 企业微信推送
│   └── notification.py        # 统一通知接口
├── web_admin/
│   ├── index.html             # Web 管理面板（桌面端）
│   ├── index_v2.html          # Web 管理面板（移动端优化版 PWA）
│   ├── v3/                    # Web Admin v3（含 DAG 可视化）
│   └── dashboard.js            # 前端交互逻辑
├── templates/                 # 任务模板
│   └── schedules.yaml         # 定时任务 + 模板配置
├── cli.py                     # 命令行工具
└── server.py                  # Web 服务入口
```

## 新手指引

1. **首次配置**：编辑 `config.yaml`，填入 `openclaw.gateway_url` 和 `auth.api_keys`
2. **访问 Web 界面**：`http://服务器IP:18790` 或手机访问 `index_v2.html`
3. **移动端使用**：添加快捷指令（见 `快捷指令集成/iOS快捷指令集成指南.md`）
4. **定时任务**：编辑 `clawctl/templates/schedules.yaml` 或在 Web 界面创建
│   ├── http_handler.py        # Flask REST API
│   └── telegram_bot.py        # Telegram Bot (Polling)
├── notify/
│   └── __init__.py            # 钉钉/Telegram 通知推送
├── cli.py                     # 命令行工具
├── server.py                  # 服务入口
└── templates/
    └── schedules.yaml         # 任务模板 + 定时任务配置
```

---

## API 一览

### 多实例管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/monitor/instances` | 列出所有实例 |
| POST | `/api/v1/monitor/instances` | 注册新实例 |
| GET | `/api/v1/monitor/instances/{id}` | 实例详情 |
| PATCH | `/api/v1/monitor/instances/{id}` | 更新实例 |
| DELETE | `/api/v1/monitor/instances/{id}` | 注销实例 |
| POST | `/api/v1/monitor/instances/health-check` | 手动健康检查 |
| POST | `/api/v1/monitor/instances/select` | 策略选择最优实例 |

### 监控
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/monitor/snapshot` | 系统快照 |
| GET | `/api/v1/monitor/series/{metric}` | 指标时序 |
| GET | `/api/v1/monitor/dashboard` | Dashboard 全量汇总 |
| GET | `/api/v1/monitor/current/{metric}` | 当前指标值 |

### 告警
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/monitor/alerts/rules` | 列出告警规则 |
| POST | `/api/v1/monitor/alerts/rules` | 添加告警规则 |
| DELETE | `/api/v1/monitor/alerts/rules/{id}` | 删除规则 |
| GET | `/api/v1/monitor/alerts/active` | 当前告警 |
| GET | `/api/v1/monitor/alerts/history` | 告警历史 |
| POST | `/api/v1/monitor/alerts/{id}/ack` | 确认告警 |

### 核心接口
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/health` | 健康检查 | 无 |
| GET | `/api/v1/status` | 系统状态 | Read |
| POST | `/api/v1/tasks` | 创建任务 | Exec |
| GET | `/api/v1/tasks` | 列出任务 | Read |
| GET | `/api/v1/tasks/{id}` | 任务详情 | Read |
| DELETE | `/api/v1/tasks/{id}` | 取消任务 | Admin |

### 任务模板
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/templates` | 列出模板 | Read |
| GET | `/api/v1/templates/{name}` | 模板详情 | Read |
| POST | `/api/v1/templates/reload` | 热重载 | Admin |
| POST | `/api/v1/templates/{name}/execute` | 执行模板 | Exec |

### 定时任务
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/schedules` | 列出定时任务 | Read |
| POST | `/api/v1/schedules` | 创建定时任务 | Exec |
| PATCH | `/api/v1/schedules/{id}` | 启用/暂停 | Exec |
| DELETE | `/api/v1/schedules/{id}` | 删除定时任务 | Admin |
| POST | `/api/v1/schedules/{id}/trigger` | 立即触发 | Exec |

### 快捷触发（无需认证）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/trigger/quick-report` | 快速简报 |
| POST | `/api/v1/trigger/tech-analyst` | 技术分析 |
| POST | `/api/v1/trigger/market-insight` | 商业洞察 |
| POST | `/api/v1/trigger/full-scan` | 全量扫描 |
| POST | `/api/v1/webhook` | 通用 Webhook |

---

## 定时任务配置示例

在 `clawctl/templates/schedules.yaml` 中配置：

```yaml
schedules:
  - id: daily-brief
    name: "每日早报"
    template_id: quick-report
    cron: "0 8 * * *"        # 每天 08:00
    timezone: Asia/Shanghai
    enabled: true
    notify:
      on_complete: true
      channel: dingtalk
```

---

## Telegram Bot 命令

```
/status              查看系统状态
/list [n]            列出最近 n 条任务
/templates           显示可用模板
/exec <模板>         触发任务（如 /exec quick-report）
/cancel <task_id>    取消任务
/help                帮助
直接发消息           透传给 OpenClaw 执行
```

---

## CLI 用法

```bash
python cli.py status                    # 查看状态
python cli.py trigger tech-analyst      # 触发任务
python cli.py exec "生成今日简报"        # 直接执行
python cli.py task <task_id>            # 查看任务详情
python cli.py list --status running      # 列出运行中任务
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `CLAWCTL_CONFIG` | 配置文件路径 | `config.yaml` |
| `CLAWCTL_TEMPLATES` | 模板 YAML 路径 | `clawctl/templates/schedules.yaml` |
| `OPENCLAW_API_KEY` | OpenClaw API Key | - |
| `DINGTALK_TOKEN` | 钉钉群机器人 Token | - |
| `DINGTALK_SECRET` | 钉钉加签密钥 | - |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | - |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | - |
| `WEBHOOK_SECRET` | Webhook 签名密钥 | - |

---

## 安全设计

- **三级 API Key**：Read / Exec / Admin
- **速率限制**：滑动窗口（默认 60次/分钟）
- **IP 白名单**：可选限制
- **操作审计**：所有操作记录日志
- **Webhook 签名**：HMAC-SHA256 验证
- **危险操作二次确认**：Admin 级操作需确认

---

## 部署方式

### Docker Compose（推荐）
```bash
cd /workspace/reports/oc-cross-device/docker

# 设置环境变量
export OPENCLAW_API_KEY="your-openclaw-key"
export DINGTALK_TOKEN="your-dingtalk-token"
export DINGTALK_SECRET="your-dingtalk-secret"

# 启动全部服务（clawctl + nginx + watchtower）
docker-compose up --build -d

# 查看日志
docker-compose logs -f clawctl

# 更新（Watchtower 自动处理）
docker-compose pull
```

> nginx 默认监听 80/443，提供 HTTPS 代理（证书放入 `./ssl/` 目录后取消注释 nginx.conf 中的 HTTPS server 块）。

### 直接运行
```bash
cd /workspace/reports/oc-cross-device/code
pip install flask apscheduler pyyaml requests httpx aiosqlite
OPENCLAW_API_KEY=xxx DINGTALK_TOKEN=xxx python server.py
```

---

## URL Scheme — 跨平台一键触发

注册 `clawctl://` 协议后，所有设备（iOS/Android/macOS/Windows）均可一键触发任务：

| 设备 | 注册方式 | 触发示例 |
|------|----------|----------|
| iOS | 快捷指令 App | `clawctl://run?template=quick_fetch&api_key=xxx` |
| Android | Tasker + HTTP Request | 通过 Intent 触发 |
| macOS | Automator App | 双击注册后即可 |
| Windows | `.reg` 注册表 | 双击导入 |
| 浏览器 | 书签栏脚本 | 一键触发 |

详细文档：
- [`快捷指令集成/iOS快捷指令集成指南.md`](快捷指令集成/iOS快捷指令集成指南.md)
- [`快捷指令集成/macOS-URL-Scheme注册指南.md`](快捷指令集成/macOS-URL-Scheme注册指南.md)

---

## API 文档（交互式）

启动服务后访问：
- Swagger UI: `http://localhost:8080/api/v1/docs`
- 快捷指令列表: `http://localhost:8080/api/v1/shortcuts`
- 健康检查: `http://localhost:8080/api/v1/health`
