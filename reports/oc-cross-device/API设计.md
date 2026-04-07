# OpenClaw 跨设备控制方案 - API 设计文档

## 1. API 概述

### 1.1 基本信息
- **基础 URL**: `http://<server>:8080/api/v1`
- **协议**: HTTP/1.1, HTTPS
- **认证方式**: API Key (Header: `X-API-Key`)
- **数据格式**: JSON

### 1.2 通用响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": "2026-03-19T12:00:00Z"
}
```

### 1.3 错误码
| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1000 | 参数错误 |
| 1001 | 缺少必需参数 |
| 2000 | 认证失败 |
| 2001 | API Key 无效 |
| 2002 | 权限不足 |
| 3000 | 资源不存在 |
| 4000 | 任务执行失败 |
| 5000 | 服务器内部错误 |

---

## 2. 任务管理 API

### 2.1 创建任务
**POST** `/tasks`

**请求头**:
```
X-API-Key: <your-api-key>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "快速报告",
  "action": "spawn",
  "agent": "tech-analyst",
  "params": {
    "scope": "brief"
  },
  "trigger": {
    "type": "manual"
  },
  "notify": {
    "on_start": true,
    "on_complete": true,
    "on_failed": true
  },
  "timeout": 300
}
```

**响应** (201 Created):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "task_abc123",
    "name": "快速报告",
    "status": "pending",
    "created_at": "2026-03-19T12:00:00Z",
    "result_url": "/api/v1/tasks/task_abc123"
  }
}
```

### 2.2 获取任务状态
**GET** `/tasks/{task_id}`

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "task_abc123",
    "name": "快速报告",
    "action": "spawn",
    "agent": "tech-analyst",
    "status": "completed",
    "created_at": "2026-03-19T12:00:00Z",
    "started_at": "2026-03-19T12:00:01Z",
    "completed_at": "2026-03-19T12:05:00Z",
    "duration": 239,
    "result": {
      "output": "任务执行完成",
      "summary": "获取到 15 条技术资讯"
    }
  }
}
```

### 2.3 取消任务
**DELETE** `/tasks/{task_id}`

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "task_abc123",
    "status": "cancelled"
  }
}
```

### 2.4 列出任务
**GET** `/tasks`

**查询参数**:
| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| status | string | 过滤状态 | - |
| limit | int | 返回数量 | 20 |
| offset | int | 偏移量 | 0 |

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 100,
    "tasks": [
      {
        "task_id": "task_abc123",
        "name": "快速报告",
        "status": "completed",
        "created_at": "2026-03-19T12:00:00Z"
      }
    ]
  }
}
```

---

## 3. 任务模板 API

### 3.1 获取模板列表
**GET** `/templates`

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "templates": [
      {
        "id": "quick_report",
        "name": "快速报告",
        "description": "生成当日简报",
        "action": "spawn",
        "agent": "tech-analyst",
        "params": {
          "scope": "brief"
        }
      },
      {
        "id": "full_scan",
        "name": "完整扫描",
        "description": "执行全量信息抓取",
        "action": "spawn",
        "agent": "info-fetcher",
        "params": {
          "full": true
        }
      }
    ]
  }
}
```

### 3.2 获取模板详情
**GET** `/templates/{template_id}`

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "quick_report",
    "name": "快速报告",
    "description": "生成当日简报",
    "action": "spawn",
    "agent": "tech-analyst",
    "params": {
      "scope": "brief"
    },
    "notify": {
      "on_start": true,
      "on_complete": true,
      "on_failed": true
    },
    "timeout": 300
  }
}
```

### 3.3 使用模板创建任务
**POST** `/templates/{template_id}/execute`

**请求体** (可选，覆盖模板参数):
```json
{
  "params": {
    "scope": "full"
  }
}
```

**响应** (201 Created):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "task_abc123",
    "status": "pending"
  }
}
```

---

## 4. Webhook API

### 4.1 Webhook 回调
**POST** `/webhook`

**请求头**:
```
Content-Type: application/json
X-Webhook-Signature: sha256=<signature>
```

**请求体**:
```json
{
  "event": "task.completed",
  "task_id": "task_abc123",
  "status": "completed",
  "result": {
    "output": "任务执行完成"
  },
  "timestamp": "2026-03-19T12:05:00Z"
}
```

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success"
}
```

### 4.2 注册 Webhook
**POST** `/webhooks`

**请求体**:
```json
{
  "url": "https://your-server.com/callback",
  "events": ["task.completed", "task.failed"],
  "secret": "your-webhook-secret",
  "enabled": true
}
```

**响应** (201 Created):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "webhook_id": "wh_abc123",
    "url": "https://your-server.com/callback",
    "events": ["task.completed", "task.failed"],
    "enabled": true
  }
}
```

