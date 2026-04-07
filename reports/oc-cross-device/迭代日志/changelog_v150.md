# 迭代日志 (Changelog)

## v1.5.0 — 2026-04-02（定时 Agent 触发）

> 主题：**SQLite 持久化 + SSE 实时推送 + 移动端 Web Admin 全新改版**

### 完成项

**SQLite 任务历史数据库 `core/database.py`** 🆕
- 线程安全 `TaskDatabase` 类（WAL 模式，支持高并发）
- 任务历史表（TaskHistory）：完整字段，含 params/result JSON
- 审计日志表（AuditLog）：API 调用全记录
- 定时任务配置表（Schedules）：持久化定时任务元数据
- 近 N 天统计报表（按状态/每日趋势/成功率/平均耗时）
- 过期数据自动清理（默认保留 30 天）
- 导出功能（JSON 备份）

**SSE 实时推送系统 `handlers/sse_handler.py`** 🆕
- `SseManager`：线程安全连接管理器，按 token 隔离事件
- 支持事件类型：`task_update` / `task_result` / `system_alert` / `scheduled_trigger` / `heartbeat`
- 25 秒心跳保活，断线自动重连（5 秒后）
- `stream_with_context` 兼容 Flask 长连接
- `register_sse_routes()` 路由注册函数
- 自动摘要结果（JSON → 200 字符截断）

**HTTP Handler 大幅增强 `handlers/http_handler.py`** ✅
- `create_app()` 新增 `db` + `sse_manager` 参数注入
- 任务创建时自动持久化到 SQLite
- API 认证自动写入审计日志
- **新增端点**：
  - `GET  /api/v1/history` — 历史任务查询（支持分页/状态过滤/时间范围）
  - `GET  /api/v1/history/<id>` — 历史详情
  - `GET  /api/v1/stats` — 统计报表
  - `GET  /api/v1/audit` — 审计日志（Admin）
  - `DELETE /api/v1/history/cleanup` — 清理过期记录
  - `GET  /api/v1/history/export` — JSON 导出
  - `GET  /api/v1/events/count` — SSE 连接数

**Server 集成升级 `server.py`** ✅
- `TaskDatabase` + `SseManager` 全局初始化
- 任务完成回调：持久化 → SSE推送 → 通知三步联动
- SSE 路由自动注册（`/api/v1/events`）
- Web Admin 静态文件路由（`/admin/`）
- Telegram Bot 同步传递 `sse_manager`

**全新 Web Admin v2 `web_admin/index_v2.html` + `dashboard.js`** 🆕
- 移动端优先设计（深色主题）
- 5 个标签页：控制台 / 历史 / 快捷 / 统计 / 设置
- SSE 实时推送 UI 指示器
- 任务历史点击查看详情（params/result/error）
- 统计图表（每日趋势柱状图 + 成功率 + 平均耗时）
- 快捷触发面板（4 宫格 + 卡片列表）
- 消息发送、URL Scheme 复制、API Key 管理
- 数据清理 + JSON 导出

### 代码更新

- `server.py`：`import json`，`db`/`sse_manager` 注入，任务回调三步联动
- `http_handler.py`：新增 `db`/`sse_manager` 参数，DB 端点 7 个，审计日志写入
- `core/database.py`：新建 ~280 行，完整数据模型 + 统计聚合
- `handlers/sse_handler.py`：新建 ~260 行，SSE 事件系统

### 依赖

- `core/database.py` 无额外依赖（使用标准库 `sqlite3`）
- `handlers/sse_handler.py` 无额外依赖
