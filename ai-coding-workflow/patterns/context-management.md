# 上下文管理 - 与AI保持清晰的信息流

## 为什么上下文重要

AI没有长期记忆，每次对话都是独立的。清晰的上下文 = 高效的协作。

## CLAUDE.md 项目记忆文件

在项目根目录创建，让AI快速了解项目：

```markdown
# Project Name

## Tech Stack
- Node.js 18+
- React 18 + TypeScript
- PostgreSQL

## Commands
- `npm run dev` - 启动开发服务器
- `npm test` - 运行测试

## Code Style
- 使用函数式组件
- Hooks命名：useXxx
- CSS使用Tailwind

## Project Structure
- /src/components - UI组件
- /src/hooks - 自定义Hooks
- /src/api - API调用
```

## 上下文传递技巧

### 1. 开场说明上下文
> "继续之前的用户登录功能，现在需要添加登出功能"

### 2. 提供关键信息
> "数据库用户表结构是：id, email, password_hash, nickname"

### 3. 及时压缩上下文
当对话很长时：
> "压缩一下之前的对话，保留核心信息"

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 上下文太长 | 用/compact压缩 |

---

## 🔴 2026最大范式转变：Context Engineering（上下文工程）

> 这是2026年AI Coding领域最重要的范式迁移——从"Prompt Engineering（提示词工程）"升级为"Context Engineering（上下文工程）"。

### 核心定义

**Context Engineering = 设计和管理AI系统工作内存中的所有信息，使其能理解意图、做出正确决策、交付一致结果。**

| 对比维度 | Prompt Engineering | Context Engineering |
|----------|-------------------|---------------------|
| 核心焦点 | 优化单条指令的措辞 | 管理AI的整个工作内存 |
| 比喻 | 磨刀 | 打造整个工作台 |
| 效果 | 边际改进 | 显著跃升 |
| Gartner数据 | 基准 | **50%响应速度提升，40%输出质量提升** |

### 为什么现在发生

- **2025年中**：Shopify CEO Tobi Lütke 和前 OpenAI 研究员 Andrej Karpathy 公开支持
- **2025下半年**：LangChain、Anthropic、LlamaIndex 正式采纳
- **2026**：Agentic AI（57%组织已在生产环境）+ SLM普及 → 上下文管理成为最大瓶颈

### 类比：LLM = CPU，Context = RAM

```
CPU (LLM)        RAM (Context Window)
─────────────────────────────────────
处理能力    ←→    模型智能
工作内存    ←→    上下文窗口
缓存优化    ←→    上下文工程
```

**Context Window 里装的东西：**
- 系统指令（角色定义、行为规则）
- 检索到的文档（RAG）
- 对话历史
- 工具定义（Tools/MCPs）
- 用户偏好
- 当前状态信息

### Context Engineering 的四大支柱

| 支柱 | 说明 | 实践 |
|------|------|------|
| **检索管道** | 精准获取相关上下文 | RAG、向量化搜索、语义检索 |
| **记忆管理** | 跨会话持久化关键信息 | CLAUDE.md、项目规则、Memory Bank |
| **动态组装** | 根据任务实时组装最优上下文 | CTCO/CRISP框架、角色-任务映射 |
| **上下文压缩** | 保持关键信息密度 | /compact、摘要提取、关键信息保留 |

### 关键最佳实践

**1. 把上下文当作第一公民**
- 不要只优化Prompt，先确保上下文里有正确的信息
- 信息质量 > 指令措辞

**2. 上下文信息架构（Information Architecture）**
- LLM准确率在相关信息嵌入长上下文中时下降 **24.2%**
- 关键信息要突出（用分隔符、XML标签、明确标注）
- 无相关信息要主动排除

**3. CTCO 框架（OpenAI GPT-5.2）— 上下文组装的工程化方法**

| 组件 | 说明 | 示例 |
|------|------|------|
| **C - Context** | 完整的技术背景 | "Node.js + Express，JWT认证，PostgreSQL数据库" |
| **T - Task** | 明确的任务目标 | "实现用户注册API，包含邮箱验证" |
| **C - Constraints** | 明确的约束条件 | "不修改现有迁移文件，响应时间<200ms" |
| **O - Output** | 可量化的完成标准 | "POST /register返回201，测试覆盖率>80%" |

