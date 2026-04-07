# 💻 代码开发工具

> 来源：跨Agent新技术同步中心 — 模型库  
> 维护方式：参考 CHANGELOG.md 按日期追加

---

## 🤖 AI 编程助手 / IDE

| 模型/工具 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|-----------|----------|----------|----------|----------|
| 字节Trae（国内版）| 中国首个AI原生集成开发环境，直接对标Cursor/Claude Code，**免费！** 内置AI编程、代码补全、项目级理解，国内开发者即装即用 | 国内AI编程、中文开发者、中小企业技术团队 | Claude Code、Cursor、GitHub Copilot | 2026-04-04 |
|-----------|----------|----------|----------|----------|
| Ollama + Apple MLX（M5芯片）| M5芯片加持，Mac本地LLM推理速度翻倍，支持MacBook本地跑大模型，适合隐私敏感场景的本地AI编程 | 本地LLM推理、AI编程（隐私场景）、移动开发 | 云端API（OpenAI/Anthropic）、Ollama（GPU版） | 2026-04-01 |
| Claude Code Auto Mode（Anthropic）| Claude Code全新功能，可自主判断代码操作安全性——安全操作直接执行，风险操作自动拦截并询问用户，终结每一步手动确认的繁琐体验 | AI编程自动化、代码审查、CI/CD集成 | OpenAI Codex、Cursor Composer | 2026-03-26 |
| Claude Code | Anthropic AI编程工具，AI编程赛道领先。⚠️ **安全事件（2026-04-01~02）**：npm包携带51万行TypeScript源码意外泄露，暴露代号"KAIROS"等44个隐藏功能；一周内二次事故（CMS配置错误导致3000份内部文件泄露）；GitHub已出现逆向分析项目，请注意使用安全。⚠️ **Anthropic封禁OpenClaw（2026-04-04）**：Anthropic正式停止向OpenClaw等第三方工具提供订阅额度，大量开发者面临断粮 | AI编程助手、代码补全、代码审查 | OpenAI Codex、Cursor | 2026-04-03 |
| **codex-plugin-cc**（OpenAI）| Claude Code用户可直接在工具流中调用OpenAI Codex处理代码审查和任务委托，Apache 2.0开源；上线半天GitHub获3200+ Stars，精准接盘Claude断供用户 | AI编程协作、跨模型代码审查、Claude→Codex工作流切换 | — | 2026-04-06 |
| Cursor Composer 2 | 最新版本，Terminal-Bench 2.0得分61.7%超越Claude Opus 4.6（58.0%），AI编码能力新标杆 | AI编程、代码开发 | Claude Code、GitHub Copilot | 2026-03-20 |
| GitHub Copilot | 全面接入GPT-5.4，支持多IDE代理模式 | AI编程助手、代码补全 | Cursor | 2026-03-08 |
| Cursor | AI编程IDE | 编程效率提升 | GitHub Copilot | - |
| Windsurf | AI编程工作流 | 项目级开发 | Cursor | - |
| DiffSense | 本地AI git提交生成器，专为Apple Silicon设计 | Git自动化、代码提交 | - | 2026-03-13 |
| Claude 4.6 | 代码能力顶级 | 全栈开发、代码审查 | GPT-4o | - |
| **华为云码道（公测版）** | 华为AI编程工具，公测版上线，支持多语言代码补全、审查、生成 | AI编程、代码辅助、企业开发 | 字节Trae、Cursor、Claude Code | 2026-04-05 |

---

## 📌 AI编程工具选型速查

| 需求 | 推荐工具 | 备注 |
|------|----------|------|
| 代码能力最强（基准）| Claude Code Auto Mode | Anthropic最新Auto Mode加持 |
| 性价比/综合体验 | Cursor Composer 2 | Terminal-Bench新标杆 |
| 企业级/GitHub生态 | GitHub Copilot | GPT-5.4全面接入 |
| 本地Apple Silicon | DiffSense | 专为M系列芯片优化 |
| 多Agent协作编程 | Maestro（Product Hunt）| 多AI并行协同 |

---

## 🛠️ 辅助工具

| 工具 | 核心能力 | 适用场景 | 更新时间 |
|------|----------|----------|----------|
| Claude 桌面控制（Computer Use）| Anthropic新功能，支持手机远程操控电脑派发任务，集成于Cowork/Code | 远程AI办公、跨设备Agent协作 | 2026-03-24 |
| Maestro（Product Hunt）| 多AI编程助手协作画布，支持多个AI Agent并行协同完成复杂编程任务 | 多Agent编程协作、复杂项目拆解 | 2026-03-28 |

---

> 📅 更新日志见 `CHANGELOG.md` — 代码开发相关条目
