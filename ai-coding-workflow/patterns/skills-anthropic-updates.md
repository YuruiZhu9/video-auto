# Skills 系统 — Anthropic Skills 仓库最新更新 (2026-03-27)

> 来源：[github.com/anthropics/skills](https://github.com/anthropics/skills) | ⭐ 52.3k Stars | 最后更新：2025-12-20

---

## 仓库概览

| 指标 | 数值 |
|------|------|
| Stars | 52.3k |
| Forks | 5.1k |
| 技能总数 | 16+ |
| 最后提交 | 2025-12-20（添加 agentskills.io 规范链接）|
| 主要贡献者 | klazuka, claude（Anthropic 官方）|

**仓库结构：**
```
skills/
├── docx/          # Word 文档创建与编辑（源开放）
├── pdf/           # PDF 操作（源开放）
├── pptx/          # PowerPoint 创建（源开放）
├── xlsx/          # Excel 电子表格（源开放）
├── doc-coauthoring/   # 🆕 文档协作工作流（2025-12-04）
├── frontend-design/    # 🆕 前端设计（2025-12-04）
├── slack-gif-creator/ # 🆕 Slack GIF 创建器（2025-12-04）
├── mcp-builder/       # MCP Server 构建器
├── skill-creator/     # 技能创建指南
├── webapp-testing/    # Web 应用测试
├── algorithmic-art/   # 算法艺术
├── brand-guidelines/  # 品牌指南
├── canvas-design/     # Canvas 设计
├── theme-factory/     # 主题工厂
├── web-artifacts-builder/  # Web Artifacts 构建器
├── internal-comms/    # 内部沟通
spec/               # Agent Skills 规范（agentskills.io）
template/           # 技能模板
```

---

## 🆕 新增技能详解

### 1. doc-coauthoring（文档协作）

> **触发条件**：用户提到写文档、提案、规范、PRD、RFC、技术规格等写作任务时激活。
>
> **文件**：`skills/doc-coauthoring/SKILL.md` | 最后更新：2025-12-04

**三阶段工作流：**

```
Stage 1: Context Gathering（上下文收集）
   ↓ 用户提供背景/meta-context
Stage 2: Refinement & Structure（精炼与结构）
   ↓ 分节头脑风暴→编辑→迭代
Stage 3: Reader Testing（读者测试）
   ↓ 用子 Agent 模拟真实读者
   完成
```

**Stage 1 关键要点：**
- 元问题：文档类型、受众、预期影响、格式模板、约束
- 支持多方式提供上下文：stream-of-consciousness、指向频道/文档、集成拉取（Slack/Teams/GDrive）
- 澄清问题生成：5-10 个基于上下文缺口的问题
- 退出条件：当可以询问边缘情况而不需解释基础时，说明上下文足够

**Stage 2 关键要点：**
- 每个 section 走 6 步：澄清问题→头脑风暴（5-20项）→筛选→缺口检查→起草→迭代精炼
- 使用 `str_replace` 进行精准编辑（永远不重印整个文档）
- 连续 3 次迭代无实质性改动时，主动问"有没有可以去掉的内容"
- 接近完成时（80%+ sections）全文通读检查流畅性/冗余/矛盾

**Stage 3 关键要点（读者测试）：**
- 预测读者问题（5-10 个）
- 用子 Agent 测试（Claude Code 环境）或让用户手动在新对话中测试
- 检查歧义、矛盾、隐含假设
- 问题修复后循环回 Stage 2

**核心原则：** 文档的价值在于读者真正读懂并据此行动。协作工作流确保上下文充分、逻辑清晰、读者验证通过。

---

### 2. frontend-design（前端设计）

> **触发条件**：用户要求构建 Web 组件、页面、落地页、仪表盘、React 组件、HTML/CSS 布局，或任何 UI 样式/美化任务。
>
> **文件**：`skills/frontend-design/SKILL.md` | 许可证：Apache 2.0 | 最后更新：2025-12-04

**设计思维框架（做之前必先理解）：**
```
Purpose   → 这个界面解决什么问题？谁用？
Tone      → 选择一个极端方向：
            - 极简主义 / 极繁主义 / 复古未来主义
            - 有机自然 / 奢华精致 / 玩具感
            - 杂志编辑风 / 粗野主义 / 艺术装饰几何
            - 柔和粉彩 / 工业实用 / ...
Constraints → 技术要求（框架、性能、可访问性）
Differentiation → 一个让人记住的点是什么？
```

**反"AI slop"美学清单：**

❌ **禁止使用：**
- 通用字体：Arial、Inter、Roboto
- 俗套配色：白底紫色渐变
- 套路布局：居中卡片+投影
- 无差异化设计（与其他 AI 生成物相似）

✅ **必须追求：**
- **字体**：独特显示字体 + 精致正文字体配对
- **色彩**：主导色 + 锐利强调色（均匀分布的 timid palette 是失败）
- **动效**：CSS-only 优先；React 用 Motion 库；聚焦高冲击时刻（页面加载时的错落揭示）
- **空间**：不对称、重叠、斜向流动、网格破坏、大量负空间 OR 受控密度
- **背景**：纹理/渐变/噪点/几何图案/装饰阴影/自定义光标/颗粒叠加

**实现原则：** 实现复杂度要匹配美学愿景。极繁需要复杂代码+大量动画；极简需要克制、精度和间距的精细关注。

---

### 3. slack-gif-creator（Slack GIF 创建器）

> **触发条件**：用户请求为 Slack 创建动画 GIF，如"做一个 X 做 Y 的 Slack GIF"。
>
> **文件**：`skills/slack-gif-creator/SKILL.md` | 许可证：Apache 2.0

**Slack GIF 技术规格：**
| 类型 | 推荐尺寸 | FPS | 色彩数 | 时长 |
|------|---------|-----|-------|------|
| Emoji GIF | 128×128 | 10-15 | 48 | ≤3s |
| 消息 GIF | 480×480 | 15-20 | 48-128 | ≤5s |

**Python 技术栈：**
```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

builder = GIFBuilder(width=128, height=128, fps=10)
# 生成帧...
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

**动画概念（8种基础模式）：**
| 模式 | 原理 | 适用场景 |
|------|------|---------|
| Shake/Vibrate | `sin()` 震动位移 | 通知图标、警告 |
| Pulse/Heartbeat | `sin()` 缩放（0.8-1.2x）| 心跳、爱心 |
| Bounce | 重力加速 + `bounce_out` 缓动 | 弹跳球 |
| Spin/Rotate | 绕中心旋转 | 加载、刷新 |
| Fade | alpha 渐变 | 淡入淡出 |
| Slide | 从屏外滑入 + `back_out` | 入场动画 |
| Zoom | 缩放+裁剪中心 | 放大镜效果 |
| Explode | 粒子向外扩散+重力 | 爆炸效果 |

**优化策略：**
- 减少帧数（FPS 20→10）
- 减少色彩数（128→48）
- 缩小尺寸（480→128）
- 去除重复帧（`remove_duplicates=True`）

---

## Agent Skills 规范（agentskills.io）

> 2025-12-20 重大更新：仓库 README 顶部新增了对 agentskills.io 的引用，将该网站作为 Agent Skills 标准的权威来源。

**规范核心要点（来自 agentskills.io）：**

- **技能定义**：技能的文件夹（包含 `SKILL.md`）是 Claude 动态加载以提升特定任务性能的指令集
- **元数据**：只需两个 frontmatter 字段：`name`（唯一标识符）+ `description`（完整描述）
- **加载机制**：Claude 在相关场景下自动使用技能
- **使用方式**：
  - Claude Code：`/plugin install <skill>@anthropic-agent-skills`
  - Claude.ai：付费用户直接可用
  - Claude API：Skills API

---

## claude-code-guide（zebbern）— 全面参考

> 来源：[github.com/zebbern/claude-code-guide](https://github.com/zebbern/claude-code-guide) | ⭐ 3.1k Stars | MIT License

### 内置子 Agent（5种）

| Agent | 类型 | 职责 |
|-------|------|------|
| **planner** | 只读 | 将功能/问题拆解为小型可测试任务，输出任务列表或 plan.md |
| **codegen** | 可编辑 | 实现任务，限定于 `src/` + `tests/` |
| **tester** | 只读/补丁 | 编写一个失败的测试或最小复现 |
| **reviewer** | 只读 | 留下结构化审查评论，永不编辑 |
| **docs** | 可编辑 | 仅更新 `README.md` / `docs/` |

### 核心命令（28个）

```
/add-dir     添加工作目录    /agents      管理自定义子 Agent
/bug         报告 Bug       /clear       清空会话历史
/compact     压缩会话        /config      查看/修改配置
/cost        显示 Token 使用 /doctor      检查安装健康
/help        帮助           /init        初始化项目
/login/logout 账户切换      /mcp         管理 MCP 连接
/memory      编辑 CLAUDE.md /model       选择/切换模型
/permissions 查看/更新权限  /pr_comments 查看 PR 评论
/review      代码审查       /status      查看账户状态
/vim         Vim 模式
```

### Thinking 关键词（Token 消耗递增）

```
think → think hard → think harder → ultrathink
```

### Hook 系统（8种事件）

| 事件 | 时机 |
|------|------|
| `PreToolUse` | 工具执行前 |
| `PostToolUse` | 工具完成后 |
| `Notification` | Claude 需要权限或空闲 |
| `UserPromptSubmit` | 用户提交 prompt |
| `Stop` | 主 Agent 完成响应 |
| `SubagentStop` | 子 Agent 完成响应 |
| `PreCompact` | 执行 compact 操作前 |
| `SessionStart` | 新会话开始 |

### MCP 服务器推荐

| 服务器 | 命令 | 用途 |
|--------|------|------|
| filesystem | `npx -y @modelcontextprotocol/server-filesystem` | 直接文件读写 |
| github | `npx -y @modelcontextprotocol/server-github` | 管理 issue/PR/代码审查 |
| puppeteer | `npx -y @modelcontextprotocol/server-puppeteer` | 自动化 Web 操作 |
| postgres | `npx -y @modelcontextprotocol/server-postgres` | 数据库查询 |
| fetch | `npx -y @kazuph/mcp-fetch` | REST API 调用 |
| brave-search | `npx -y @modelcontextprotocol/server-brave-search` | 搜索引擎 |
| slack | `npx -y @modelcontextprotocol/server-slack` | 发送消息、管理频道 |
| memory | `npx -y @modelcontextprotocol/server-memory` | 跨会话保存信息 |
| thinking | `npx -y @modelcontextprotocol/server-sequential-thinking` | 逐步思考 |

### GitHub Actions 工作流

**Auto PR Review：**
```yaml
# 触发：PR open/sync/reopen/ready_for_review
# 功能：创建结构化审查 + 行内评论
# 工具：GitHub MCP tools
```

**Security Review on Every PR：**
```yaml
# 触发：pull_request
# 功能：专注安全扫描
# 输出：直接在 PR 上评论发现
```

**Issue Triage：**
```yaml
# 触发：issue opened/edited/reopened
# 功能：建议标签和严重级别
# 可选：自动应用标签
```

### 配置文件层级

| 类型 | 位置 |
|------|------|
| 企业政策 | `/etc/claude-code/CLAUDE.md`（Linux）/ `~/Library/Application Support/ClaudeCode/CLAUDE.md`（macOS）|
| 项目内存 | `./CLAUDE.md` |
| 用户内存 | `~/.claude/CLAUDE.md` |
| 本地覆盖 | `./CLAUDE.local.md` |
| 全局配置 | `~/.claude.json` |
| MCP 配置 | `.mcp.json` |

---

## 使用建议

1. **doc-coauthoring** 适合所有需要写技术文档、PRD、RFC 的场景，可直接引导用户进入结构化协作流程
2. **frontend-design** 是反 AI slop 的设计指南，适合 UI 开发任务
3. **slack-gif-creator** 提供了完整的 Slack GIF 技术约束和动画概念
4. **claude-code-guide** 的子 Agent 模式（planner/codegen/tester/reviewer/docs）值得在 OpenClaw 中参考实现
5. **GitHub Actions 工作流**（PR Review/Security Review/Issue Triage）是 AI Agent 自动化集成的优秀案例


---

## 🆕 Anthropic 内部 Skills 实战指南（toolin.ai 2026-03）

> **来源：** toolin.ai "Anthropic内部实战：如何用 Skills 让 Claude Code 效率翻倍" | [原文](https://toolin.ai/blog/claude-code-skills-guide)
> **作者：** Thariq Shihipar（Anthropic Claude Code 团队工程师）

这是 Claude Code 团队工程师的一手经验分享，揭秘 Anthropic 内部数百个 Skills 的分类体系、编写技巧和分发策略。

---

### 9大 Skills 类型（Anthropic 内部分类体系）

| 类型 | 说明 | 代表示例 |
|------|------|---------|
| **1. 库与 API 参考** | 帮助正确使用某个库、CLI工具或SDK | billing-lib、frontend-design |
| **2. 产品验证** | 描述如何测试/验证代码是否正常工作 | signup-flow-driver、checkout-verifier |
| **3. 数据获取与分析** | 连接数据和监控体系 | funnel-query、grafana |
| **4. 业务流程与团队自动化** | 将重复性工作流自动化 | standup-post、weekly-recap |
| **5. 代码脚手架与模板** | 为特定功能生成框架样板代码 | new-workflow、create-app |
| **6. 代码质量与审查** | 执行代码质量标准和辅助审查 | adversarial-review、code-style |
| **7. CI/CD 与部署** | 拉取、推送和部署代码 | babysit-pr、deploy-service |
| **8. 运维手册** | 接收现象引导排查流程，生成结构化报告 | service-debugging、oncall-runner |
| **9. 基础设施运维** | 执行日常维护和运维操作（需安全护栏）| cleanup-orphans、cost-investigation |

**核心原则：** 最好的 Skills 清晰落在某一类别，横跨多类的 Skills 容易让人困惑。

---

### 编写 Skills 的 8 个技巧（官方一手经验）

#### 1. 不要说显而易见的事
Claude Code 对代码库已经很了解，对编程也很在行。重点放在能打破 Claude 常规思维模式的信息上。
- ✅ 有效信息：踩坑点、边界情况、容易出错的用法
- ❌ 避免：语言基础、常见语法、显而易见的实现

#### 2. 建一个踩坑点章节（⚠️ 最重要的技巧）
这是信息量最大的部分，应该根据 Claude 使用时的常见失败点逐步积累，持续更新记录新踩坑点。
> 大多数 Skills 一开始就是几行文字加一个踩坑点章节。

#### 3. 利用文件系统与渐进式披露
Skills 是文件夹，不只是 markdown 文件。把详细函数签名和用法示例拆分到独立文件中（`references/api.md` 等），按需加载。

#### 4. 不要把 Claude 限制得太死
给 Claude 需要的信息，但留给它适应具体情况的灵活性。指令不要太具体，因为 Skills 复用性强。

#### 5. 考虑好初始设置
需要用户提供上下文时，把配置信息存在 Skill 目录下的 `config.json` 文件里。如果配置未设置，智能体会向用户询问。

#### 6. description 字段是给模型看的（⚠️ 关键规范）
Claude Code 启动时构建所有可用 Skills 及其描述的清单，Claude 通过扫描这份清单判断是否触发 Skill。
- ✅ `description` 描述的是**何时该触发**，不是功能摘要
- ❌ 避免：`"This skill does X"` 类型的描述

#### 7. 记忆与数据存储
可以用追加写入的日志文件、JSON 文件或 SQLite 数据库实现记忆功能。
- 示例：`standup-post` 可以保留 `standups.log` 记录历史站会汇报

#### 8. 存储脚本与生成代码
给 Claude 提供脚本和库，让它把精力花在组合编排上，而不是重新构造样板代码。

---

### Skills 分发策略

| 分发方式 | 适用场景 |
|---------|---------|
| 代码仓库提交 | `./.claude/skills` 目录 |
| 插件市场 | 搭建内部插件市场，让团队成员自行决定安装哪些 |

---

### 实施路线图

1. **从最痛的点开始**：先做 1-2 个解决团队最大痛点的 Skills
2. **持续迭代**：根据 Claude 实际使用情况补充踩坑点
3. **建立分享机制**：鼓励团队成员贡献和改进
4. **衡量效果**：使用 `PreToolUse` 钩子记录使用情况

**验证类 Skills（类型2）值得重点投入：** 值得花一周时间专门打磨，一旦做好，长期节省大量重复验证时间。

---

## anthropics/skills 仓库增量更新（2026-03-27 检查）

### 最新提交记录

| 日期 | 作者 | 内容 |
|------|------|------|
| 2026-03-25 | cc-skill-sync[bot] | 更新 claude-api skill（13文件批量同步）|
| 2026-03-22 | cc-skill-sync[bot] | 更新 claude-api skill |
| 2026-03-06 | zack-anthropic | skill-creator: 移除 `ANTHROPIC_API_KEY` 要求，改为 `claude -p` 子进程调用 |
| 2026-03-04 | Eric Harmeling | 新增 claude-api skill（515）|

### skill-creator 重大改进（2026-03-06）

**变更：** `improve_description.py` 不再依赖 ANTHROPIC_API_KEY，改用 `claude -p` 子进程调用认证。
- **用户收益**：无需单独配置 API Key 即可运行描述优化循环
- **认证模式**：与 `run_eval.py` 一致，复用现有 Claude Code 认证

### claude-api skill 新增内容（2026-03-04）

`claude-api` skill 正式加入仓库，提供多语言 SDK 参考：
- Python（agent-sdk / claude-api）
- TypeScript（agent-sdk / claude-api）
- Go / Ruby / PHP / Java / C# / curl
- `shared/` 目录：prompt-caching.md、tool-use-concepts.md

### claude-code-guide 增量更新（2026-03-01）

| 日期 | 作者 | 内容 |
|------|------|------|
| 2026-03-01 | zebbern | 重构 README 结构 + 新增资源链接 |
| 2026-03-01 | zebbern | 更新安全 Agent skill 链接 |
| 2026-02-28 | zebbern | 新增 Chrome/Sandbox/LSP 章节 + 5 个新 flags |
| 2026-02-28 | zebbern | 更新 README（新增环境变量和功能）|

Auto-sync bot 每日同步 Claude Code CHANGELOG（2026-03-26 已覆盖 v2.1.84）。

---

## 使用建议（综合更新）

1. **Auto Mode**：Claude Code 新增的自主执行模式，适合需要 AI 长时间独立运行的任务（需配合沙箱环境）
2. **Anthropic Skills 9分类**：参考此分类体系为自己的团队设计 Skills，避免跨类混乱
3. **skill-creator 改进**：Anthropic 官方不再强制要求 ANTHROPIC_API_KEY，降低了 Skill 开发的门槛
4. **claude-api skill**：多语言 SDK 参考现已加入官方仓库，适合 API 集成开发
5. **验证类 Skills 优先投入**：产品验证类（Playwright/tmux 集成）值得重点打磨
