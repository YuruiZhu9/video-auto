# Prompt Engineering - 高效提问的艺术

## 核心原则

### 1. 明确具体
- ❌ "帮我写个API"
- ✅ "帮我写一个用户登录的REST API，使用Express + JWT，返回token"

### 2. 提供上下文
- ❌ "这段代码报错"
- ✅ "在Node.js 18环境下，这段读取文件的代码报错..."

### 3. 指定格式
- ❌ "告诉我怎么做"
- ✅ "用步骤1、步骤2的形式告诉我..."

### 4. 设定约束
- "用TypeScript写"
- "不要用第三方库"

## 高效Prompt模板

### 代码生成
```
生成[语言/框架]的[功能]代码：
- 输入：[参数]
- 输出：[返回值]
- 要求：[约束条件]
```

### 问题排查
```
[环境信息]
问题描述：[具体问题]
错误信息：[日志/报错]
```

## 进阶技巧

### 分步引导
1. "先帮我设计数据库结构"
2. "基于这个结构，写API路由"
3. "添加错误处理"

### 指定风格
- "用函数式编程风格"
- "参考React Hooks最佳实践"

### 5. 按任务类型选模型（Peter Steinberger，2026）

选对模型比优化 Prompt 更重要：

| 任务复杂度 | 代表任务 | 推荐模型 | 理由 |
|-----------|---------|---------|------|
| **简单** | 代码补全、格式化、翻译 | Haiku / Gemini Flash | 速度快、成本低 |
| **中等** | 单函数生成、BugFix、解释 | Sonnet / GPT-4o | 性价比最优 |
| **复杂** | 架构设计、系统重构、多模块 | Opus / o1 | 深度推理能力 |

> 核心原则：AI = 放大器（放大你的技能），人类 = 设计师（定义方向、最终审批）

## 2026年进阶技巧 (Addy Osmani)

### 1. 迭代式规划Prompt
- 让LLM先**迭代提问**直到需求和边界情况都清晰
- 生成详细规格文档(spec.md)包含：需求、架构决策、数据模型、测试策略

### 2. 分步任务Prompt模板
```
任务目标：[具体目标]
当前状态：[现状]
期望结果：[期望]
约束条件：[限制]
验证方式：[如何验证成功]
```

### 3. 调试Prompt模板
- 预期结果 vs 实际结果
- 最小复现步骤
- 附上相关代码片段

### 4. 代码审查Prompt
- "审查以下代码，找出潜在问题"
- "用第二AI会话来审查第一会话生成的代码"

### 5. 上下文构建技巧
- 使用 gitingest 或 repo2txt 把代码库关键部分转为文本
- 使用 Context7 等 MCP 工具增强上下文
- CLAUDE.md 记住项目约定

### 2026年Prompt Engineering十大最佳实践 (Meetzest)

#### 1. 具体且有上下文的Prompt
质量输入→质量输出。 vague requests → generic, often unusable code.
- ✅ 好的Prompt示例：`Create a reusable React button component using TypeScript and Tailwind CSS v3.3. It should accept an 'onClick' handler and a boolean 'disabled' prop. Style it to match our design system: primary color #3B82F6, white text, rounded-md corners, and a px-4 py-2 size.`
- 保存成功的Prompt为团队"Cheatcodes"确保一致性

#### 2. 明确输出格式
- 使用 `Format your response as:` 或 `Return ONLY the following structure:`
- 为复杂情况提供mini-templates
- 标准化团队输出格式

#### 3. 迭代优化
- 有效Prompt是循环优化过程，不是单次尝试
- 分析缺失什么信息导致响应错误
- 逐步添加澄清信息
- 跟踪Prompt版本

#### 4. Few-Shot示范
- 给AI看具体示例比描述更有效
- 嵌入代表性代码片段
- 为数据转换任务提供输入-输出对

#### 5. 分解复杂任务
- 大问题一次性解决 → 不完整、有bug的输出
- 分解为逻辑步骤，用顺序Prompt：
  1. "Create a React component for a shopping cart summary"
  2. "Build a shipping address form with validation"
  3. "Write the function to integrate Stripe Elements"

#### 6. 询问推理过程
- 把AI当作学习伙伴，不只是代码生成器
- 添加 "explain your reasoning" 或 "describe trade-offs"
- 捕获教育输出作为共享资源