---

## 5. 定时任务 API

### 5.1 创建定时任务
**POST** `/schedules`

**请求体**:
```json
{
  "name": "每日简报",
  "template_id": "quick_report",
  "cron": "0 9 * * *",
  "timezone": "Asia/Shanghai",
  "enabled": true,
  "notify": {
    "on_complete": true
  }
}
```

**响应** (201 Created):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "schedule_id": "sch_abc123",
    "name": "每日简报",
    "cron": "0 9 * * *",
    "next_run": "2026-03-20T09:00:00+08:00",
    "enabled": true
  }
}
```

### 5.2 列出定时任务
**GET** `/schedules`

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "schedules": [
      {
        "schedule_id": "sch_abc123",
        "name": "每日简报",
        "cron": "0 9 * * *",
        "next_run": "2026-03-20T09:00:00+08:00",
        "enabled": true
      }
    ]
  }
}
```

### 5.3 启用/禁用定时任务
**PATCH** `/schedules/{schedule_id}`

**请求体**:
```json
{
  "enabled": false
}
```

---

## 6. 系统状态 API

### 6.1 获取系统状态
**GET** `/status`

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "version": "1.0.0",
    "uptime": 86400,
    "openclaw": {
      "status": "running",
      "sessions": 3,
      "agents": 5
    },
    "tasks": {
      "pending": 2,
      "running": 1,
      "completed_today": 45
    },
    "system": {
      "cpu": 0.35,
      "memory": 0.62,
      "disk": 0.45
    }
  }
}
```

### 6.2 健康检查
**GET** `/health`

**响应** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-03-19T12:00:00Z"
}
```

---

## 7. 消息指令 API (for Bot)

### 7.1 处理钉钉消息
**POST** `/commands/dingtalk`

**请求体** (钉钉回调):
```json
{
  "msgtype": "text",
  "text": {
    "content": "执行快速报告"
  }
}
```

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "task_abc123",
    "message": "✅ 任务已创建: 快速报告\n任务ID: task_abc123"
  }
}
```

### 7.2 支持的命令
| 命令 | 说明 | 示例 |
|------|------|------|
| `执行 <模板名>` | 使用模板执行任务 | 执行 快速报告 |
| `状态` | 查看系统状态 | 状态 |
| `任务列表` | 查看最近任务 | 任务列表 |
| `帮助` | 显示帮助信息 | 帮助 |

---

## 8. 认证 API

### 8.1 生成 API Key
**POST** `/auth/keys`

**请求体**:
```json
{
  "name": "我的应用",
  "level": "execute",
  "expires_in": 2592000
}
```

**响应** (201 Created):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "key_id": "key_abc123",
    "api_key": "ock_xxxxxxxxxxxxx",
    "name": "我的应用",
    "level": "execute",
    "created_at": "2026-03-19T12:00:00Z",
    "expires_at": "2026-04-18T12:00:00Z"
  }
}
```

### 8.2 列出 API Key
**GET** `/auth/keys`

**响应** (200 OK):
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "keys": [
      {
        "key_id": "key_abc123",
        "name": "我的应用",
        "level": "execute",
        "created_at": "2026-03-19T12:00:00Z",
        "last_used": "2026-03-19T12:00:00Z"
      }
    ]
  }
}
```

### 8.3 撤销 API Key
**DELETE** `/auth/keys/{key_id}`

---

## 9. OpenClaw 集成 API

### 9.1 发送消息
**POST** `/openclaw/message`

**请求体**:
```json
{
  "channel": "dingtalk",
  "message": "Hello from remote!",
  "target": "user123"
}
```

### 9.2 触发 Agent
**POST** `/openclaw/spawn`

**请求体**:
```json
{
  "task": "分析最近AI领域的最新进展",
  "runtime": "subagent",
  "label": "remote-analysis"
}
```

### 9.3 获取会话列表
**GET** `/openclaw/sessions`

---

## 10. WebSocket (可选)

### 10.1 连接
**WS** `/ws`

**认证**: `ws://host:8080/ws?api_key=xxx`

### 10.2 消息格式
```json
{
  "type": "task_update",
  "data": {
    "task_id": "task_abc123",
    "status": "completed"
  }
}
```

---

*文档版本：v1.0*
*创建时间：2026-03-19*
