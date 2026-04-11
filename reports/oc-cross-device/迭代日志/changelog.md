# 迭代日志 (Changelog)

## v2.10.0 — 2026-04-11（定时任务 UI + 模板管理 + Schedule API 完整 CRUD）🆕 本次完成

> 主题：**Web Admin v3 补全定时任务和模板管理 UI，FastAPI Schedule CRUD 接口全对齐**

---

### 核心升级

**1. Schedule API 全 CRUD（`fastapi_main.py`）：**

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/schedules` | 列出所有定时任务（增强：返回完整 job 信息） |
| POST | `/api/v1/schedules` | 创建定时任务（新增） |
| DELETE | `/api/v1/schedules/{id}` | 删除定时任务（新增） |
| PATCH | `/api/v1/schedules/{id}/toggle` | 切换启用/暂停状态（新增） |
| POST | `/api/v1/schedules/{id}/trigger` | 立即触发（原有，已修复用 `trigger_now`） |

- 修复：`list_schedules` 不再访问不存在的 `.jobs` 属性，改用 `scheduler.list_jobs()`
- 修复：`trigger_schedule` 改用 `scheduler.get_job()` + `scheduler.trigger_now()`

**2. Templates API 修复：**
- `GET /api/v1/templates` — 修复不存在的 `list_templates()` 方法，改为 `template_loader.list()`
- `GET /api/v1/templates/{id}` — 新增，用 `template_loader.get(id)` 获取单条模板

**3. Web Admin v3 新增两个 Tab：**

#### ⏰ 定时任务 Tab（新增）
- 定时任务列表：显示名称、cron 表达式、下次/上次运行时间、累计次数
- 状态指示：✅ 已启用 / ⏸ 已暂停
- 一键操作：▶ 立即执行 / ⏸/▶ 暂停或启用 / ✕ 删除
- 新建表单：选择模板 + cron 表达式 + 通知渠道 + 完成后通知开关
- Cron 预设快捷按钮：每天 9:00 / 每天 18:00 / 工作日 9:00 / 每周一 9:00 / 每 6 小时 / 每 30 分钟
- Cron 表达式参考说明面板

#### 📋 模板管理 Tab（新增）
- 模板卡片网格：点击查看详情
- 详情面板：显示模板名称、描述、action 类型标签、通知配置、完整 params JSON
- 快捷执行：直接在详情面板点击"🚀 立即执行此模板"（NL 接口）
- 内置模板提示：quick-report / tech-analyst / market-insight / full-scan

**4. 顶部导航 + 底部 Bar 同步升级：**
- 6 个 Tab：⚡任务 / 📊监控 / 🔀流程 / ⏰定时 / 📋模板 / 🔌插件

---

### Phase 2 进度总览

| 功能 | 状态 | 备注 |
|------|------|------|
| 任务模板系统 | ✅ | `core/template_loader.py` + 📋模板Tab |
| 定时任务调度 | ✅ | `core/scheduler.py` + ⏰定时Tab + CRUD API |
| Web Admin 界面 | ✅ | React SPA v3，6 Tab 全覆盖 |

---

## v2.9.0 — 2026-04-10（FastAPI 原生层 + Plugin 系统 + Web Admin v3）🆕 本次完成

> 主题：**FastAPI 完整异步化 + 插件生态 + React SPA 控制台 — 打造可持续演进的开放平台**
>
> 详见 [changelog_v290.md](./changelog_v290.md)

---

### 核心升级

**FastAPI Server（新建 `clawctl/fastapi_main.py`）：**
- 全链路 async/await，告别 Flask 同步阻塞
- 原生 WebSocket + SSE 双通道，实时推送更稳定
- 自动 OpenAPI 文档（访问 `/docs`）
- Pydantic 自动参数校验 + 类型提示
- Lifespan 生命周期管理（启动初始化/关闭清理）

**Plugin 系统（新建 `core/plugin_manager.py`）：**
- 用户通过 API 动态注册自定义意图 + handler
- 内置 4 个快捷命令插件（status/list/help/ping）
- 插件市场 4 款插件可一键安装（job-hunter/stock-watcher/meeting-notes/dev-ops）
- NL Interpreter 插件扩展（`core/nl_plugin_ext.py`）

**Web Admin v3（新建 `web_admin/v3/index.html`）：**
- React 18 SPA，移动端优先
- 4 个 Tab：⚡任务 / 📊监控 / 🔀DAG / 🔌插件
- ECharts 仪表盘实时 CPU/内存
- Canvas DAG 流程图可视化
- PWA 支持（添加至主屏幕）

**启动方式：**
```bash
cd /workspace/reports/oc-cross-device/code
/app/.venv/bin/pip install -r fastapi_requirements.txt
OPENCLAW_API_KEY=xxx /app/.venv/bin/python clawctl/fastapi_main.py --port 8081
# 访问
open http://localhost:8081/admin_v3/
open http://localhost:8081/docs   # OpenAPI 文档
open http://localhost:8081/ws    # WebSocket 端点
```

---

## v2.8.0 — 2026-04-09（iOS/Android 快捷指令深度集成）🆕 本次完成

> 主题：**手机上一句话，OpenClaw 立刻执行 — iOS 快捷指令 × Siri 语音触发**

---

### 核心能力：移动端零门槛控制

**为什么需要快捷指令集成？**

现有控制方式的体验断层：
- ✅ Web 界面：功能完整，但需要打开浏览器
- ✅ 钉钉：适合聊天，复杂操作繁琐
- ❌ 随手执行："Hey Siri，帮我生成今日简报" — 无法实现

**v2.8.0 解决的核心问题：**
- 用户对 Siri 说 **"AI简报"** → 触发 OpenClaw 执行任务 → 钉钉收到结果
- 全程无需打开任何 App，无需打字
- 固定任务一键导入 iOS 快捷指令 App

---

### 新增文件

#### `handlers/shortcuts.py` 🆕 (~280行)

**快捷指令模板系统 + clawctl:// URL Scheme 解析**

| 功能 | 说明 |
|------|------|
| 13 个预设快捷指令模板 | 覆盖日常任务、快速查询、个性化分析三类 |
| `ShortcutTemplate` 数据类 | 模板定义（名称/图标/颜色/URL/标签） |
| iOS Shortcut URL 生成器 | `generate_ios_url_scheme()` 直接生成 iOS 可用 URL |
| clawctl:// URL 解析 | 支持 `clawctl://run`、`message`、`status`、`schedule` |
| 快捷指令库导出 | JSON/iOS 两种格式，支持前端/App 直接使用 |