**CTCO vs CRISP 对比：**

| 维度 | CTCO | CRISP |
|------|------|-------|
| 侧重点 | 上下文 → 任务 → 约束 → 输出 | 角色 → 任务 → 规格 → 润色 |
| 来源 | OpenAI GPT-5.2 | Dev.to CRISP Framework |
| 适用场景 | 结构化、工程化任务 | 探索性、设计性任务 |
| 互补性 | 强调"边界" | 强调"角色理解" |

**4. 小语言模型（SLM）需要更精准的上下文**
- SLM对歧义容忍度更低
- 需要更明确的指令、更具体的约束
- AT&T案例：90% API成本下降，70%响应速度提升
  - 架构：大推理模型做"主控制器"规划 + 专用SLM执行任务

**5. 多模态上下文的 Progressive Specificity Pattern**
```
Step 1: 宽泛模态输入（图片/文档）
Step 2: 文字指令引导注意力（"关注右下角的图表"）
Step 3: 明确约束输出格式
```

### 从"写Prompt"到"建系统"的转变

| 旧范式 | 新范式 |
|--------|--------|
| 优化单条Prompt | 设计上下文架构 |
| 等待模型猜对 | 确保信息到位 |
| 一次想清楚 | 动态组装最优上下文 |
| Prompt工程师 | Context架构师 |

**岗位演变信号：**
- "Prompt Engineer"职位名称下降约40%（2024-2025）
- 被吸收到：AI Developer、AI Workflow Designer、Generative AI Strategist
- LinkedIn上要求Prompt技能的岗位增长250%

**学习路径建议：**
```
Level 1: 会写Prompt（基础）
Level 2: 会组装上下文（进阶）← 当前主流
Level 3: 会设计上下文架构（Context Engineering）← 2026发展方向
Level 4: 会编排多Agent + 工具 + 记忆系统（完整AI系统）
```
| AI忘了之前的内容 | 重新提供关键信息 |
| 多任务混杂 | 分成多个对话处理 |

## 11. 上下文获取工具链（Addy Osmani 2026推荐）

**来源：** [Addy Osmani — My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/)

Addy Osmani 在原文中明确推荐了三款将代码库打包为 AI 可用上下文的专用工具，这是 Context Engineering 落地的关键基础设施：

| 工具 | 用途 | 地址 |
|------|------|------|
| **Context7** | 提取代码库结构化为 AI 友好文本 | context7.com |
| **gitingest** | 将 Git 历史 + 代码库转为 prompt 友好文本 | github.com/upskdigital/gitingest |
| **repo2txt** | 代码仓库转文本，用于 AI 上下文投喂 | github.com/CluedIn-io/repo2txt |

### 核心使用场景

```bash
# Context7：上传代码库，获取结构化上下文片段
# → 适合：需要 AI 理解特定模块时

# gitingest：整个 repo 转可读文本，包含变更历史
# → 适合：需要 AI 理解项目演进脉络时

# repo2txt：完整仓库转文本，最大化上下文覆盖率
# → 适合：新 Claude 会话启动时快速加载全貌
```

### 与 CLAUDE.md 的协同

```
CLAUDE.md        → 项目规范和约束（人类维护）
repo2txt         → 当前代码状态（自动同步）
gitingest        → 历史上下文和变更原因
Context7         → 精准定位特定模块的上下文
```

> **Addy Osmani 的实践**：在每个 Claude Code 会话开始时，用 Context7/gitingest 加载代码库上下文，而不是仅靠 CLAUDE.md——因为 CLAUDE.md 是人类维护的摘要，而这三个工具可以自动同步最新代码状态。

### Claude Skills（指令打包为可复用模块）

Addy Osmani 同时提到 Anthropic 的 **Claude Skills** 系统：将一组指令打包为可复用的模块化技能包，供 Agent 在不同任务中调用。

**适用场景：**
- 团队标准化 AI 工作流
- 重复性任务自动化
- 专业领域知识封装（如"安全审查技能包"、"API设计技能包"）

---

## 12. 精细化上下文控制：.claudeignore + MCP CLI（aiorg.dev 2026）

