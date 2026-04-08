# 迭代日志 (Changelog)

## v2.7.0 — 2026-04-08（LLM驱动的深度语义解析）🆕 本次完成

> 主题：**当规则引擎"看不懂"时，GLM-4 自动顶上 — 复杂指令零门槛解析**

---

### 核心能力：规则引擎 + GLM-4 双引擎

**为什么需要 LLM 增强？**

规则引擎擅长处理「固定模式」：
- ✅ "生成今日技术简报" → `trigger_report` conf=0.95
- ✅ "查一下AI热点新闻" → `trigger_fetch` conf=0.90
- ❌ "最近有没有什么比较火的AI创业公司值得关注的" → conf=0.30（规则无法识别）
- ❌ "帮我看看大模型最近有什么新的进展" → conf=0.40（模糊）

**LLM 增强后的效果：**
- 规则置信度 < 0.55 → 自动调用 GLM-4
- GLM-4 深度语义理解 → 返回结构化结果
- 自动合并 LLM 结果，替换/增强规则解析
- 端到端延迟透明可见

---

### 新增文件

#### `core/nl_interpreter/llm_resolver.py` 🆕 (~250行)

**LLMLightResolver — LLM驱动轻量解析器**

| 特性 | 说明 |
|------|------|
| 按需调用 | 规则置信度 < 0.55 才触发，避免不必要的 API 消耗 |
| GLM-4-Flash | 200万Tokens/天免费额度，低成本高性能 |
| 低温度采样 | temperature=0.1，保证输出稳定可靠 |
| JSON强制解析 | 解析LLM输出，容错处理 markdown 代码块 |
| 单例模式 | 全局共享，避免重复创建 Client |
| 延迟透明 | 返回 `latency_ms`，便于监控 |

**调用链：**
```
用户: "最近有没有什么比较火的AI创业公司？"
       ↓
规则引擎: conf=0.35 (不足阈值 0.55)
       ↓
LLMLightResolver.parse(text, rule_confidence=0.35)
       ↓
GLM-4 API 调用
{
  "intent": "trigger_report",
  "confidence": 0.88,
  "agent": "market-insight",
  "params": {"topics": ["AI创业", "融资动态"], "scope": "all"},
  "reasoning": "用户想了解AI创业公司热点，属于市场洞察类报告",
  "suggestion": null
}
       ↓
自动合并到 TaskPlan，执行任务 + 钉钉通知
```

**环境变量：**
```bash
export GLM_API_KEY="your-zhipu-api-key"  # 智谱AI开放平台
```

---

#### `handlers/nl_routes.py` 增强 🆕

**NLRequest 新增字段：**
```python
use_llm: bool = Field(default=True, description="置信度不足时启用GLM-4增强")
```

**NLResponse 新增字段：**
```python
llm_enhanced: bool          # 是否经过GLM-4增强
llm_reasoning: str          # GLM-4推理说明
llm_latency_ms: float      # GLM-4调用耗时
```

**整合逻辑（nl_execute）：**
```python
if req.use_llm and plan.confidence < LLM_THRESHOLD:
    llm_result = await llm_resolver.parse(text, rule_confidence=plan.confidence)
    if llm_result and llm_result.confidence > plan.confidence:
        plan.intent = llm_result.intent
        plan.confidence = llm_result.confidence
        plan.agent = llm_result.agent
        plan.params.update(llm_result.params)
```

**新端点：**
```
POST /api/v1/nl/llm-parse    强制GLM-4深度解析（不经过规则引擎）
```

---

### 使用场景

#### 场景 1：复杂模糊指令（自动触发LLM）

```bash
curl -X POST http://localhost:8081/api/v1/nl \
  -H "Content-Type: application/json" \
  -d '{"text": "最近有没有什么比较火的AI创业公司值得关注的", "channel": "dingtalk"}'

# 返回
{
  "success": true,
  "intent": "trigger_report",
  "confidence": 0.88,      # LLM提升置信度
  "agent": "market-insight",
  "llm_enhanced": true,
  "llm_reasoning": "用户想了解AI创业公司热点，属于市场洞察类报告",
  "llm_latency_ms": 420.5
}
```

#### 场景 2：强制LLM解析（复杂多义词）

```bash
curl -X POST http://localhost:8081/api/v1/nl/llm-parse \
  -H "Content-Type: application/json" \
  -d '{"text": "帮我看看大模型最近有什么新的进展，侧重技术层面的"}'

# 直接返回LLM解析结果（不经过规则引擎）
{
  "success": true,
  "intent": "trigger_analysis",
  "confidence": 0.91,
  "agent": "tech-analyst",
  "params": {
    "topics": ["大模型", "技术进展", "LLM"],
    "scope": "technical",
    "time_range": "recent"
  },
  "reasoning": "用户关注大模型技术进展，属于技术分析类任务",
  "llm_enhanced": true,
  "llm_latency_ms": 387.2
}
```

#### 场景 3：快捷指令（低置信度自动升级）

```
iOS 快捷指令 → POST /api/v1/nl
  → 规则引擎 conf=0.35（不足）
  → 自动触发 GLM-4 → conf=0.88 ✅
  → 执行任务 + 钉钉通知
```

---

### 架构图（v2.7.0 LLM增强层）

```
                    ┌──────────────────────────────┐
                    │     NL自然语言输入            │
                    │  "最近AI创业有什么好机会？"   │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │      规则引擎 NLInterpreter  │
                    │  intent=unknown conf=0.35 ⚠  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  CONFIDENCE < 0.55?          │
                    │  ════════════════════        │
                    │         是 ↓                 │
                    │  ┌──────────────────┐       │
                    │  │  LLMLightResolver │       │
                    │  │  (GLM-4-Flash)    │       │
                    │  └────────┬─────────┘       │
                    │           │                 │
                    │  intent=trigger_report     │
                    │  conf=0.91 ✅               │
                    │  agent=market-insight       │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │      执行器 NLExecutor        │
                    │  spawn_agent + 钉钉通知       │
                    └──────────────────────────────┘
```

---

### 代码变更

| 文件 | 变更 |
|------|------|
| `core/nl_interpreter/llm_resolver.py` | 🆕 新增 ~250行，LLM解析引擎 |
| `handlers/nl_routes.py` | ✏️ 修改，整合LLMresolver，659行 |
| `fastapi_server/main.py` | ✏️ 修改，传入GLM_API_KEY |

---

### 配置说明

**启用GLM-4增强：**
```bash
# .env 或环境变量
GLM_API_KEY=your-zhipu-api-key
```

**智谱AI注册（免费）：**
- 地址：https://open.bigmodel.cn/
- 控制台 → API Keys → 创建Key
- GLM-4-Flash：200万Tokens/天免费

**成本预估：**
- 1条NL指令 ≈ 200-400 tokens
- 免费额度 ≈ 5000-10000次/天
- 完全覆盖日常使用场景

---

### 后续迭代方向

- **v2.8.0**：多轮对话上下文记忆（NL会话session，复杂任务拆解）
- **v2.8.0**：Plugin系统（自定义意图 + 参数schema）
- **v2.9.0**：意图路由可视化（Web Admin展示解析链路）