**预设模板一览：**

```
📋 日常任务（5个）
  - 📋 生成今日简报      🌐 AI热点新闻
  - 🔬 技术前沿扫描      📊 市场动态洞察
  - 🚀 全面信息扫描

⚡ 快速操作（3个）
  - 💡 查看系统状态      📜 最近任务记录
  - ⏳ 待处理任务

🎯 个性化分析（5个）
  - 🎯 推荐系统深度分析  🧠 大模型最新进展
  - 💼 推荐算法就业市场  📚 本周论文速递
```

#### `handlers/shortcuts_routes.py` 🆕 (~270行)

**FastAPI/Flask HTTP 路由 — 快捷指令专用端点**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/shortcuts` | **快捷指令库主端点**（iOS"获取内容"动作用） |
| GET | `/api/v1/shortcuts/library` | 导出完整库 JSON（支持 format=ios） |
| GET | `/api/v1/shortcuts/mobile` | 移动端专用格式（intent_filter） |
| GET | `/api/v1/shortcuts/{id}` | 单个快捷指令详情 |
| POST | `/api/v1/shortcuts/parse` | 解析 clawctl:// URL |
| **GET** | **`/api/v1/shortcuts/cmd`** | **🚀 核心端点（iOS 快捷指令专用）** |
| GET | `/api/v1/shortcuts/share/{id}` | 生成分享链接 |

**GET /shortcuts/cmd 响应示例：**
```json
{
  "success": true,
  "intent": "trigger_report",
  "confidence": 0.95,
  "agent": "tech-analyst",
  "task_id": "nl-20260409-abc12345",
  "message": "✅ 收到！正在执行「trigger_report」\n📋 任务ID: nl-20260409-abc12345\n⏱ 完成后我会通知你~"
}
```

#### `快捷指令集成/iOS-Shortcuts集成指南.md` 🆕

**完整的 iOS 快捷指令集成文档：**
- 3 步快速配置指南
- 13 个预设快捷指令导入说明
- Siri 语音触发配置
- clawctl:// URL Scheme 协议规范
- 常见错误排查表
- 安全配置建议

---

### 实现细节

#### iOS 快捷指令 URL 格式

```
# 标准格式（iOS 快捷指令"获取内容"动作）
GET https://your-server/api/v1/shortcuts/cmd?q=生成今日技术简报&channel=dingtalk