#### 7. 设置明确约束
- 告诉AI**不**想要什么和**想要**什么一样重要
- 创建专门的 "Constraints:" 部分
- 链接风格指南和编码标准
- 指定性能预算和大小限制

#### 8. 使用领域特定语言
- ✅ "add a B-tree index on the 'user_id' column in the 'orders' table"
- ❌ "speed up the database query"
- 用具体指标替换模糊目标（"better", "faster"）
- 建立团队术语表

#### 9. 立即验证和测试
- 永远不要盲目复制粘贴AI代码
- 在工作流中内置即时验证
- 显式要求单元测试和边界情况
- 使用验证清单（静态分析、敏感信息检测）

#### 10. 测量和追踪
- 有效Prompt是团队特定的
- 建立基线，使用AI特定指标（会话有效性、修订率）
- 定期审查以识别有效模式
- 只为有积极影响的实践创建团队范围模板

**核心指标：**
- Prompt成功率：首次生成可用输出的百分比
- 每个任务的迭代周期：最终解决方案所需的平均修订次数
- 到首个有效代码的时间：从初始Prompt到通过测试的时间

---

### Addy Osmani 工作流核心原则（2026）

#### 补充工具链（完整引用）
- **Jules**：Google异步编程Agent，克隆代码库到云端VM后台工作，自动开PR
- **Copilot Agent**：GitHub异步Agent，背景任务处理
- **Conductor**：多Agent并行编排工具
- **Chrome DevTools MCP**：桥接静态代码分析和浏览器实时执行
- **Context7 / gitingest / repo2txt**：将代码库关键部分导入上下文
- **AI-assisted engineering book**：[beyond.addy.ie](https://beyond.addy.ie/)

#### 1. 计划先行 (Specs Before Code)
- 不要只是把需求扔给LLM，先定义问题并规划解决方案
- 在写代码前与AI头脑风暴详细的规格说明
- 让LLM迭代提问直到完善需求和边界情况
- 生成包含需求、架构决策、数据模型、测试策略的 spec.md

#### 2. 分块投喂 (Chunked Context)
- 范围管理是关键 - 给LLM可管理的任务，而不是整个代码库
- 避免大型整体输出 - 将项目分解为迭代步骤/ticket
- 每个chunk要足够小，让AI能在上下文窗口内处理
- 结合TDD（测试驱动开发）效果最佳

#### 3. 充足上下文
- LLMs只和你提供的上下文一样好
- 使用 Context7、gitingest、repo2txt 等工具导入相关代码库部分
- 提供：高层目标/不变量、好的解决方案示例、避免的方法警告

#### 4. 规则驱动行为
- 创建 CLAUDE.md 或 GEMINI.md 文件，包含过程规则和偏好
- 使用 "Big Daddy" 规则或 "no hallucination" 条款
- 示例规则："如果有疑问，先问清楚而不是编造答案"

---

### 5. OpenAI Codex 有效上下文四要素（2026 新增）

来自 OpenAI Codex 最佳实践指南，与 Addy Osmani 方法论高度收敛：

| 要素 | 说明 | 示例 |
|------|------|------|
| **明确的目标** | 你想要做什么 | "实现用户认证模块" |
| **充分的上下文** | 相关文件、文档、错误信息 | 附上现有 auth.py 代码片段 |
| **清晰的约束条件** | 规范、架构要求、项目惯例 | "使用 JWT、不修改迁移文件" |
| **可量化的完成标准** | 测试通过、bug消失、功能正常 | "单元测试覆盖率 > 80%" |

**核心理念：**
> AI只是将人类需求表达方式放大了，它无法像人一样主动猜测你的意图。说清楚要什么、背景是什么、有什么限制、如何验收——这种沟通逻辑与人类协作如出一辙。

**工具权限配置原则：**
- 初期设置严格权限（什么能做、什么需要批准）
- 熟悉工具后逐步放开
- 这与学习任何新工具的逻辑一致：先小心试探，确认安全后放心使用

**规范文档迭代原则（AgentS.md / CLAUDE.md）：**
- 文档应短而准确，先框架后补充
- AI犯同样错误两次 → 及时复盘，将教训加入文档
- 规则是可演进的，不是写一次就固定了


---

## 6. Spec 层级体系 + Human-as-Driver（hamy.xyz / Addy Osmani 2026）

**来源：** hamy.xyz/blog/2026-01_ai-engineering-best-practices（Google AI Director 五原则提炼）

### Spec 三级分层（此前以分散形式存在，本节集中整合）

| 层级 | 定义 | 使用时机 | 内容要求 |
|------|------|---------|---------|
| **产品级 Spec** | 描述产品今天做什么 | 每次 AI 会话开始时读取 | 功能范围、技术架构、不变量 |
| **变更级 Spec** | 描述具体变更的预期结果，而非实现方式 | 发起变更时 | 目标行为、成功标准、约束 |
| **变更级计划** | AI 将遵循的实现计划 | Spec 确认后 | 分阶段，每阶段一个逻辑变更 |

**Spec → Plan → 执行工作流：**
```
1. 写变更级 Spec（描述目标结果）
   ↓
2. AI 基于产品 Spec + 变更 Spec 生成变更级计划
   ↓
3. 分阶段执行：每个阶段一个逻辑变更，保持代码库可运行状态
   ↓
4. 每阶段：review → 测试 → commit → 下一阶段
   ↓
5. 更新产品 Spec（新现实）
   ↓
6. 下一变更
```

### Human-as-Driver 核心理念（Addy Osmani + hamy.xyz 共同强调）

> "AI-augmented software engineering, not AI-automated. The human engineer remains the director."
> — Addy Osmani（Google Gemini 团队总监）

**人类负责的三件事（AI 无法替代）：**

| 职责 | 说明 | 为什么 AI 做不了 |
|------|------|-----------------|
| **代码质量最终责任** | 每个 bug、安全漏洞、体验问题都有你的名字 | 价值判断、用户体验感知 |
| **产品愿景** | 构建什么？用户感受如何？ | 战略决策、优先级排序 |
| **系统设计** | 架构决策、模块间权衡 | 全局视角、业务理解 |

**AI 能做什么（放大器而非替代者）：**
- 快速生成：重复代码、样板代码、BugFix
- 高上下文任务：读懂大型代码库、跨文件重构
- 永不疲倦地执行明确方向下的任务

**核心原则：永远不要把方向盘完全交给 AI**
> "这个功能先让 AI 出初稿 → 我来 review → 过了再让它接着做下一块"
> — Peter Steinberger，AI Coding 元框架实战口诀


---

## ⚠️ 2026范式转变通知：从Prompt Engineering → Context Engineering

> **最重要趋势（2026年3月更新）**：AI Coding领域正在发生从"Prompt Engineering"到"**Context Engineering**"的根本性范式转变。
> 
> 详见：`patterns/context-management.md` — "2026最大范式转变：Context Engineering（上下文工程）"章节

**核心变化：**
- 焦点从"优化单条指令"转向"设计AI的整个工作内存架构"
- Gartner数据：Context Engineering方法带来 **50%响应速度提升、40%输出质量提升**
- 新框架：**CTCO**（Context-Task-Constraints-Output）— OpenAI GPT-5.2官方方法论

**快速对照：**

| 你在做的 | 正确做法 |
|---------|---------|
| 优化Prompt措辞 | 同时检查上下文是否包含正确信息 |
| 担心模型不够聪明 | 检查上下文是否被无关信息稀释（LLM准确率↓24.2%）|
| 一个通用Prompt | 根据任务动态组装最优上下文（CTCO框架）|
| Prompt工程师 | Context架构师（岗位增长250%）|

*延伸阅读：`patterns/context-management.md` — Context Engineering 完整章节*

---

## 7. Cursor Automations Pipeline（事件驱动 AI 动作，🆕 2026-03）

**来源：** dev.to @dohkoai，2026-03

Cursor 在 2026 年 3 月推出 Automations 功能，实现基于事件的 AI 动作触发，是 IDE 内 AI 能力的重要升级。

### 核心触发器

| 触发器 | 动作示例 | 适用场景 |
|--------|---------|---------|
| `file_save` | 自动 review + 建议修复 | 保存 `.test.ts` 时自动审查 |
| `git_commit` | 自动生成 changelog 条目 | 提交时自动文档化变更 |
| `test_fail` | AI 分析失败原因 + 提供修复 | 持续集成环节 |
| `pr_open` | 自动补充测试、文档缺失检查 | PR 创建时 |

### Cursor Automations 配置示例

```json
{
  "automations": [
    {
      "trigger": "file_save",
      "pattern": "**/*.test.ts",
      "action": "review_and_suggest",
      "model": "claude-sonnet-4.6",
      "context": ["src/**/*.ts", "jest.config.ts"]
    },
    {
      "trigger": "git_commit",
      "action": "generate_changelog_entry",
      "model": "gpt-5.4-mini"
    }
  ]
}
```

> **便宜模型（GPT-5.4 Mini / Sonnet）处理自动化，昂贵模型（Opus）处理架构决策 — 节省 70%+ 成本**

### 与 Claude Code 的定位差异

- **Cursor Automations**：事件驱动、IDE 内即时反应，适合短循环反馈
- **Claude Code**：任务级自主执行、终端原生，适合端到端功能交付
- **推荐组合**：Cursor 处理 Automations + Claude Code 处理复杂任务

---

## 8. Multi-Model Rotation Strategy（多模型轮换成本路由，🆕 2026-03）

**来源：** dev.to @dohkoai，2026-03，节省 73% 成本

### 任务路由配置

```yaml
routing:
  architecture_decisions:    # 最复杂 → 最高配模型
    primary: claude-opus-4.6
    fallback: gpt-5.4
    max_cost_per_task: $5.00

  code_generation:           # 中等复杂度
    primary: claude-sonnet-4.6
    fallback: deepseek-r1
    max_cost_per_task: $0.50

  test_writing:              # 低复杂度 → 便宜模型
    primary: gpt-5.4-mini
    fallback: mistral-small-4
    max_cost_per_task: $0.10

  code_review:               # 需要质量但不必最高配
    primary: claude-sonnet-4.6
    fallback: gpt-5.4-mini
    max_cost_per_task: $0.25
```

### 成本对比

| 策略 | 日成本 | 年成本（~250工作日） |
|------|--------|-------------------|
| 单一 Opus 模型 | ~$15/天 | ~$3,750/年 |
| 多模型轮换 | ~$4/天 | ~$1,000/年 |
| **节省** | **73%** | **~$2,750** |

> **用 $15/M-token 的模型写单元测试 = 浪费；用 $0.1/M-token 的模型做架构决策 = 冒险**

---

## 9. AGENTS.MD 驱动开发（实时维护，🆕 2026-03）

**来源：** dev.to @dohkoai，2026-03

每个主流 AI Coding 工具都会读取 `AGENTS.md`。一份维护良好的文件可消除 80% 的"AI 不理解我的项目"问题。

### 关键维护时机

| 时机 | 动作 |
|------|------|
| 架构决策时 | 立即写入 AGENTS.md |
| 发现 bug 时 | 写入 Known Issues |
| 新增依赖时 | 更新 Project Context |
| 功能完成时 | 更新 Current State |

### 进阶：.claude/pipeline.yaml（CI/CD 集成，🆕 BSWEN 2026-03）

```yaml
workflows:
  daily-review:
    schedule: "0 9 * * *"
    tasks:
      - name: "Review open PRs"
        agent: code-reviewer
      - name: "Check security alerts"
        agent: security-scanner
  feature-development:
    trigger: issue-created
    tasks:
      - name: "Analyze requirements"
        agent: planner
      - name: "Implement feature"
        agent: implementer
      - name: "Run tests"
        agent: test-runner
      - name: "Create PR"
        agent: pr-creator
```

> Claude Code CLI 原生架构天然支持 Pipeline 自动化（优于 Cursor 的视觉化方案）；Cursor 在交互式快速编辑上有优势

---

## 🆕 Claude Code Extended Thinking 机制（Simon Willison 源码分析，2025-04）

Claude Code 内置**分层思维预算**机制，通过在提示词中嵌入特定短语触发不同级别的额外推理能力：

| 触发词 | 思维预算 (Token) | 适用场景 |
|--------|---------------|---------|
| `think` | 4,000 | 简单推理，快速决策 |
| `think hard` / `megathink` | 10,000 | 复杂分析，多方案权衡 |
| `ultrathink` / `think harder` 等 | 31,999 | 高风险决策、全局架构权衡 |

> 原始实现来源：[Simon Willison 源码分析](https://simonwillison.net/2025/Apr/19/claude-code-best-practices/)（2025-04），通过解析 Claude Code CLI JS 代码 + ripgrep 验证。

**使用原则：**
- 日常任务用 `think`，节省 token
- 架构级决策用 `ultrathink`，充分权衡后再行动
- 不要对所有问题都触发最高级思维预算
- Anthropic 官方建议：按此顺序递进 → `think` < `think hard` < `think harder` < `ultrathink`


---

## 🆕 CRISP Prompt Framework（dev.to 2026）

**来源：** dev.to "Prompt Engineering for Developers: 10x Your AI Coding in 2026"

五步结构化 Prompt 框架，专门为开发者设计：

| 组件 | 说明 | 示例 |
|------|------|------|
| **C - Context** | 技术背景：语言/框架/架构 | "Node.js + Express + PostgreSQL" |
| **R - Role** | AI角色定位 | "Senior Python Backend Engineer" |
| **I - Instructions** | 任务分解（动词开头） | "实现、测试、部署..." |
| **S - Specifications** | 成功标准/风格规范 | "覆盖率>80%，遵循PEP8" |
| **P - Polish** | 要求解释权衡和替代方案 | "说明trade-off" |

**项目上下文模板（CRISP 扩展）：**
```
I'm working on [PROJECT TYPE] using [TECH STACK].
Key constraints: [PERFORMANCE/MEMORY/COMPATIBILITY]
Architecture: [MVVM/MVC/CLEAN]
Coding standards: [STYLE GUIDE]
When providing solutions:
1. Follow [SPECIFIC STYLE]
2. Include appropriate error handling
3. Consider [SPECIFIC PERFORMANCE]
4. Explain trade-offs made
```

**三大高级 Prompt 模式：**

- **Chain-of-Thought**：引导AI逐步推理复杂问题
  ```
  "让我理解实时聊天系统：
  1. 评估 WebSocket vs SSE vs 轮询
  2. 设计客户端消息状态管理
  3. 处理连接失败和重连
  对每步解释推理并展示代码。"
  ```

- **Constraint-First**：先给限制条件，再设计方案
  ```
  "需要图片缓存，约束：
  - 1GB RAM 设备可用
  - 磁盘缓存不超过 50MB
  - 兼容现有 URLSession 配置
  基于此设计缓存策略。"
  ```

- **Evolution Pattern**：多版本迭代（简单→复杂）
  ```
  "展示 Python 限流器的三个版本：
  1. 基础：内存计数器
  2. 中级：Redis 滑动窗口
  3. 高级：可配置令牌桶
  每版本说明适用场景。"
  ```

---

## 🆕 "Waterfall in 15 Minutes" 极速规格驱动开发（Addy Osmani 2026）

**来源：** Addy Osmani "My LLM coding workflow going into 2026"

**核心理念：** 用AI辅助在15分钟内完成传统"瀑布流"规格文档的全流程：

1. **明确问题** → 用自然语言描述需求
2. **与AI头脑风暴规格** → 让AI主动追问直到需求清晰
3. **生成完整 spec.md** → 包含：需求/架构/数据模型/测试策略
4. **AI生成里程碑计划** → 分解为可执行任务
5. **迭代直到计划完整** → 确认逻辑自洽

**Addy Osmani 原文：**
> "Ask AI to iteratively ask questions until requirements are fleshed out. Compile into a comprehensive spec.md. Use a reasoning-capable model to generate a project plan broken into logical tasks. Iterate on the plan until coherent and complete."

**vs 传统方式：**
- ❌ 传统：想法 → 直接写代码 → 发现问题 → 修改 → 重复
- ✅ AI原生：明确问题 → AI规划方案 → 执行 → 反思 → 优化

---

## 🆕 CLAUDE.md 实时架构更新规范（ccino.org 2026）

**来源：** blog.ccino.org "2026 Claude Code 工作流最佳实践"

**核心原则：** CLAUDE.md 不是静态文档，而是随项目演进的"活文件"

**好 vs 差的 CLAUDE.md：**
- ✅ 好的CLAUDE.md：包含架构目录、约束条件、编码风格、最近变更
- ❌ 不好的CLAUDE.md：列举所有50个文件功能（AI记不住）

**实时更新示例：**
```markdown
## 最近变更（2026-03-26）
- 添加了 Redis 缓存层（app/cache/）
- 认证方式从 JWT 改为 Session + Redis
- 新功能优先使用缓存，不要直接查数据库

## 编码风格
- 使用 Pydantic v2 的 @validate_call 装饰器
- 异步函数统一用 async/await
- 错误处理：统一 raise HTTPException

## 禁止事项
- ❌ 不要修改 alembic/versions/ 中的迁移文件
- ❌ 不要直接操作数据库，必须通过 service 层
- ❌ 不要添加新的依赖包，先在 CLAUDE.md 中说明用途
```

---

## 🆕 Type-First Development（类型优先开发）

**来源：** hamy.xyz/blog/2026-01_ai-engineering-best-practices（基于 Addy Osmani 工作流，2026-01）

**适用场景：** 超大系统，AI 上下文窗口无法一次性容纳所有接口时的迭代策略

**核心理念：** 先用类型定义系统边界，再在类型约束内逐个实现功能

**三步流程：**
1. **铺类型** → 用 TypeScript/Go/Pydantic 等类型系统，先描述整个系统的接口和数据结构
2. **分块实现** → 在类型约束内，一次实现一个功能
3. **上下文可控** → 每次 AI 对话只包含类型定义 + 当前任务，token 消耗稳定

**效果：**
- AI 始终在"类型边界"内工作，不易产生越界设计
- 系统演进时，类型变更驱动实现更新，而非相反
- 避免"上下文爆炸"（一次投喂太多导致 AI 输出质量下降）

**示例：**
```
# 第一轮：只给类型
"我有一个电商系统。以下是数据模型和接口类型定义：
- Product, Order, User 类型
- OrderService.create(), OrderService.cancel() 接口签名
请先理解这些类型，然后实现 OrderService。"

# 后续轮次：只提实现
"现在实现 OrderService.create()，包含库存校验和支付集成。"
```

---

## 🆕 Vibe Engineering vs Vibe Coding 哲学区分

**来源：** hamy.xyz/blog/2026-01_ai-engineering-best-practices（2026-01）

**Vibe Coding（直觉式编码）：**
- 自然语言描述意图，AI 生成代码，你"感受整个过程"
- 强调直觉、模糊性、整体感知
- 适合：探索阶段、快速原型

**Vibe Engineering（直觉工程）：**
- 同样利用 AI 加速实现，但**对输出保持批判性审视**
- 人类深度参与方向设定和质量把关
- AI 是执行工具，不是唯一的方向来源

**核心区别：**
| 维度 | Vibe Coding | Vibe Engineering |
|------|-------------|-------------------|
| 人类参与度 | 低（接受 AI 输出）| 高（主动判断决策）|
| 方向来源 | AI 主导 | 人类主导，AI 执行 |
| 适用场景 | 探索/学习 | 生产项目 |
| 质量风险 | 较高 | 可控 |

> "Vibe Engineering" = 享受 AI 速度，同时保持工程师的判断力


---

## 121. 上下文窗口主权（Context Window Sovereignty）— 2026年最大范式转变

**来源：** dev.to "Top 10 AI Coding Tools for 2026"（2026-03）

**核心概念：**
> 高性能工具现在摄取整个代码库、读取 Jira 历史、监听 Slack 讨论。只"看见"一个打开文件的工具已被视为过时。

**2026年新基准：**
| 指标 | 2024年末 | 2026年 |
|------|---------|--------|
| SWE-bench Lite 通过率 | 15% | **40%+** |
| 效率提升 | ~30% | **30-55%** |

**三大阵营（2026完整版）：**

| 阵营 | 代表 | 定位 |
|------|------|------|
| AI IDE | Cursor 2.0、Antigravity、Windsurf | AI是核心，编辑器重新打造 |
| 代码助手 | GitHub Copilot、Tabnine、JetBrains AI | 不换编辑器，能力受插件形式限制 |
| 编程智能体 | Claude Code、Codex、Cline、Gemini CLI | 自主规划、执行、测试、改代码 |

**战略含义：**
- 工具选择 = 选择了"能看到多少上下文"的权力
- 上下文窗口 = 2026年开发者的数字地产
- 只支持单文件补全的工具正在快速边缘化

---

## 122. RTF / RASC / COSTAR — 三大结构化 Prompt 框架（codewave.com 2026）

**来源：** codewave.com "AI Prompt Engineering Cheat Sheet for Software Teams"（2026）

三大框架覆盖不同复杂度场景，可互补使用：

### RTF（Quick Task Framework）— 简单任务首选

| 组件 | 说明 | 示例 |
|------|------|------|
| **Role** | 赋予 AI 具体角色 | "You are a software tester" |
| **Task** | 清晰描述任务 | "Identify performance bottlenecks in this API" |
| **Format** | 指定输出格式 | "List the issues with step-by-step fixes" |

**适用场景：** 代码调试、日志总结、文档生成等直接任务
**特点：** 轻量、三要素、快速上手

### RASC（Deep Analysis Framework）— 复杂分析任务

| 组件 | 说明 | 示例 |
|------|------|------|
| **Role** | 定义 AI 角色 | "You are a product coach" |
| **Action** | 说明执行动作 | "Guide a leader to refine AI features" |
| **Steps** | 分解为清晰步骤 | 先分析，再建议 |
| **Context** | 提供背景信息 | "The product uses AI for real-time recommendations" |

**适用场景：** 战略分析、多步推理、架构决策
**特点：** 强制分步思考，避免跳步幻觉

### COSTAR（Full-Spectrum Framework）— 高标准产出

| 组件 | 说明 | 示例 |
|------|------|------|
| **Context** | 背景信息 | "The app has performance issues" |
| **Outcome** | 定义目标 | "Reduce API response time by 30%" |
| **Style** | 输出结构 | "Step-by-step breakdown" |
| **Tone** | 响应语气 | "Professional and technical" |
| **Audience** | 受众是谁 | "Backend developers" |
| **Response** | 输出格式 | "List of bottlenecks with solutions" |

**适用场景：** PRD、技术提案、正式文档、多方评审
**特点：** 最完整，确保 AI 理解全貌

### 框架选用指南

| 任务复杂度 | 推荐框架 | 理由 |
|-----------|---------|------|
| 简单/单一目标 | RTF | 足够，无需过度设计 |
| 中等/多步骤 | CRISP（已有 Section 118）| R/I/S/P 平衡简洁与完整 |
| 高标准/正式产出 | COSTAR | C/O/S/T/A/R 六要素全覆盖 |
| 深度分析/推理 | RASC | 强制步骤分解 |
| 复杂规划 | CTCO（已有 Section 118）| C/T/C/O 适合模型规划输出 |

### 高级 Prompt 技巧（codewave.com 补充）

**If–Then 条件逻辑：**
```
If the code shows latency issues, suggest faster algorithms.
Otherwise, focus on optimizing database queries.
```
→ 让 AI 根据情况自适应，无需两个独立 Prompt

**Temperature 设置（软件开发场景）：**
| Temperature | 适用场景 |
|------------|---------|
| 0–0.2 | 编码、调试、精确指令（低随机性）|
| 0.7–1.0 | 头脑风暴、创意方案（高随机性）|

**Top-p 设置：**
| Top-p | 适用场景 |
|-------|---------|
| 0.2–0.5 | 代码生成、精确任务（聚焦）|
| >0.5 | 探索性任务（多样）|

---

## 🆕 Section 123 — Plan-then-Execute：推理模型的计划-执行分离模式（2026 新增）

**来源：** promptbestie.com "AI Prompt Engineering Trends 2026"

### 核心思想

推理模型（如 o3、Claude Opus/Gemini 的深度推理模式）现在原生支持「先规划再执行」的输出结构：

```
[PLANNING BLOCK] ← 模型先输出完整计划
- 步骤 1: ...
- 步骤 2: ...
- 风险评估: ...
[/PLANNING BLOCK]

[REASONING BLOCK] ← 推理过程
- 探索方案 A...
- 排除方案 B（因为...）
[/REASONING BLOCK]

[OUTPUT BLOCK] ← 最终输出
```

### 使用方法

在 Prompt 中明确要求：
```
在开始编码前，先：
1. 列出你的实现计划（每个文件的作用）
2. 标注潜在风险点
3. 确认验收标准

然后再开始生成代码。
```

### 与 CTCO 的结合

| 阶段 | CTCO 角色 | Plan-then-Execute 对应 |
|------|-----------|----------------------|
| C（Context） | 上下文提供 | [PLANNING BLOCK] 的输入 |
| T（Task） | 任务定义 | [PLANNING BLOCK] 的输出 |
| C（Constraints） | 约束条件 | [REASONING BLOCK] 中的排除逻辑 |
| O（Output） | 输出格式 | [OUTPUT BLOCK] |

### 适用场景

- ✅ 复杂多文件重构
- ✅ 架构决策（数据库选型、API 设计）
- ✅ 涉及多个服务/仓库的任务
- ❌ 简单单文件修改（过度工程）

---

## 🆕 Section 124 — SAM 3 与多模态 Prompt 新范式：从分割到概念理解（2026 新增）

**来源：** promptbestie.com "AI Prompt Engineering Trends 2026"

### SAM 3 的突破

**Segment Anything Model 3**（Meta）已从「图像分割」进化为「概念理解分割」：

| 版本 | 能力 | Prompt 类型 |
|------|------|-------------|
| SAM 1 | 分割任何图像中的物体 | 点/框/文本 |
| SAM 2 | 视频中跟踪分割 | 时序提示 |
| **SAM 3** | 基于复杂多模态提示的概念分割 | 文本+图像+音频联合描述 |

### SAM 3 的多模态 Prompt 示例

```json
{
  "image": "工业生产线视频帧",
  "audio": "异常振动音频片段",
  "prompt": "分割所有红色设备中发出异常声响的运动部件"
}
```

### 对 AI Coding 的启示

SAM 3 的演进映射到 LLM 提示工程的进化：

| SAM 版本 | LLM 对应能力 | 提示工程演进 |
|----------|-------------|-------------|
| SAM 1（单图像） | 纯文本输入 | 单一 Prompt |
| SAM 2（视频跟踪） | 多轮对话上下文 | 上下文管理 |
| SAM 3（概念理解） | 多模态输入（文本+图像+音频+视频） | **多模态 Prompt 组合** |

### 多模态 Prompt 最佳实践

1. **从最广模态开始**：图像/文档作为基础上下文
2. **叠加文本指令**：明确引导 AI 关注特定特征
3. **明确约束输出格式**：多模态输入增加了输出不确定性
4. **当前局限**：LLM 在长上下文内的相关信息准确率下降 **24.2%**（Glean 2025）


### Section 125 — Claude Code 快捷命令与 CLI 高级用法（computingforgeeks.com 2026-04）

**`/btw` 临时问答命令（Ephemeral Mode）：**
- 用法：`/btw [问题]`
- 效果：不保存到上下文，不触发 compact，纯粹临时查询
- 场景：确认某个 API 用法/查看某个文件/问一个快速问题后立即继续主线任务
- 对比：`/btw` vs 正常消息 = "草稿纸" vs "正式对话"

**CLI 非交互模式关键参数：**

| 参数 | 说明 | 场景 |
|------|------|------|
| `--max-budget-usd <金额>` | 设置本次会话最大消费上限 | CI/CD 自动化成本控制 |
| `--max-turns <N>` | 限制 Agent 最大对话轮次 | 防止失控长会话 |
| `--no-session-persistence` | 禁用会话持久化（纯一次性）| CI/CD 安全隔离环境 |
| `--debug` | 输出详细调试日志 | 排查超时/异常 |
| `--output-format json` | JSON 格式输出 | 脚本解析/自动化处理 |
| `--allowedTools` | 预授权工具白名单 | 自动化脚本安全边界 |

**Effort 级别详细对照表：**

| 级别 | 适用场景 | Token 消耗 |
|------|---------|-----------|
| `low` | 简单问题、快速查询 | 最少 |
| `medium` | 默认：日常编码/编辑/修复 | 平衡 |
| `high` | 复杂调试、架构决策 | 较多 |
| `max` | 最难问题（仅 Opus，支持无限思考预算）| 最多 |

**Hook 事件完整清单（computingforgeeks.com）：**

| 事件 | 触发时机 |
|------|---------|
| `SessionStart` | 会话启动时 |
| `PreToolUse` | 工具执行前（含 defer 决策）|
| `PostToolUse` | 工具执行后 |
| `Stop` | 会话停止时 |
| `Notification` | 需要通知用户时 |
| `UserPromptSubmit` | 用户提交消息时 |
| `TaskCreated` | 后台任务创建时（v2.1.84 新增）|
| `CwdChanged` | 工作目录切换时（v2.1.83 新增）|
| `FileChanged` | 文件变更时（v2.1.83 新增）|
