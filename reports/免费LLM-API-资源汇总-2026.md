---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d966eb9eeb9f6a6d1c77b32b54c25b31
    PropagateID: d966eb9eeb9f6a6d1c77b32b54c25b31
    ReservedCode1: 30450220600e9bc90bec5a592f7e1c7498b3d56fd4209961a4ef80c5ae00b676539758de022100a50d18bbc148e271ac9205cf421c8d6e0bb46d937b1de595615a5174e70432a1
    ReservedCode2: 30450220516aadd669c858eedbb976ec0f3ee83f39c2db16446d0de932197ed8477d245c022100ca03bcb05600a29796678b1a50e5f54ccb0026fba80768823b10a2a9893486cb
---

# 免费 LLM API 资源汇总（2026年4月）

> 信息源：百度百家号 + GitHub cheahjs/free-llm-api-resources  
> 更新时间：2026-04-01

---

## 一、先说重点：真正长期免费的 API（非新用户赠送）

这类 API 存在永久免费额度，不依赖"注册送 X 美元"的活动，适合作为稳定调用的后盾。

### 🏆 Tier 1：额度最实在，可日常使用

| API | 免费额度 | 速率限制 | 代表模型 | 说明 |
|-----|---------|---------|---------|------|
| **Groq** | 永久免费 | Llama 3.1 8B: **14400次/天**，6000 tokens/min；Llama 3.3 70B: 1000次/天 | Llama 3.1 8B/70B、Gemma 2 9B、DeepSeek R1 Distill | ⭐ 推荐。注册即用，额度最宽松，速度极快（LPU芯片）|
| **Cloudflare Workers AI** | 永久免费 | **10000 神经元/天**（每日UTC 00:00重置） | Llama 3.1 8B、Mistral 7B、Gemma 2B/12B、DeepSeek R1、Qwen系列 | ⭐ 推荐。无需信用卡，无月费，模型覆盖面广 |
| **Google AI Studio** | 永久免费 | Gemini 3 Flash: 25万tokens/min；Gemma 3: 1.44万次/天 | Gemini 2.0/3.0 Flash、Gemini 1.5 Flash、Gemma 3 27B/12B | ⭐ 推荐。额度按月重置，量大稳定。**注意：欧洲/英国/EEA外使用数据用于训练** |
| **Cohere** | 永久免费 | 20次/min，**1000次/月** | Command A、Command R+、c4ai-aya-expanse-32B | 长期免费但月度限额较低，适合轻量调用 |
| **GitHub Models** | 永久免费 | 与 GitHub Copilot 订阅等级挂钩 | AI21 Jamba 1.5 Large、Cohere Command R 等 | 拥有 GitHub 账号即可用，限流较严 |
| **NVIDIA NIM** | 永久免费（原型开发） | **40次/min** | DeepSeek R1、Nemotron Nano、 Gemma 2 9B | 需加入 NVIDIA 开发者计划 + 手机号验证 |

### 🥈 Tier 2：可用但有条件的长期免费

| API | 免费额度 | 速率限制 | 代表模型 | 条件 |
|-----|---------|---------|---------|------|
| **Mistral La Plateforme** | 每月 10亿 tokens | 1次/sec，50万tokens/min | mistral-large-2402、mistral-7B、Codestral | ✅ 永久免费；❌ 需手机号验证 + 授权数据训练 |
| **Mistral Codestral** | 永久免费 | 30次/min，2000次/天 | Codestral（代码模型）| ✅ 永久免费；❌ 需手机号验证 |
| **Cerebras** | 永久免费 | 30次/min，6万tokens/min，**1万tokens/天** | Llama 3.1 8B、gpt-oss-120B | ✅ 永久免费；需申请候补（通常自动通过）|
| **HuggingFace Inference** | 每月 $0.10 credit | 模型文件 < 10GB | GPT-3 开源适配版、DistilBERT 等 | 额度极少，适合小量测试 |
| **Vercel AI Gateway** | 每月 $5 credit | 按用量抵扣 | 聚合多模型 | ✅ 长期有效；缺点是 $5 在生产环境很快用完 |
| **OpenRouter** | 永久免费套餐 | 20次/min，**50次/天** | Qwen3.6 Plus (free variant)、部分 Gemma 3 | ⭐ 有免费变体模型（如 Qwen3.6 Plus Preview free）长期存在 |

### 🏅 特别收录：硅基流动（SiliconCloud，中国特供）

| API | 情况 | 说明 |
|-----|------|------|
| **硅基流动 SiliconCloud** | 有免费模型 | 汇聚国产大模型，部分模型有免费额度（如 DeepSeek 系列），但免费政策时有调整，需实地查看官网 |


---

## 二、新用户赠送额度（一次性，用完即止）

以下 API 的免费额度本质上是"注册红包"，用完后需付费，适合薅羊毛 / 短期项目：