# 模板 ID 格式（精确匹配预设快捷指令）
GET https://your-server/api/v1/shortcuts/cmd?template=quick_report&channel=dingtalk

# 解析模式（只解析不执行，用于调试）
GET https://your-server/api/v1/shortcuts/cmd?q=生成AI新闻&intent_only=true
```

#### NL Executor 集成

```python
# shortcuts_routes.py — 快捷指令 → NL Executor
if _nl_executor is None:
    return {"success": True, "note": "NL Routes 未启动"}

result = _nl_executor.execute(nl_text, channel=channel)
return jsonify(result)
```

#### server.py 注册

```python
# 在 NL Routes 注册后追加
from clawctl.handlers.shortcuts_routes import shortcuts_bp, init_shortcuts_routes
init_shortcuts_routes(nl_executor)  # 注入 NL Executor
app.register_blueprint(shortcuts_bp)
logger.info("📱 快捷指令路由已注册 (/api/v1/shortcuts/*) — iOS/Android 快捷指令集成")
```

---

### Phase 3 进度总览

| 功能 | 状态 | 备注 |
|------|------|------|
| 多平台支持（钉钉） | ✅ | `dingtalk_handler.py` 完整 |
| 多平台支持（Telegram） | ✅ | `telegram_bot.py` 283行 |
| 多平台支持（微信） | ✅ | `wechat_handler.py` 639行 |
| 自然语言解析 | ✅ | `nl_interpreter.py` + `nl_routes.py` |
| LLM 增强解析 | ✅ | `llm_resolver.py` (v2.7.0) |
| **快捷指令集成** | **✅ 本次** | **v2.8.0** |
| 语音控制 | ✅ | `voice_handler.py` 535行 + `voice_routes.py` 216行 |
| SSE 实时推送 | ✅ | `sse_handler.py` 313行 |
| DAG 任务流 | ✅ | `task_dag.py` |
| iOS App / 小程序 | 🔲 规划中 | 需原生开发 |

---

## v2.7.0 — 2026-04-08（LLM驱动的深度语义解析）🆕 本次完成

> 主题：**当规则引擎"看不懂"时，GLM-4 自动顶上 — 复杂指令零门槛解析**
>
> 详见 [changelog_v270.md](./changelog_v270.md)

---

## v2.6.0 — 2026-04-08（NL Routes 完整实现）🆕 本次完成

> 主题：**NL 自然语言解析 HTTP 接口层完整落地，与 FastAPI 服务深度集成**
>
> **本次完成**：新建 `handlers/nl_routes.py`，提供 5 个 NL HTTP 端点并与 FastAPI 服务集成。详见 [changelog_v260.md](./changelog_v260.md)

---

## v2.5.0 — 2026-04-07（自然语言任务解析器 NL Interpreter）✅

> 主题：**移动端核心体验 — 一句话说清楚要什么，NL Interpreter 自动解析 + 执行**

---

### 完成项

#### 1. NL Interpreter 核心 `core/nl_interpreter.py` 🆕

**意图识别（13 种意图全覆盖）**
- `Intent` 枚举：trigger_report / trigger_scan / trigger_analysis / trigger_fetch / trigger_search / send_message / ask_question / query_status / query_task / query_history / cancel_task / pause_schedule / resume_schedule
- 多层级解析：精确匹配（置信度 0.95）→ 模糊匹配（关键词重叠度 0.5+）→ 问号推断（0.7）
- 零代码扩展：新增意图只需往 `INTENT_PATTERNS` 字典添加关键词

**参数抽取**
- Agent 映射：`info-fetcher` / `tech-analyst` / `market-insight` / `quick-report`
- 时间词解析：现在/今天/明天/后天/下周，自动解析为 `datetime`
- 技术关键词提取：大模型/RAG/Agent/MoE 等 30+ 关键词自动识别
- 通知渠道推断：`发钉钉` / `只通知我` 等口语识别

**Urgency 紧急度识别**
- `ASAP`：立刻/马上/立即/十万火急
- `HIGH`：尽快/快点
- `LOW`：有空/慢慢来/不急
- 影响任务优先级和推送表情

**NLExecutor — 解析结果执行器**
- 意图 → 执行动作一体化（execute 接口）
- `ASK_QUESTION` → 自动 spawn agent 回答
- `QUERY_STATUS` → 格式化状态输出
- `UNKNOWN`（置信度 < 0.4）→ 友好提示，不乱执行

**内置模式库**
```python
INTENT_PATTERNS   # 意图关键词（中文全覆盖）
AGENT_KEYWORDS    # Agent 别名映射
URGENCY_PATTERNS  # 紧急度关键词
TIME_PATTERNS     # 时间词正则 + 解析函数
```

---

#### 2. NL 路由 `handlers/nl_routes.py` 🆕

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/nl` | 自然语言 → 自动解析执行 |
| POST | `/api/v1/nl/preview` | 预览解析结果（不执行）|
| GET | `/api/v1/nl/intents` | 列出支持的 13 种意图及示例 |
| POST | `/api/v1/nl/batch` | 批量自然语言解析 |

