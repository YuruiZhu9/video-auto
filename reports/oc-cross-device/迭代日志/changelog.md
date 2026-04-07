# 迭代日志 (Changelog)

## v2.4.0 — 2026-04-06（多实例管理 · 实时监控 · 智能告警）✅ 本次完成

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
