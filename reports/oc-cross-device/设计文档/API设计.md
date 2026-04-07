# OpenClaw 跨设备远程控制方案 — API 设计

## 1. API 概览

- **Base URL**：`http://localhost:8080/api/v1`
- **认证方式**：`Authorization: Bearer <API_KEY>` 请求头
- **Content-Type**：`application/json`
- **返回格式**：统一 JSON 响应

---

## 2. 认证与权限

### 2.1 请求认证

```http
Authorization: Bearer sk-xxxxx-EXECUTE
```

### 2.2 权限等级

| 等级 | 值 | 可调用接口 |
|------|----|-----------|
| `read_only` | 10 | `GET /status`, `GET /tasks`, `GET /templates` |
| `execute` | 20 | 以上 + `POST /tasks` |
| `admin` | 30 | 以上 + `POST /templates`, `DELETE /tasks/*`, `PUT /config` |

### 2.3 错误响应

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing API key"
  }
}
```

| HTTP Code | 错误码 | 说明 |
|-----------|--------|------|
| 400 | `INVALID_REQUEST` | 请求参数错误 |
| 401 | `UNAUTHORIZED` | 未提供或无效 Key |
| 403 | `FORBIDDEN` | Key 权限不足 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 429 | `RATE_LIMITED` | 请求过于频繁 |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 |

---

## 3. 任务接口

### 3.1 创建任务

```
POST /api/v1/tasks
```

**请求体**：

```json
{
  "template": "daily_brief",       // 模板名称（二选一）
  "params": {                      // 模板参数
    "scope": "tech"
  },
  "trigger": "manual",             // 触发来源（可选，默认 manual）
  "notify": true,                  // 执行完成后是否推送（可选，默认 true）
  "notify_channels": ["dingtalk"]  // 推送渠道（可选，默认配置）
}
```

或者直接指定任务：

```json
{
  "task": {
    "name": "my_task",
    "action": "spawn",
    "agent": "tech-analyst",
    "params": {
      "scope": "brief"
    }
  },
  "notify": true
}
```

**响应** `201 Created`：

```json
{
  "task_id": "t_20260328_001",
  "name": "daily_brief",
  "status": "queued",
  "created_at": "2026-03-28T17:22:00+08:00",
  "estimated_duration": 60
}
```

### 3.2 查询任务状态

```
GET /api/v1/tasks/{task_id}
```

**响应**：

```json
{
  "task_id": "t_20260328_001",
  "name": "daily_brief",
  "status": "completed",
  "progress": {
    "current": 3,
    "total": 3
  },
  "created_at": "2026-03-28T17:22:00+08:00",
  "started_at": "2026-03-28T17:22:01+08:00",
  "completed_at": "2026-03-28T17:23:15+08:00",
  "result": {
    "summary": "生成了3条技术简报",
    "output_file": "/workspace/reports/daily_20260328.md"
  },
  "notify_sent": true
}
```

**任务状态枚举**：

| 状态 | 说明 |
|------|------|
| `queued` | 等待执行 |
| `running` | 执行中 |
| `completed` | 已完成 |
| `failed` | 执行失败 |
| `cancelled` | 已取消 |

### 3.3 取消任务

```
DELETE /api/v1/tasks/{task_id}
```

**响应** `200 OK`：

```json
{
  "task_id": "t_20260328_001",
  "status": "cancelled"
}
```

### 3.4 列出任务

```
GET /api/v1/tasks?status=running&limit=20&offset=0
```

**响应**：

```json
{
  "tasks": [...],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

---

## 4. 模板接口

### 4.1 获取模板列表

```
GET /api/v1/templates
```

**响应**：

```json
{
  "templates": [
    {
      "name": "daily_brief",
      "display_name": "每日简报",
      "description": "生成当日 AI 领域简报",
      "params_schema": {
        "scope": {
          "type": "string",
          "enum": ["tech", "business", "all"],
          "default": "all"
        }
      },
      "notify_on_complete": true
    },
    {
      "name": "full_scan",
      "display_name": "全量扫描",
      "description": "执行全量信息抓取",
      "params_schema": {}
    }
  ]
}
```

### 4.2 创建/更新模板（Admin）

```
POST /api/v1/templates
PUT /api/v1/templates/{name}
```

**请求体**：

```json
{
  "display_name": "每日简报",
  "description": "生成当日 AI 领域简报",
  "action": "spawn",
  "agent": "tech-analyst",
  "params": {
    "scope": "all"
  },
  "notify_on_complete": true
}
```

### 4.3 删除模板（Admin）

```
DELETE /api/v1/templates/{name}
```

---

## 5. 状态接口

### 5.1 获取系统状态

```
GET /api/v1/status
```

**响应**：

```json
{
  "server": {
    "version": "1.0.0",
    "uptime": 86400,
    "python_version": "3.11"
  },
  "openclaw": {
    "gateway_reachable": true,
    "active_sessions": 2,
    "agents": [
      {"name": "tech-analyst", "status": "idle"},
      {"name": "info-fetcher", "status": "running"}
    ]
  },
  "tasks": {
    "queued": 0,
    "running": 1,
    "completed_today": 15,
    "failed_today": 1
  }
}
```

---

## 6. Webhook 接口

### 6.1 通用 Webhook 入口

```
POST /api/v1/webhook
```

**认证方式**：Query 参数或 Header 签名

```http
POST /api/v1/webhook?secret=WEBHOOK_SECRET
```

**请求体**（IFTTT/快捷指令标准格式）：

```json
{
  "template": "daily_brief",
  "params": {}
}
```

### 6.2 钉钉专用 Webhook

```
POST /api/v1/webhook/dingtalk
```

钉钉自定义机器人加签签名校验自动处理。

---

## 7. 快捷指令 / IFTTT 触发格式

### 7.1 URL 触发（GET）

```
GET /api/v1/tasks/trigger?name=daily_brief&scope=tech
```

### 7.2 快捷指令配置

```
URL: https://your-domain.com/api/v1/tasks/trigger
Method: POST
Headers:
  Authorization: Bearer sk-xxxxx-EXECUTE
  Content-Type: application/json
Body:
  {"template": "daily_brief", "params": {"scope": "tech"}}
```

---

## 8. WebSocket（实时推送）

```
WS /api/v1/ws?api_key=sk-xxxxx
```

**推送消息示例**：

```json
{"type": "task_update", "task_id": "t_20260328_001", "status": "completed"}
{"type": "task_progress", "task_id": "t_20260328_001", "progress": 2, "total": 3}
{"type": "openclaw_alert", "message": "tech-analyst 执行失败"}
```

---

## 9. 操作日志

```
GET /api/v1/audit_logs?from=2026-03-28&to=2026-03-29&limit=100
```

**响应**：

```json
{
  "logs": [
    {
      "id": 1001,
      "timestamp": "2026-03-28T17:22:00+08:00",
      "api_key_name": "手机执行Key",
      "api_key_level": "execute",
      "action": "task.create",
      "resource": "daily_brief",
      "result": "success",
      "ip": "12.34.56.78"
    }
  ],
  "total": 1
}
```