**POST /api/v1/nl 示例**
```bash
curl -X POST http://localhost:18789/api/v1/nl \
  -H "Content-Type: application/json" \
  -d '{"text": "帮我查一下今天有啥AI新闻", "channel": "dingtalk"}'

# 返回
{
  "success": true,
  "intent": "trigger_fetch",
  "task_id": "nl-20260407-xxx",
  "message": "收到！正在执行「trigger_fetch」\n📋 任务ID: nl-20260407-xxx\n⏱ 完成后我会通知你~"
}
```

---

### 典型使用场景

#### 场景 1：手机快捷指令 + NL
```
用户说："Hey Siri，帮我查AI新闻"
       ↓
快捷指令 → POST /api/v1/nl → {"text": "帮我查AI新闻"}
       ↓
NL Interpreter 识别为 trigger_fetch，置信度 0.95
       ↓
TaskManager 自动 spawn info-fetcher
       ↓
完成后钉钉推送 ✅
```

#### 场景 2：微信/Telegram 文字输入
```
用户发消息："生成今日简报"
       ↓
Telegram/WeChat Handler → NL Interpreter
       ↓
识别为 trigger_report，scope=daily
       ↓
执行 quick-report 模板，钉钉通知
```

#### 场景 3：预览解析（调试/开发）
```bash
# 不执行，只看解析结果
curl -X POST http://localhost:18789/api/v1/nl/preview \
  -d '{"text": "帮我分析一下RAG的技术趋势"}'

# 返回
{
  "intent": "trigger_analysis",
  "confidence": 0.95,
  "agent": "tech-analyst",
  "params": {"topics": ["RAG", "检索增强"], "scope": "technical"},
  "urgency": "normal"
}
```

---

### 架构图（v2.5.0 新增 NL 层）

```
                    ┌─────────────────────────────┐
                    │    NL Interpreter (新增)     │
                    │  ┌──────────────────────┐   │
                    │  │  Intent Recognition  │   │
                    │  │  精确/模糊/语义三层   │   │
                    │  └──────────┬───────────┘   │
                    │  ┌──────────▼───────────┐   │
                    │  │   Parameter Extraction│  │
                    │  │  Agent/Time/Urgency  │   │
                    │  └──────────┬───────────┘   │
                    └──────────────┼───────────────┘
                                   │ ParsedIntent
                    ┌──────────────▼───────────────┐
                    │      NL Executor              │
                    │  execute() → 意图路由          │
                    │  ASK_QUESTION → spawn agent  │
                    │  QUERY_STATUS → format output │
                    │  TRIGGER_* → TaskManager     │
                    └──────────────────────────────┘
```

---

### 代码变更

| 文件 | 变更 |
|------|------|
| `core/nl_interpreter.py` | 新增 ~400 行，NL 解析引擎 |
| `handlers/nl_routes.py` | 新增 ~150 行，REST API |
| `server.py` | 注入 NL 模块 + 注册路由 |

---

### 后续迭代方向

- v2.6.0：LLM 驱动的深度语义解析（GPT-4o / GLM-4 增强）
- v2.6.0：对话式多轮任务（上下文记忆）
- v2.7.0：Plugin 系统（自定义意图 + 参数 schema）

---

## v2.4.0 — 2026-04-06（多实例管理 · 实时监控 · 智能告警）✅

> 主题：**分布式 OpenClaw 集群管理 — 多实例路由 + 全维度监控 + 智能告警**

---

### 完成项

#### 1. 多实例管理器 `core/multi_instance.py` 🆕

**InstanceInfo — 实例元数据**
- `id` / `name` / `base_url` / `api_key` / `group` / `tags` / `max_concurrent`
- 运行时状态：`status` / `active_tasks` / `avg_response_time` / `failure_rate`

