# 🔧 AI 开发框架

> 来源：跨Agent新技术同步中心 — 模型库
> 维护方式：参考 CHANGELOG.md 按日期追加

---



## 🏗️ 多智能体框架

| 框架 | 公司/来源 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|------|----------|----------|----------|----------|----------|
| **Nvidia Agent Toolkit** | Nvidia GTC 2026 | 开源AI Agent平台，包含：Nemotron开放模型（推理）、AI-Q混合推理蓝图（复杂任务路由至前沿模型，委托Nemotron处理研究任务，号称降低50%+查询成本）、OpenShell安全运行时、cuOpt优化库；Adobe/Salesforce/SAP/ServiceNow/Siemens/CrowdStrike等17家企业签约 | 企业级AI Agent、AI推理优化、智能客服、工业自动化 | LangChain、Dify、agency-agents | 2026-04-04 |
## 🏗️ 多智能体框架

| 框架 | 公司/来源 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|------|----------|----------|----------|----------|----------|
| DeerFLow 2.0 | 字节跳动 | 字节跳动开源多智能体框架2.0版本，支持多Agent协同推理与任务分解 | 多智能体开发、企业AI工作流、复杂任务编排 | agency-agents、LangChain | 2026-03-26 |
| agency-agents | — | 开源多智能体协作框架，7天狂飙2.3万GitHub星，用"拼装协作"替代大参数，单个智能体协同完成复杂任务 | AI Agent开发、多智能体协作、轻量化部署 | LangChain、CrewAI | 2026-03-25 |
| Dify | — | 开源LLMOps平台，3000万美元融资（红杉领投） | AI应用开发、工作流编排 | - | 2026-03-11 |
| LangChain | — | LLM应用开发 | RAG、Agent | LlamaIndex | - |
| LlamaIndex | — | 知识检索 | RAG、数据索引 | LangChain | - |
| CrewAI | — | 多Agent编排 | 复杂工作流 | AutoGen | - |
| AutoGen | 微软 | 多Agent框架 | 企业级应用 | CrewAI | - |
| MACRO-LLM | 港科大/上交 | 多智能体协作推理框架，解决"时空局部可观测性"问题，CoProposer+Negotiator+Introspector三模块 | 多智能体协调、多目标Pareto优化、推荐系统目标协调 | - | 2026-03-23 |
| **AgenticPay**（Berkeley/SafeRL-Lab）🆕 | 多智能体LLM谈判系统：110+任务模拟买家-卖家多轮自然语言谈判，评估可行性/效率/福利三个维度；为AI智能体在经济活动中的应用奠定基准 | 多智能体博弈、谈判系统、推荐激励策略 | AgenticRec | 2026-04-08 |

---

| Google TurboQuant | ICLR 2026发布，KV缓存内存压缩至少6倍，H100 GPU实现8倍速度提升，震动存储芯片板块 | AI推理优化、KV缓存压缩、GPU加速 | 传统KV缓存方案 | 2026-04-02 |

---

## ☁️ AI 推理部署 / 基础设施

| 框架 | 公司 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|------|------|----------|----------|----------|----------|
| NVIDIA Dynamo 1.0 | 英伟达 | 生产级AI工厂推理操作系统，已与LangChain等生态深度集成，面向AI推理优化 | AI推理部署、生产级LLM serving、企业AI基础设施 | vLLM、TGI | 2026-03-26 |
| EvoX | UC Berkeley RISE Lab | 自适应元进化算法，"双层进化"：同时进化候选解与生成策略本身，在200+真实优化任务上超越AlphaEvolve | AutoML、推荐系统超参自动优化、搜索策略自适应 | AlphaEvolve、OpenEvolve | 2026-03-23 |

---

## 🔌 AI 安全 / 评估工具

| 框架 | 核心能力 | 适用场景 | 更新时间 |
|------|----------|----------|----------|
| **Shannon**（KeygraphHQ）| 全自主AI渗透测试工具，XBOW基准96.15%，100/104漏洞利用；GitHub两天31,788 Stars爆发级增长；TypeScript，支持AI安全评估 | AI渗透测试、Agent安全评估、红队测试 | 2026-04-05 |
| **AReaL**（inclusionAI）| 闪电般RL强化学习框架，专为LLM推理和Agent设计，PyTorch生态 | Agent强化学习、LLM推理优化、多智能体训练 | 2026-04-05 |

---

## 🔌 Agent 开发工具

| 框架 | 核心能力 | 适用场景 | 更新时间 |
|------|----------|----------|----------|
| **ReMe**（agentscope-ai）| Agent记忆管理工具包，"记住我，精炼我"；GitHub持续增长，Agent持久化必备组件；支持记忆检索+精炼+持久化全链路 | Agent记忆管理、推荐Agent、长期规划Agent | 2026-04-05 |
| FusionRoute（北大/蚂蚁）| Token级多LLM协作框架，每个token由路由器动态选择最合适专家，互补logits修正 | 多模型协作推理、推荐系统多专家路由 | 2026-03-22 |
| **MiniMax MMX-CLI**（MiniMax）🆕 | 一行代码原生接入全模态模型，支持Claude Code等主流开发环境，MiniMax全模态能力快速接入工具 | 全模态AI接入、CLI开发工具、AI编程辅助 | — | 2026-04-09 |
| CLI-Anything（港大）| 开源，一行命令让任意软件秒变AI Agent"原生工具" | AI Agent开发、工具集成 | 2026-03-18 |
| 百度秒哒 | 零门槛全球应用开发，三步快速接入应用生成Skill | 低代码开发、应用生成 | 2026-03-18 |
| NemoClaw | 英伟达企业级智能体平台，基于OpenClaw构建，为企业提供"盔甲" | 企业级AI Agent、智能体部署 | 2026-03-18 |
| CocoLoop（OpenClaw Skills）| 国内最大OpenClaw Skills商店，5074+ Skills，支持20+主流Agent平台兼容，开发者SDK+场景化模板市场 | AI Agent技能市场、垂直行业模板、个人开发者套利 | - | 2026-03-26 |

---

## 📌 AI开发框架选型速查

| 需求 | 推荐框架 |
|------|----------|
| 多Agent协作/任务分解 | DeerFLow 2.0（字节）/ agency-agents |
| AI应用快速开发 | Dify（开源，红杉投资）|
| 生产级LLM推理 | NVIDIA Dynamo 1.0 |
| AutoML/推荐超参 | EvoX（UC Berkeley）|
| OpenClaw生态扩展 | CocoLoop Skills / NemoClaw |
| 快速接入任意工具 | CLI-Anything（港大）|

---

## ⚙️ 推理优化 / RAG 算法

| 框架/算法 | 公司/来源 | 核心能力 | 适用场景 | 替代方案 | 更新时间 |
|------|----------|----------|----------|----------|----------|
| **FIPO**（阿里通义实验室）🆕 | 引入Future-KL机制，优化大模型推理过程中关键Token识别与定位，显著提升推理效率和质量 | LLM推理优化、Token级优化、推荐Agent推理加速 | CoT、ToT | 2026-04-07 |
| **CompactRAG**（arXiv 2602.05728）🆕 | 高效多跳RAG：离线预计算将语料库转化为原子QA对，在线推理无论跳数多少仅调用2次LLM（分解+综合），token消耗大幅降低且保持竞争性准确率 | 高效RAG、多跳问答、商品知识库问答 | 标准多跳RAG | 2026-04-08 |

> 📅 更新日志见 CHANGELOG.md — AI开发框架相关条目
