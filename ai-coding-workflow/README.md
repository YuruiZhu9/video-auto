# AI Coding 工作流指南

> 长期更新的AI协作开发实践文档，助你养成良好的开发习惯和思路清晰的规划。

## 核心原则

| 原则 | 说明 |
|------|------|
| **分阶段推进** | 需求 → 架构 → 规划 → 实现 → 审查 → 交付 |
| **上下文管理** | 用CLAUDE.md记录项目约定，用SPEC.md定义需求 |
| **小步迭代** | 每轮对话聚焦单一任务，避免多任务混杂 |
| **验证驱动** | 先写测试，再写代码（TDD思路） |

## 快速开始

### 与AI协作的标准流程

```
1. 需求定义     → 写出清晰的PRD或描述
2. 架构设计     → 让AI先画架构图/数据流
3. 任务拆分     → 拆解成可执行的TODO
4. 逐个实现     → 每个任务完成后验证
5. 代码审查     → 让AI自审或交叉审
6. 交付部署     → 确保可运行可部署
```

### 推荐的项目结构

```
项目根目录/
├── CLAUDE.md          # AI入口指南（必读）
├── SPEC.md            # 需求规格说明
├── .claude/           # Claude Code配置
│   ├── commands/      # 自定义斜杠命令
│   ├── workflow/      # 工作流阶段定义
│   └── rules/         # 代码规范约束
└── src/               # 业务代码
```

## 文档索引

### 阶段指南
- [01-需求分析](./phases/01-requirement.md) — 如何清晰地描述需求
- [02-架构设计](./phases/02-architecture.md) — 架构决策和设计模式
- [03-任务规划](./phases/03-planning.md) — 任务拆分与优先级
- [04-代码实现](./phases/04-codegen.md) — 编码规范与AI协作技巧
- [05-代码审查](./phases/05-review.md) — 审查要点与改进建议
- [06-部署交付](./phases/06-deployment.md) — 部署流程与验证

### 模式与实践
- [Prompt工程](./patterns/prompt-engineering.md) — 高效提问的艺术
- [上下文管理](./patterns/context-management.md) — 上下文传递与记忆
- [调试策略](./patterns/debugging-strategies.md) — 有效定位问题
- [代码规范](./patterns/code-standards.md) — 团队编码约定

### 更新日志
- [2026年3月](./notes/2026-03.md) — 最新更新

---

*此文档由AI自动维护，定期更新最新实践*