**来源：** [aiorg.dev — Claude Code Best Practices: 15 Tips from 6 Projects (2026)](https://aiorg.dev/blog/claude-code-best-practices)

两项此前文档未显式收录的上下文控制工具：

### .claudeignore — 排除无关文件，减少上下文噪音

在项目根目录创建 `.claudeignore`，告诉 Claude Code 忽略哪些文件，避免无关内容占用宝贵的上下文窗口：

```
# .claudeignore
node_modules/
.next/
dist/
*.lock
*.log
coverage/
.env*
.git/
*.min.js
__pycache__/
```

**效果：** 减少无关 token 消耗 → 更快、更准确的响应

### MCP CLI 全套命令（zhuanlan.zhihu 2026）

Claude Code 内置 MCP 管理命令，支持项目级（local）和全局（user）两种作用域：

```bash
# 列出所有已配置的 MCP 服务
claude mcp list

# 移除指定 MCP 服务
claude mcp remove <服务名>

# 重启指定 MCP 服务（调试时常用）
claude mcp restart <服务名>

# 添加项目级 MCP（local scope，仅当前用户当前项目可用）
claude mcp add-json <服务名> -s local '{"command":"npx","args":["-y","服务包名"]}'

# 添加全局 MCP（user scope，跨所有项目生效）
claude mcp add-json <服务名> -s user '{"command":"npx","args":["-y","服务包名"]}'
```

**MCP Scope 三级权限体系：**

| Scope | 曾用名 | 可见范围 | 共享方式 |
|-------|--------|----------|----------|
| `local` | project | 仅当前用户当前项目 | 不共享 |
| `project` | — | 全体项目成员（通过 `.mcp.json`） | 提交到 Git 协作 |
| `user` | global | 当前用户所有项目 | 不共享 |

**典型场景：**
- `local` scope：团队项目专属的数据库 MCP（如 `mysql-mcp`）
- `user` scope：个人效率 MCP（如 `promptx`）

### CLAUDE.md 体系完整结构（aiorg.dev 2026 新增）

将上下文管理组件打包为可迁移的完整套件：

```
.claude/
├── CLAUDE.md           # 主项目规范（必选）
├── .claudeignore       # 上下文噪音过滤（新增）
├── commands/           # 自定义快捷命令
│   ├── new-feature.md  # 一句话创建完整功能
│   ├── deploy.md
│   └── test-all.md
├── rules/              # 领域专属规则（按需加载）
│   ├── api-rules.md    # 写 API route 时触发
│   ├── database.md     # 写数据库代码时触发
│   └── testing.md      # 写测试时触发
└── knowledge/          # 架构文档等长文本参考
    └── architecture.md
```

**迁移价值：** 将 `.claude/` 目录复制到任何新项目，Claude Code 立即理解你的标准，无需每次重新配置。

---

## 进阶技巧

### 使用System Prompt
在项目根目录创建`.claude/settings.json`：
```json
{
  "instructions": "你是React专家，代码风格参考Airbnb规范"
}
```

### 分阶段记忆
- 每个阶段生成总结
- 下个阶段基于总结继续

---

## 13. 2026 市场数据与行业趋势（🆕 2026-03）

**来源：** eastondev.com AI Tools Panorama 2026，2026-03

### 市场规模与采用率

| 指标 | 数据 | 来源 |
|------|------|------|
| 市场规模（2026） | $128 亿 | eastondev.com |
| 开发者采用率 | 85%（JetBrains 调查） | eastondev.com |
| 日常任务时间节省 | 46% | eastondev.com |
| Copilot 用户数 | 2,000 万（截至 2025-07） | eastondev.com |
| Gartner 预测（2026年底） | 40% 企业应用将嵌入 AI Agent | eastondev.com |

### AI Coding 工具三大类别

| 类别 | 代表工具 | 特点 |
|------|---------|------|
| **AI IDE**（AI 重构编辑器） | Cursor、Windsurf、Antigravity | AI 为核心，不是插件 |
| **Code Assistant**（IDE 插件） | GitHub Copilot、Tabnine、JetBrains AI | 依附现有编辑器 |
| **Coding Agent**（2026 最热） | Claude Code、Cline、Gemini CLI、Codex | 自主规划、执行、测试、修改 |

### 成本基准

| 方案 | 日成本 | 年成本 |
|------|--------|--------|
| Cline + DeepSeek（极低成本） | $0.10–0.30/天 | ~$25–75/年 |
| GitHub Copilot | ~$0.33/天 | $120/年 |
| Claude Code（按量） | 几分钱–几元/天 | 视使用量 |
| Cursor Pro | ~$0.67/天 | $240/年 |

### ⚠️ 重要警示：AI 辅助代码缺陷率

> **eastondev.com 2026-03：AI 辅助代码的缺陷率是人工代码的 4 倍**
> 这不意味着 AI 代码质量差，而是提醒：不能盲目信任 AI 输出

**推荐做法：**
1. 对 AI 修改的代码进行人工 review
2. 为关键模块编写测试
3. 定期进行代码审计
4. 安全/支付模块使用额外审查层

---

## Section 13 — Front-Load Context（上下文前置原则）

**来源：** dev.to/dohkoai "5 Vibe Coding Workflows"（基于264个生产框架实战经验）

### 核心原则

> "Feed it: AGENTS.md, relevant source files, test output. Then ONE clear task."

**先投喂上下文，再给单一任务**，远比"给详细指令列表"更有效。

### 操作对比

```
❌ 传统方式（指令堆叠）
"请依次完成以下任务：1. 修改 auth/middleware.ts...
 2. 更新 users 表结构...
 3. 添加测试..."

✅ AI-Native 方式（上下文前置）
第一步：提供上下文
  - /read auth/middleware.ts
  - /read users/table-schema.sql
  - /read tests/auth.test.ts
  - 项目背景（AGENTS.md）

第二步：给出单一指令
  "修改 auth/middleware.ts 中的 JWT 验证逻辑，
   满足 users 表的新结构，运行测试确认通过"
```

### 为什么有效

| 维度 | 详细指令方式 | 上下文前置方式 |
|------|------------|-------------|
| AI 理解深度 | 浅（靠指令描述）| 深（直接读取源文件）|
| 上下文准确性 | 低（可能被误解）| 高（事实来源）|
| Token 效率 | 低（大量描述性文字）| 高（精准结构化）|
| 变更一致性 | 差（多任务容易跑偏）| 好（单一任务聚焦）|

### 适用场景

**✅ 适合上下文前置：**
- 跨多文件的逻辑变更（AI需要理解完整上下文）
- 架构性重构（AI需要看到现有设计）
- Bug修复（AI需要看到相关代码和测试）
- 复杂功能开发（AI需要理解业务上下文）

**❌ 不需要刻意前置：**
- 简单格式化 / 样板代码生成
- 单文件内的微小调整
- 已有充分 CLAUDE.md 说明的常规任务

### 配套最佳实践

1. **CLAUDE.md 始终前置**：每次会话开始时 `/read CLAUDE.md`
2. **测试输出前置**：Bug修复前先展示失败的测试输出
3. **Broken 行为前置**：先描述问题表现，再给修复任务
4. **小步迭代**：大任务拆分，每个 chunk 都遵循"上下文前置 → 单一指令"

---

## 🆕 Section 15 — Vibe Coding 红绿区安全边界

**来源：** dev.to/dohkoai（2026-03）

**核心原则：** AI 辅助写 60% 繁琐但定义明确的工作；识别 AI 失败高风险区。

**绿区（AI 适用，安全高效）：**
- 样板代码和脚手架
- 测试生成（已知边界）
- 文档编写
- 经过充分测试的代码重构
- CRUD 操作
- 配置文件和 CI/CD
- 回归测试生成

**红区（AI 高风险，谨慎使用）：**
- 安全关键路径（认证、加密、支付处理）
- 性能关键热循环
- 复杂状态机
- 涉及金钱的逻辑
- 未经充分测试的代码重构
- 专利/合规相关的实现

**Plan 先行原则：** 让 AI 先提方案再写代码，可提前拦截 80% 的错误方案。

**审查重点（每次 AI 输出必查）：**
- 硬编码值 / Magic numbers
- O(n²) 及以上的算法复杂度
- 安全捷径：`eval()`、SQL 字符串拼接、XSS
- 过度工程：引入不必要的抽象层
