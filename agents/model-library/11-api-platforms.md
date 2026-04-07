# ☁️ 大模型 API 平台

> 来源：跨Agent新技术同步中心 — 模型库
> 维护方式：参考 CHANGELOG.md 按日期追加

---

## 🏢 全球主流平台

| 平台 | 主力模型 | 特点 | 适用场景 | 更新时间 |
|------|----------|------|----------|----------|
| OpenAI API | GPT-5.4 / GPT-5.4 mini/nano | 模型全面，更新快 | 通用开发、企业级应用 | - |
| Anthropic API | Claude 4.6 / Claude 3.6 Sonnet | Claude Code加持，代码能力强 | 代码开发、长文本分析 | - |
| Google AI | Gemini 2.5 / Gemini Embedding2 | 长上下文、多模态嵌入领先 | 长文本处理、语义搜索 | - |
| **Nvidia Groq** ⭐ | Groq LPU（语言处理单元）| Nvidia ~200亿美元收购，整合LPU高速Token处理技术，弥补GPU在AI代码助手/智能体场景短板 | 高速Token推理、AI代码助手、Agent场景 | 2026-04-04 |
| **Nvidia Rubin** | Rubin GPU | 288GB HBM内存，推理速度50 PFlops（是Blackwell的2.5倍），GTC 2026发布 | 超大模型推理、AI工厂、分布式训练 | 2026-04-04 |

---

## 🇨🇳 国内平台

| 平台 | 主力模型 | 特点 | 适用场景 | 更新时间 |
|------|----------|------|----------|----------|
| TokenHub | 腾讯全系大模型 | 腾讯首发Agent产品全景图中的大模型服务平台，Agent生态基础支撑 | Agent开发、企业LLM部署 | 2026-03-28 |
| 阿里云DashScope | Qwen3.5-Max-Preview / Qwen3.5系列 | LM Arena全球第一，中文能力强 | 中文场景、企业部署 | - |
| **Microsoft MAI** | MAI-Transcribe-1（语音转文字，多语言错误率3.9%全球最优）/ MAI-Voice-1（语音克隆，单GPU 1秒生成60秒音频）/ MAI-Image-2（文生图，Copilot已上线） | 微软自研三件套，目标2027年实现完全自主前沿大模型，349亿美元资本支出 | 语音/图像/企业级AI | 2026-04-03 |
| 硅基流动 | Qwen3.5-4B / DeepSeek-R1-Distill等12个模型 | 低价API，国内直连 | 成本敏感场景 | - |
| 百度千帆 | ERNIE-Bot-4 / ERNIE-Bot-turbo | 注册有赠送额度 | 百度生态集成 | - |
| 讯飞星火 | 星火大模型 | 语音能力突出 | 语音/中文场景 | - |

---

## 🔬 垂直 / 专业平台

| 平台 | 主力模型 | 特点 | 适用场景 | 更新时间 |
|------|----------|------|----------|----------|
| Mistral Small 4 | Mistral Small 4 | 开源新模型，整合三大旗舰能力，加入英伟达Nemotron联盟 | 企业部署、开源方案 | 2026-03-18 |
| Together AI | Llama 3 / Mistral / Flux | 开源模型聚合，注册送1美元 | 开源模型调用 | - |
| Hugging Face Inference | 10万+开源模型 | 模型库最全，冷启动较慢 | 模型研究、实验 | - |

---

## ☁️ 免费 AI API（完整指南见 12-free-apis.md）

| 平台 | 免费模型 | 免费额度 | 备注 |
|------|----------|----------|------|
| 智谱AI | GLM-4.7-Flash / GLM-4-Flash | **永久免费**，200K上下文 | 中文友好首选 |
| 硅基流动CN | Qwen3.5-4B / DeepSeek-R7B等12个 | **永久免费**，无明确日上限 | 国内直连 |
| Hypereal AI | Flux 2 / SDXL / Sora 2等 | 35免费积分（≈数千张图/视频）| 统一API，图片+视频+3D+语音 |

---

## 📌 大模型API平台选型速查

| 需求 | 推荐平台 |
|------|----------|
| 全球最强通用 | OpenAI GPT-5.4 / Anthropic Claude 4.6 |
| 国产第一 | 阿里云DashScope（Qwen3.5-Max-Preview）|
| **Microsoft MAI** | MAI-Transcribe-1（语音转文字，多语言错误率3.9%全球最优）/ MAI-Voice-1（语音克隆，单GPU 1秒生成60秒音频）/ MAI-Image-2（文生图，Copilot已上线） | 微软自研三件套，目标2027年实现完全自主前沿大模型，349亿美元资本支出 | 语音/图像/企业级AI | 2026-04-03 |
| 免费中文API | 智谱AI GLM-4.7-Flash（永久免费）|
| 免费多模型 | 硅基流动（12个开源模型）|
| 免费图片+视频API | Hypereal AI（35积分统一入口）|
| 语义嵌入/多模态 | Google Gemini Embedding2 |
| 最低成本商用 | 硅基流动 |

---

> 📅 更新日志见 CHANGELOG.md — 大模型API平台相关条目
