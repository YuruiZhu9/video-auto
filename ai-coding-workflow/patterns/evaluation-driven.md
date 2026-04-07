# 评估驱动开发 (Evaluation-Driven Development)

> 来源：imidef.com — Beyond Vibe Coding: How AI Software Development Will Change Next (2026-04-06)

## 核心理念

**验证比生成创造更多杠杆。**

AI 生成的代码质量取决于：在编码之前定义清晰的验证标准。
速度 = 减少返工循环，而非更快的生成。

---

## Practical Spec Handoff Template（五要素规范交接模板）

在向 AI 发送任务前，必须填写以下五项：

| 要素 | 含义 | 示例 |
|------|------|------|
| **Purpose** | 一句话目标 | "为登录页面添加第三方OAuth支持" |
| **Scope** | 精确文件/模块 | "仅修改 `auth/oauth.ts` 和 `pages/login.tsx`" |
| **Constraints** | 禁止变更项 | "不要改动现有邮箱登录逻辑和UI样式" |
| **Acceptance Criteria** | 完成定义 | "Google和GitHub登录可用；token正确存储；登出清除token" |
| **Verification** | 验证命令+预期输出 | "`npm test auth` 全部通过；`curl /api/auth/google` 返回200" |

### 强规范 vs 弱规范对比

| 弱规范（避免） | 强规范（使用） |
|---------------|---------------|
| "改进整体登录" | "仅更新 `auth/validator.ts` 中的邮箱验证逻辑" |
| "优化所有性能" | "不改变面向用户的所有文案和UI" |
| "修Bug并提速" | "为无效邮箱和token过期场景添加测试用例" |

---

## 编码前必做的五项验证定义

1. **单元测试期望**：AI 生成代码对应的测试用例
2. **类型检查要求**：`strict` 模式 / 关键类型的非空断言
3. **Lint 要求**：ESLint/Pylint 通过，无 Warning
4. **回归标准**：现有功能不被破坏的判定条件
5. **UI 差异预期**（如适用）：截图对比或视觉diff

---

## 三习惯起步法

### 个人开发者最小实践
1. 编码前写3行目标
2. 定义完成标准
3. 让 AI 先出计划
4. 实现后运行验证命令
5. 接受前审查 diff

### 团队资产清单（稳定 AI 输出）
- Issue 模板（强制 Purpose/Scope/Constraints/Acceptance Criteria）
- 共享验收标准
- 必须的测试关卡
- Review 标准
- 工具权限策略
- 生产审批流程

---

## Vibe Coding 适用场景矩阵

| ✅ 适用（绿色区） | ❌ 脆弱/慎用（红色区） |
|------------------|----------------------|
| 绿地原型（Greenfield prototypes） | 大规模多文件重构 |
| UI 探索（UI exploration） | 安全/权限敏感变更 |
| 小脚本（Small scripts） | 需团队审查的生产系统 |
| 早期构思（Early ideation） | 长期维护服务 |

---

## 五层 AI 开发栈（buildbetter.ai 2026）

| 层级 | 用途 | 代表工具 |
|------|------|---------|
| **L1. IDE 助手** | 行级代码加速和探索 | Copilot, Claude Code, Cursor |
| **L2. Agent 工具** | 自主处理复杂多文件任务 | Claude Code Auto Mode, Cursor Composer |
| **L3. Skills 库** | 将团队知识和质量标准编码为可复用指令 | Anthropic Skills, Claude Code Hooks |
| **L4. AI 测试** | 填补 AI 生成代码的覆盖率缺口 | AI-generated tests, CI integration |
| **L5. AI 代码审查** | Merge 前的最终质量门 | Review Sandwich, AI PR review |

**效果**：使用完整五层栈的团队 vs 单工具团队，功能交付速度提升 **40-60%**。

---

## Review Sandwich 双层审查法

见 `patterns/multi-agent-workflows.md` Section 47 详细说明。

简述：
- **底层**：AI 先行审查（风格违规/常见 Bug/文档缺口）
- **顶层**：人类聚焦架构/业务逻辑/AI 易漏边界情况
- **效果**：人类审查时间 **-30-50%**，同时保持或提升缺陷检出率

---

## 2026 后展望

来源：imidef.com, primary sources (OpenAI Codex, GitHub Copilot, Google Agent Mode, Anthropic MCP)

- 更多任务委托给编码 Agent
- 更多 Plan-and-Approve 工作流
- 验证质量而非生成速度成为竞争焦点
- 工具连接的 Agent 集成更多
- 决策质量和风险控制能力差距扩大
- 完全无监督自主权：在严肃生产环境中仍不现实；审批、权限、Review 和安全护栏仍是核心

**人类价值高地**：问题框架设计 > 优先级排序 > 约束设计 > 验收标准设计 > 风险审查 > 异常处理 > 最终责任归属
