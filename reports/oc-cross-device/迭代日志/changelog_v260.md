# 迭代日志 (Changelog)

## v2.6.0 — 2026-04-08（NL Routes 完整实现）🆕 本次完成

> 主题：**NL 自然语言解析 HTTP 接口层完整落地，与 FastAPI 服务深度集成**

---

### 完成项

#### 1. NL Routes 完整实现 `handlers/nl_routes.py` 🆕

**文件位置**：`/workspace/reports/oc-cross-device/代码实现/handlers/nl_routes.py`

**提供 5 个 HTTP 端点**：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/nl` | 自然语言 → 自动解析执行（核心端点）|
| POST | `/api/v1/nl/preview` | 预览解析结果（不执行）|
| GET | `/api/v1/nl/intents` | 列出支持的 13 种意图及示例 |
| POST | `/api/v1/nl/batch` | 批量自然语言解析（最多 20 条）|
| GET | `/api/v1/nl/cmd` | **快捷指令专用入口**（GET 方法）|

**POST /api/v1/nl 请求示例**：
```bash
curl -X POST http://localhost:8081/api/v1/nl \
  -H "Content-Type: application/json" \
  -d '{"text": "帮我查一下今天有啥AI新闻", "channel": "dingtalk"}'

# 返回
{
  "success": true,
  "intent": "trigger_fetch",
  "confidence": 0.95,
  "agent": "info-fetcher",
  "plan": {...},
  "task_id": "nl-20260408-abc12345",
  "message": "🌐 收到！正在执行「trigger_fetch」\n📋 任务ID: nl-20260408-abc12345\n⏱ 完成后我会通知你~"
}
```

**NL → 执行映射**：
- `send_message` → 调用 `client.send_message()`
- `ask_question` → 调用 `client.spawn_agent()` 回答
- `trigger_fetch/report/analysis/scan/search` → 调用 `client.spawn_agent()` + 钉钉通知
- `query_status` → 调用 `client.get_status()` 格式化返回
- `query_history` → 查询 SQLite 历史任务
- `cancel_task` → `task_mgr.cancel_task()`
- `pause/resume_schedule` → 返回确认消息

**快捷指令 GET 端点**：
```
# URL Scheme 格式（可直接在快捷指令中调用）
http://localhost:8081/api/v1/nl/cmd?q=生成今日技术简报&channel=dingtalk&api_key=sk-xxx
```

#### 2. FastAPI 集成 `fastapi_server/main.py` ✅

**修改点**：
- 导入 `nl_router` 和 `set_nl_components`
- `app.include_router(nl_router)` 注册 NL 路由
- `lifespan` 启动时调用 `set_nl_components()` 注入 `_task_mgr / _notify_mgr / _gateway_client / _auth_mgr`
- API 版本升级至 **v2.5.0**，title 更新

#### 3. API Key 权限隔离

- 所有端点强制认证（`authorization` header）
- 审计日志自动记录：`nl_parse` 事件，含意图/置信度/原始文本
- 快捷指令端点支持独立 `api_key` 参数（可配置 `NL_CMD_KEY` 环境变量）

#### 4. 置信度路由

| 置信度 | 行为 |
|--------|------|
| ≥ 0.4 + 已知意图 | 正常执行 |
| < 0.4 或 `unknown` | 返回友好提示，引导用户换说法 |

---

### 调用链路

```
用户输入（手机/Siri/快捷指令）
        ↓
POST /api/v1/nl {text: "生成今日技术简报"}
        ↓
NLInterpreter.parse() → TaskPlan(intent=trigger_report, conf=0.95)
        ↓
_execute_plan() → OpenClawClient.spawn_agent()
        ↓
NotifyManager.send("dingtalk", 确认消息)
        ↓
任务异步执行 → 完成后钉钉推送结果
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
client.spawn_agent(agent="info-fetcher")
       ↓
钉钉推送确认 → Agent执行 → 钉钉推送结果 ✅
```

#### 场景 2：快捷指令直接 GET（无需 body）'
```
快捷指令 App → 打开 URL
URL: http://localhost:8081/api/v1/nl/cmd?q=生成今日商业简报&channel=dingtalk
       ↓
GET /api/v1/nl/cmd → nl_execute() → 执行
```

#### 场景 3：调试/预览（不触发实际操作）
```bash
curl -X POST http://localhost:8081/api/v1/nl/preview \
  -H "Content-Type: application/json" \
  -d '{"text": "查一下最新的推荐系统论文"}'

# 返回解析结果，不执行任何操作
```

---

## v2.5.0 — 2026-04-07（自然语言任务解析器 NL Interpreter）✅

> 主题：**移动端核心体验 — 一句话说清楚要什么，NL Interpreter 自动解析 + 执行**

（详见上方 changelog_v150.md）