| API | 赠送额度 | 有效期 | 代表模型 |
|-----|---------|--------|---------|
| **Fireworks AI** | $1 credit | 用完即止 | Llama 3.1 405B、DeepSeek R1 |
| **AI21 Labs** | $10 credit | 3个月 | Jamba Mini/Large |
| **SambaNova Cloud** | $5 credit | 3个月 | Llama 3.1/3.3/4、DeepSeek R1/V3、Qwen3 |
| **Upstage Solar** | $10 credit | 3个月 | Solar Pro/Mini |
| **Hyperbolic** | $1 credit | 用完即止 | DeepSeek V3、Llama 3.1/3.2/3.3、Qwen 系列 |
| **Novita** | $0.5 credit | 1年 | 多种模型 |
| **Nebius** | $1 credit | 用完即止 | 多种模型 |
| **Baseten** | $30 credit | 用完即止 | 任意模型（按计算时间计费）|
| **Modal** | $5~30/month | 持续（需添加支付方式）| 任意模型 |
| **Scaleway** | 100万 tokens | 用完即止 | Llama 3.1/3.3、Gemma 3、DeepSeek R1、Qwen 系列 |
| **阿里云百炼** | 百万 tokens | 新用户 | 通义全系列、DeepSeek 等 |
| **NLP Cloud** | $15 credit | 用完即止 | 多种模型 |
| **Inference.net** | $1（回复邮件调查表得 $25）| 用完即止 | 多种模型 |

---

## 三、按用途推荐（转行推荐系统算法）

### 推荐系统 / 大模型算法学习

| 场景 | 推荐 API | 理由 |
|------|---------|------|
| **日常练手 / demo** | **Groq**（免费额度最宽）| 14400次/天，Llama 3.1 8B 足够跑小规模推荐实验 |
| **RAG / embedding** | **Cloudflare**（免费神经元）| 支持 embedding 模型 BGE-M3 |
| **国产模型适配** | **硅基流动**（DeepSeek 系免费）| DeepSeek V3/R1 性价比极高 |
| **代码生成 / Agent** | **Mistral Codestral**（代码模型免费）| 代码能力出众，适合推荐系统特征工程脚本 |
| **思考链（Reasoning）** | **Google AI Studio**（Gemini 2.0 Flash）| 免费额度和速度都不错 |
| **大规模推理测试** | **OpenRouter**（Qwen3.6 Plus free variant）| 0成本跑新模型 |

---

## 四、你特别问的：智谱 GLM-4-Flash

智谱 GLM-4-Flash 确实有免费 API 调用额度，但**政策波动较大**：
- 2025 年底曾因算力紧张推出"Coding Plan"收费制
- 常规免费额度（注册赠送 + 活动）是主要获取方式
- **建议搭配硅基流动 SiliconCloud** 使用，部分硅基节点接入了 GLM 系列，免费额度稳定

---

## 五、快速选择指南

```
日均 < 5000 次调用   → Groq（主力）+ Cloudflare（辅助）
需要国产大模型       → 硅基流动 SiliconCloud
需要稳定思考链       → Google AI Studio Gemini 2.0/3.0 Flash
做代码类推荐实验     → Mistral Codestral（免费代码模型）
想试新模型（0成本）  → OpenRouter Qwen3.6 Plus free variant
额度快用完了薅羊毛   →  Fireworks AI / Hyperbolic / AI21 Labs
```

---

## 六、获取方式速查

| API | 官网 | 注册难度 | 是否需信用卡 |
|-----|------|---------|------------|
| Groq | console.groq.com | ⭐ 简单（邮箱即可）| 否 |
| Cloudflare | cloudflare.com/workers-ai | ⭐ 简单 | 否 |
| Google AI Studio | aistudio.google.com | ⭐ 简单（Google账号）| 否 |
| Cohere | cohere.com | ⭐ 简单 | 否 |
| GitHub Models | github.com/marketplace/models | ⭐ 简单（GitHub账号）| 否 |
| NVIDIA NIM | build.nvidia.com | ⭐⭐ 中等（需手机号）| 否 |
| Mistral | console.mistral.ai | ⭐⭐ 中等（需手机号）| 否 |
| Cerebras | cerebras.ai | ⭐⭐ 需申请候补 | 否 |
| OpenRouter | openrouter.ai | ⭐ 简单 | 否（$10可升级）|
| 硅基流动 | cloud.siliconflow.cn | ⭐ 简单 | 否 |
| Fireworks | fireworks.ai | ⭐⭐ 需充值$1 | 需充值$1 |

---

*本文档随资源变化持续更新，建议星标 GitHub 源仓库 [cheahjs/free-llm-api-resources](https://github.com/cheahjs/free-llm-api-resources) 获取最新动态。*