**MultiInstanceManager — 全局管理器**
- `register_instance()` / `unregister_instance()` / `update_instance()` — 实例 CRUD
- `get_best_instance()` — 三种路由策略自动选择最优实例
  - `ROUND_ROBIN`：轮询分配，公平分发
  - `LEAST_LOADED`：选择当前负载最低的实例
  - `FAILOVER`：主备切换，优先主实例，自动跳过故障节点
- `execute_task()` — 在最优实例上自动执行任务
- `start_health_check()` / `stop_health_check()` — 后台心跳检测（默认 15s 间隔）
- `_run_health_check()` → `_process_health_result()` — 批量健康检查，自动更新状态
- 健康状态回调：`on_unhealthy(instance_id, error)` / `on_recovered(instance_id)`
- `get_multi_instance_manager()` — 全局单例

**CircuitBreaker — 熔断器**
- 连续 `failure_threshold=3` 次失败 → 熔断器打开，实例摘除
- `recovery_timeout=60s` 后进入半开状态，允许 1 个测试请求
- 测试成功自动恢复；再次失败重新熔断

**MultiInstanceClient — 单实例客户端**
- 绑定到特定实例，线程安全
- `get_status()` / `send_message()` / `spawn_agent()` / `execute_task()`
- `execute_task()` 自动递增/递减 `active_tasks` 计数器

**实例状态流转**
```
UNKNOWN → HEALTHY（连续健康）
UNKNOWN → FAILED（熔断打开）
HEALTHY → DEGRADED（响应时间 > 3s 或 错误率 > 30%）
DEGRADED → HEALTHY（恢复）
DEGRADED → FAILED（熔断打开）
FAILED → HEALTHY（熔断恢复后测试成功）
```

---

#### 2. 实时监控与告警系统 `core/monitor.py` 🆕

**MonitoringManager — 监控核心**
- 后台线程每 5s 收集一次指标（可配置间隔）
- 滑动窗口存储 1 小时数据（720 个点 @ 5s）
- 支持指标：`cpu_percent` / `memory_percent` / `request_count` / `error_rate` / `avg_response_ms` / `active_tasks` / `api_latency_p95`

**告警引擎**
- `AlertRule`：可配置指标 + 条件（gt/lt/gte/lte/eq）+ 阈值 + 严重程度 + 冷却时间
- 告警触发时执行回调（多通道通知）
- `acknowledge_alert()` — 人工确认
- `get_alert_history()` — 历史告警查询

**数据查询**
- `get_snapshot()` — 当前系统快照（CPU/内存/磁盘/OpenClaw指标/API QPM）
- `get_series(metric, minutes)` — 任意指标时序数据
- `get_dashboard_summary()` — Dashboard 全量汇总（快照 + 10分钟序列 + 告警 + 规则）

**告警预置规则**
```python
# CPU 持续 > 80% → warning
# CPU 持续 > 95% → critical
# 内存 > 85% → warning
# 内存 > 95% → critical
# 错误率 > 5% → warning
# P95 延迟 > 5000ms → warning
# 活跃任务 > 10 → info（通知）
```

---

#### 3. 监控 API 路由 `handlers/monitor_routes.py` 🆕

**指标查询**
```
GET  /api/v1/monitor/snapshot          系统快照
GET  /api/v1/monitor/series/{metric}  指标时序（?minutes=10）
GET  /api/v1/monitor/dashboard         Dashboard 全量汇总
GET  /api/v1/monitor/current/{metric}  当前指标值
```

**告警管理**
```
GET    /api/v1/monitor/alerts/rules       列出告警规则
POST   /api/v1/monitor/alerts/rules       添加告警规则
DELETE /api/v1/monitor/alerts/rules/{id}   删除规则
GET    /api/v1/monitor/alerts/active      当前告警
GET    /api/v1/monitor/alerts/history      告警历史
POST   /api/v1/monitor/alerts/{rule_id}/ack  确认告警
```

**多实例管理**
```
GET    /api/v1/monitor/instances           列出实例
POST   /api/v1/monitor/instances           注册实例
GET    /api/v1/monitor/instances/{id}      实例详情
PATCH  /api/v1/monitor/instances/{id}      更新实例
DELETE /api/v1/monitor/instances/{id}       注销实例
POST   /api/v1/monitor/instances/health-check  手动触发健康检查
POST   /api/v1/monitor/instances/select    策略选择最优实例
```

---

#### 4. 多实例 + 监控集成到 server.py ✅

