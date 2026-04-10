# 迭代日志 v2.9.0（2026-04-10）

> 主题：**FastAPI 原生层 + Plugin 系统 + Web Admin v3 — 全链路异步升级**
> cron 定时任务执行日期：2026-04-10

---

## 本次完成

### 1. FastAPI Server — `fastapi_main.py`（新建 ~490行）

**替换 Flask，完整异步化：**

| 特性 | Flask（旧） | FastAPI（新增） |
|------|------------|----------------|
| 异步 | 同步 only | 全链路 async/await |
| WebSocket | 需要 flask-socketio | 原生 `app.websocket()` |
| SSE | 手动实现 | StreamingResponse 原生支持 |
| OpenAPI | 手动写 docstring | 自动生成（访问 `/docs`） |
| 类型校验 | 手动 | Pydantic 自动 |
| CORS | flask-cors | 原生 Middleware |

**新增端点：**
```
WS  /ws                     WebSocket 双向通道（ping/subscribe/trigger）
GET /api/v1/events          SSE 实时推送（兼容旧客户端）
POST /api/v1/plugins        注册插件
GET  /api/v1/plugins        列出插件
DELETE /api/v1/plugins/{id} 卸载插件
GET  /api/v1/nl/cmd         快捷指令 GET 入口（兼容 iOS 快捷指令）
```

**生命周期管理：**
```python
@lifespan
async def lifespan(app):
    # 启动：初始化所有组件（client/task/db/scheduler/nl/plugin/monitor）
    yield
    # 关闭：scheduler.stop() / monitor.stop() / 关闭所有 WS 连接
```

**SSE Manager 重构：**
```python
class SseManager:
    async def connect(ws)     # WebSocket 接入
    async def disconnect(ws)   # 优雅摘除
    async def broadcast(event) # 广播到所有连接
    # 死连接自动清理
```

**启动方式：**
```bash
cd /workspace/reports/oc-cross-device/code
OPENCLAW_API_KEY=xxx /app/.venv/bin/python -m clawctl.fastapi_main --port 8081
# 或直接
/app/.venv/bin/python clawctl/fastapi_main.py --port 8081
```

---

### 2. Plugin 系统 — `core/plugin_manager.py`（新建 ~380行）

**核心能力：动态注册意图 + 自定义 handler，用户无需改代码**

```
用户安装插件
       ↓
PluginManager.register(Plugin)
       ↓
NL Interpreter 动态扩展意图表
       ↓
用户说"帮我搜推荐算法岗位" → job_search 意图 → job-hunter 插件执行
```

**Plugin 数据结构：**
```python
@dataclass
class Plugin:
    id: str          # 唯一标识
    name: str        # 显示名称
    description: str # 描述
    intents: list[dict]  # 意图列表
    handlers: dict   # intent → callable
    enabled: bool
```

**内置插件（无需安装）：**
- `builtin_commands`：status/list/help/ping — 常用快捷命令

**插件市场（静态）：**
| 插件 | 功能 |
|------|------|
| job-hunter | 自动抓取 Boss 直聘/猎聘岗位，简历匹配 |
| stock-watcher | 监控自选股异动，钉钉推送告警 |
| meeting-notes | AI 自动生成结构化会议纪要 |
| dev-ops | 服务器健康检查、日志分析、异常告警 |

**API：**
```bash
# 安装插件
curl -X POST http://localhost:8081/api/v1/plugins \
  -d '{"id":"job-hunter","name":"求职助手","description":"...","intents":[{"intent":"job_search","keywords":["找工作","职位"],"handler":""}]}'

# 列出插件
curl http://localhost:8081/api/v1/plugins

# 卸载插件
curl -X DELETE http://localhost:8081/api/v1/plugins/job-hunter
```

---

### 3. NL Interpreter Plugin 扩展 — `core/nl_plugin_ext.py`（新建 ~160行）

**为 NLInterpreter 注入插件能力（幂等 patch）：**
```python
from clawctl.core.nl_plugin_ext import patch_nl_interpreter

interpreter = NLInterpreter()
patch_nl_interpreter(interpreter, plugin_manager)

# 新增方法
interpreter.add_custom_intent("job_search", ["找工作","职位搜索"], plugin_id="job-hunter")

# _recognize_intent 插件意图优先匹配
result = interpreter.parse("帮我找推荐算法工作")
# → job_search (plugin), confidence=0.95
```

---

### 4. Web Admin v3 — `web_admin/v3/index.html`（新建 ~650行）

**React 18 SPA，移动端优先（桌面端兼容）：**

| Tab | 功能 |
|-----|------|
| ⚡ 任务 | NL 输入 + 预览解析 + 6 个快捷任务按钮 + 实时任务列表 |
| 📊 监控 | CPU/内存/活跃任务 实时指标 + ECharts 仪表盘 + 告警面板 |
| 🔀 DAG | Canvas 绘制 DAG 流程图（4节点+3条并行边）|
| 🔌 插件 | 已安装插件管理 + 插件市场（4个市场插件一键安装）|

**技术选型：**
- React 18（CDN UMD，无需构建）
- ECharts 5（仪表盘图表）
- Canvas API（DAG 可视化）
- CSS 变量（暗色主题）
- PWA（manifest.json，添加至主屏幕）

**访问方式：**
```
http://服务器IP:8081/admin_v3/   ← FastAPI 挂载
http://服务器IP:18790/admin/     ← 原 Flask 静态文件
```

---

### 5. FastAPI 依赖文件 — `fastapi_requirements.txt`（新建）

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
python-multipart>=0.0.6
```

---

## 架构对比（v2.8 → v2.9）

```
v2.8（Flask）                    v2.9（FastAPI）
────────────────────            ──────────────────────
Flask + Blueprint 同步            FastAPI + async/await 全链路异步
flask-socketio (需额外安装)       原生 WebSocket
手动 SSE Response               StreamingResponse
静态文件 @app.route              StaticFiles Mount
手动参数校验                     Pydantic 自动校验
无 OpenAPI                      自动 /docs /redoc
单例 scheduler                  Lifespan 生命周期管理
无插件系统                       PluginManager + 插件市场
NL interpreter 独立             NL + Plugin 双引擎
旧版 Web Admin                  Web Admin v3 (React SPA)
```

---

## 待办（v3.0 方向）

- [ ] DAG 可视化编辑器（节点拖拽编排）
- [ ] Plugin 安装器（从远程 URL 安装）
- [ ] 多 OpenClaw 实例 Web 端管理
- [ ] 任务执行历史分析（统计图表）
- [ ] 语音输入（Web Speech API）
- [ ] Docker Compose 集成 FastAPI 版本
