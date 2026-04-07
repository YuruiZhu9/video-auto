# Agent信息源补充方案（2026-03-03）

## 来源说明
用户通过 docx 文件提供了三个Agent的详细升级方案，来源包括豆包、Deepseek、Qwen的建议整合。

---

## 一、信息抓取助手（AI新闻与大模型公司动态）

### 核心必补信息源（高优先级）
| 信息源 | 核心价值 |
|--------|----------|
| The Verge（AI板块） | 全球顶级科技媒体，OpenAI/Anthropic/Meta/Google动态 |
| Bloomberg Technology | 财经科技媒体，聚焦融资/战略/财报/商业化 |
| 量子位 | 国内AI垂直媒体第一梯队，覆盖字节/阿里/腾讯/DeepSeek/MiniMax/月之暗面 |
| 机器之心 | 国内顶级AI产业媒体，兼顾技术深度与产业落地 |
| 目标大厂官方博客/X账号 | 一手信息，无二手滞后 |
| AI Business | 企业级AI垂直媒体 |

### AI Agent 专项追踪（扩围重点）
| 信息源 | 核心价值 |
|--------|----------|
| Awesome AI Agents Live | 全球AI Agent产品/工具/框架日更追踪 |
| AI Agents 中文社区 | 国内AI Agent落地案例与产品动态 |
| Agentic（播客/Newsletter） | AI Agent前沿技术与商业化 |
| Clawhub（OpenClaw技能市场） | 第三方Agent Skills生态动态 |
| LangChain Blog / Agents文档 | Agent开发框架最新能力 |
| CrewAI Blog | 多Agent协作框架动态 |
| AutoGen（Microsoft）GitHub | 企业级多Agent框架更新 |
| Relevance AI | 低代码Agent平台产品迭代 |

### 垂直补充信息源
- Reuters Technology（AI板块）：全球监管政策
- VentureBeat：AI创业公司/创新项目
- 品玩PingWest：海内外AI联动
- 36氪：国内AI公司融资/战略

---

## 二、技术前沿分析师（论文+技术+招聘+AI Agent）

### AI Agent 技术专项
| 信息源 | 核心价值 |
|--------|----------|
| arXiv cs.AI（Agent/Agentic AI） | AI Agent学术论文权威源 |
| Papers With Code（Agent相关） | Agent论文+开源代码落地 |
| OpenAI Agents SDK 文档 | OpenAI官方Agent开发框架 |
| Anthropic Computer Use / MCP | Claude Agent工具调用与MCP生态 |
| Google Agent Development Kit | Google Gemini Agent开发工具 |
| LlamaIndex / LangGraph | Agent记忆与工作流编排 |
| GitHub Trending（AI/Agents） | 热门Agent开源项目追踪 |

### 学术论文专属源
| 信息源 | 核心价值 |
|--------|----------|
| arXiv cs.AI/cs.IR/cs.LG | 精准锁定大模型+推荐系统 |
| RecSys/SIGIR/WSDM顶会 | 推荐系统核心权威源 |
| NeurIPS/ICML/ICLR/ACL | 大模型顶级顶会 |
| Papers With Code | 论文+开源代码，落地能力强 |

### 工业界实践源
- Netflix AI（推荐系统鼻祖）
- 字节/阿里妈妈/腾讯推荐算法团队
- Google DeepMind/Meta AI官方博客
- GitHub Trending（AI/ML板块）

### 招聘渠道
| 信息源 | 核心价值 |
|--------|----------|
| 拉勾网 | 国内互联网垂直招聘 |
| 猎聘 | 年薪30W+中高端岗位 |
| 脉脉 | 真实岗位需求/内推 |
| LinkedIn领英 | 海内外全球AI岗位 |

---

## 三、商业需求洞察分析师（商机+政策+跨行业）

### 独立开发者&创业变现源
| 信息源 | 核心价值 |
|--------|----------|
| V2EX 创业/分享板块 | 国内个体开发者AI产品案例 |
| Product Hunt | 全球AI新产品风向标 |
| 掘金 独立开发者专区 | 国内AI工具/SaaS案例 |
| Hacker News（Show HN） | 海外早期AI项目 |

### 政策&行业趋势权威源
- 中国政府网 政策专栏
- 工信部 人工智能板块
- 易观分析/头豹研究院
- QuestMobile/极光大数据

### 全行业需求&消费趋势源
- 新榜/蝉妈妈：内容&消费趋势
- 小红书 热门搜索：C端真实痛点
- 淘宝/京东 热门榜单：消费端商机
- 垂直行业媒体矩阵

---

## 四、推荐Newsletter（来自Deepseek建议）

### 信息抓取助手
- **AI News by Smol**：Andrej Karpathy推荐
- **The Neuron Daily**：50万订阅者
- **Alpha Signal**：5分钟每日邮件
- **Import AI**：Anthropic联创撰写

### 技术前沿分析师
- **Latent Space**：AI工程师技术通讯
- **The Sequence**：论文深度解读
- **Coding with Intelligence**：无BS的技术通讯

---

## 五、优先级建议

### 高优先级（立即接入）
- AlphaXiv（论文增强）
- Product Hunt（商机发现）
- 澎湃新闻AI排行榜
- BOSS直聘（招聘JD）
- 量子位、机器之心
- Awesome AI Agents Live（AI Agent追踪）
- OpenAI Agents SDK / Anthropic MCP（MCP协议生态）

### 中优先级（1周内）
- AI Agents 中文社区
- 智联招聘
- a16z Blog（AI Agent投资动态）
- InfoQ AICon
- LangChain Agents Blog
- Clawhub 新增Skills追踪

---

## 六、技术实现建议

### 统一数据格式
```json
{
  "source": "信息源名称",
  "type": "news/paper/job/opportunity",
  "date": "2026-02-27",
  "title": "标题",
  "summary": "摘要",
  "url": "原文链接",
  "companies": ["相关公司"],
  "tags": ["标签"]
}
```

### 定时任务配置
| 任务 | 频率 |
|------|------|
| AI新闻抓取 | 每日3次 |
| 论文更新 | 每日2次 |
| 招聘JD | 每日1次 |
| 商机分析 | 每日1次 |
| 政策报告 | 每周1次 |