- `init_multi_instance_manager()` 初始化
- `init_monitoring()` + `get_monitoring_manager()` 初始化
- 健康检查 → 自动更新 OpenClaw 指标注入到监控
- 告警回调 → 自动推送钉钉/Telegram 通知
- 告警回调 → 更新 OpenClaw 活跃任务数（多实例汇聚）
- `monitor_bp` 注册到 Flask app

---

### 新增 API

```
GET  /api/v1/monitor/snapshot                    系统快照
GET  /api/v1/monitor/series/{metric}            指标时序
GET  /api/v1/monitor/dashboard                 Dashboard 汇总
GET  /api/v1/monitor/current/{metric}           当前值
GET  /api/v1/monitor/alerts/rules               告警规则
POST /api/v1/monitor/alerts/rules               添加规则
DELETE /api/v1/monitor/alerts/rules/{id}        删除规则
GET  /api/v1/monitor/alerts/active              当前告警
GET  /api/v1/monitor/alerts/history             告警历史
POST /api/v1/monitor/alerts/{id}/ack            确认告警
GET  /api/v1/monitor/instances                  列出实例
POST /api/v1/monitor/instances                  注册实例
GET  /api/v1/monitor/instances/{id}             实例详情
PATCH /api/v1/monitor/instances/{id}            更新实例
DELETE /api/v1/monitor/instances/{id}           注销实例
POST /api/v1/monitor/instances/health-check    手动健康检查
POST /api/v1/monitor/instances/select          策略选择
```

---

### 典型使用场景

#### 场景 1：注册多 OpenClaw 实例
```bash
# 注册主实例
curl -X POST http://localhost:18789/api/v1/monitor/instances \
  -H "Content-Type: application/json" \
  -d '{
    "id": "prod-beijing",
    "name": "生产-北京",
    "base_url": "http://192.168.1.10:18789",
    "api_key": "sk-xxx",
    "group": "production",
    "tags": ["primary", "fast"],
    "max_concurrent": 10
  }'

# 注册灾备实例
curl -X POST http://localhost:18789/api/v1/monitor/instances \
  -d '{"id": "prod-ningbo", "name": "生产-宁波", ...}'
```

#### 场景 2：智能路由执行任务
```python
from clawctl.core.multi_instance import get_multi_instance_manager, LoadBalanceStrategy

mgr = get_multi_instance_manager()
# 自动选最优实例执行（Failover 策略）
result = mgr.execute_task(
    task_name="tech-analyst",
    task_params={"scope": "brief"},
    group="production",
    strategy=LoadBalanceStrategy.FAILOVER,
)
```

#### 场景 3：添加 CPU 告警
```bash
curl -X POST http://localhost:18789/api/v1/monitor/alerts/rules \
  -d '{
    "id": "high-cpu",
    "name": "CPU 过高",
    "metric": "cpu_percent",
    "condition": "gt",
    "threshold": 80,
    "severity": "warning",
    "channels": ["dingtalk"],
    "cooldown": 300
  }'
```

#### 场景 4：查看 Dashboard
```bash
curl http://localhost:18789/api/v1/monitor/dashboard | jq .
```

---

### 架构图（v2.4.0）

```
                          ┌──────────────────────────────────────────┐
                          │          clawctl Server                  │
                          │  ┌────────────┐  ┌─────────────────┐   │
                          │  │  多实例    │  │    监控系统      │   │
                          │  │  Manager   │  │   Monitoring    │   │
                          │  └──────┬─────┘  └────────┬────────┘   │
                          │         │                 │             │
                          │    ┌────▼────┐       ┌───▼────┐        │
                          │    │Circuit  │       │Alert   │        │
                          │    │Breaker  │       │Engine  │        │
                          │    └────┬────┘       └───┬────┘        │
                          │         │               │              │
                          │    ┌────▼────────────────▼────┐        │
                          │    │    统一通知通道           │        │
                          │    │ (钉钉/邮件/Telegram)    │        │
                          │    └──────────────────────────┘        │
                          └──────────────────────────────────────────┘
                                       │            │
                         ┌─────────────▼──┐   ─────▼──────────┐
                         │  OpenClaw 实例1 │   │ OpenClaw 实例2 │
                         │  (北京 · 主)    │   │ (宁波 · 备)    │
                         └─────────────────┘   └────────────────┘
```

---

## v2.3.0 — 2026-04-06（微信公众号 + 语音控制）✅ 完成

> 主题：**微信订阅号接入 + 全平台语音控制**

（详见上方 changelog_v150.md）
