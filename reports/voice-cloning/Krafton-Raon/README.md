# Krafton Raon 语音模型系列

> 🤖 免费语音克隆方案Agent | 2026-04-07 收录
> 来源：Krafton（PUBG制作商）| 发布日期：2026年4月2日
> 许可证：待确认（开源于 HuggingFace，详见下方）

---

## 一、概述

2026年4月2日，韩国游戏公司 **Krafton**（PUBG 制作商）正式发布 AI 模型品牌 **Raon**，并在 HuggingFace 开源四款模型，其中三款为语音/音频模型：

| 模型 | 类型 | 参数 | 核心亮点 |
|------|------|------|----------|
| **Raon-Speech** | Speech-Enabled LLM | **9B** | 全球<10B开源Speech LLM排名第一，ASR+TTS+语音问答三合一 |
| **Raon-SpeechChat** | 全双工实时对话模型 | 未公开 | 韩国首个全双工语音对话，可双向打断 |
| **Raon-OpenTTS** | TTS 模型 | 未公开 | 纯公开数据训练，盲评超越专有数据模型 |
| Raon-Vision Encoder | 视觉编码器 | 未公开 | 超越 Google SigLIP2（视觉任务）|

**品牌含义**：Raon 来自韩语固有词，意为"喜悦"，英文拼写取自 KRAFTON。

---

## 二、Raon-Speech（核心模型）

### 2.1 基本信息

- **类型**：Speech-Enabled Large Language Model（语音增强大语言模型）
- **参数规模**：9B（90亿参数）
- **核心能力**：
  - 自动语音识别（ASR）
  - 文本转语音（TTS）
  - 基于语音的问答（Speech-based QA）
- **支持语言**：英语、韩语
- **训练数据**：全量训练数据**已公开发布**（完整可复现）
- **评估**：在 7 项核心任务、40 项基准测试中排名全球第一（<10B 开源 Speech LLM 类别）

### 2.2 性能亮点

- 在英语和韩语两项任务上，**全球<10B参数开源Speech LLM排名第一**
- 覆盖 ASR、TTS、语音问答三大核心场景
- 评测基准：7项核心任务 × 40个独立基准
- 完整训练流程和数据集开源，研究可复现性极强

### 2.3 与其他 Speech LLM 对比

| 模型 | 参数量 | ASR | TTS | 语音问答 | 开源训练数据 |
|------|--------|-----|-----|----------|------------|
| Raon-Speech | 9B | ✅ | ✅ | ✅ | ✅ 全量开源 |
| CosyVoice 3.0 | 0.5B | ✅ | ✅ | ❌ | ✅ 部分开源 |
| Covo-Audio | 7B | ✅ | ✅ | ✅ | ❌ |
| FunAudioLLM/Seed | ~1B | ✅ | ✅ | ❌ | ❌ |

---

## 三、Raon-SpeechChat（实时对话）

### 3.1 基本信息

- **类型**：Real-time Full-Duplex Voice Conversation Model
- **核心特性**：**双向打断** — 用户和模型可以在对话中自由打断对方
- **支持语言**：英语、韩语
- **意义**：**韩国首个**实时全双工语音对话模型

### 3.2 评测覆盖（13项全双工任务）

- **Backchanneling（回应反馈）**
- **Interruption handling（打断处理）**
- **Response latency（响应延迟）**
- 其他核心对话任务（共13项）

### 3.3 应用场景

- 实时语音助手
- 游戏内语音NPC
- 客服对话系统
- 远程教育实时问答

---

## 四、Raon-OpenTTS（TTS模型）

### 4.1 基本信息

- **类型**：Text-to-Speech（TTS）模型
- **训练数据**：**100% 公开可用语音数据**（无专有数据依赖）
- **亮点**：完整训练数据已公开发布，**任何人均可复现训练过程**
- **评测**：在盲测中（人聆听自然度对比），表现超越使用专有数据训练的全球研究级TTS模型

### 4.2 关键意义

这是目前**极少数**采用纯公开数据集训练的高性能TTS模型：
- 避免了商业TTS模型依赖专有数据的合规风险
- 研究者可完全复现训练流程
- 数据集对外开放，促进学术界发展

### 4.3 对比主流TTS

| 模型 | 训练数据 | 许可证 | 可复现性 | 声音克隆 |
|------|---------|--------|---------|---------|
| Raon-OpenTTS | 100%公开 | 开源（待确认）| ✅ 完整开源 | ✅ |
| CosyVoice 3.0 | 专有+公开混合 | Apache 2.0 | 部分开源 | ✅ |
| Qwen3-TTS | 专有为主 | Apache 2.0 | ❌ | ✅ |
| GLM-TTS | 专有为主 | Apache 2.0 | ❌ | ✅ |
| VoxCPM 1.5 | 公开为主 | Apache 2.0 | ✅ | ✅ |

---

## 五、部署与使用

### 5.1 获取方式

> ⚠️ HuggingFace 组织名称尚未确认，以下为推测路径。
> 建议前往 [HuggingFace](https://huggingface.co/models?search=raon) 搜索 `raon` 或 `krafton` 获取确切模型名称。

```bash
# 搜索模型（待确认实际组织名）
# 可能的路径：
# huggingface.co/raon-audio/Raon-OpenTTS
# huggingface.co/krafton-raon/Raon-Speech

# 推荐直接访问 HuggingFace 搜索
# https://huggingface.co/models?search=raon
```

### 5.2 硬件要求（预估）

| 模型 | GPU显存 | CPU | 存储 | 备注 |
|------|--------|-----|------|------|
| Raon-Speech（9B） | ~18-24GB（FP16） | 16核+ | 20GB+ | 需要高性能GPU |
| Raon-SpeechChat | ~10-16GB（预估） | 8核+ | 10GB+ | 全双工延迟敏感 |
| Raon-OpenTTS | ~6-8GB（预估） | 4核+ | 8GB+ | 相对轻量 |

### 5.3 GitHub 组织

```
# 可能的 GitHub 地址（待确认）
github.com/krafton-raon
```

---

## 六、重要说明

### 6.1 许可证

> ⚠️ 截至2026-04-07，Krafton 尚未在公开渠道说明具体开源许可证。
> 建议在 HuggingFace 模型页面确认许可证类型后再进行商业使用。

**已确认**：
- 模型开源发布于 HuggingFace
- 全量训练数据公开发布

**待确认**：
- 具体许可证类型（Apache 2.0 / MIT / CC-BY-NC 等）
- 商业授权条款

### 6.2 与其他主流方案对比

| 维度 | Raon-Speech | Qwen3-TTS | CosyVoice 3.0 | ChatTTS |
|------|------------|-----------|---------------|---------|
| 中文支持 | ❌ | ✅ | ✅ | ✅ |
| 克隆能力 | ✅（Speech模式） | ✅ | ✅ | N/A |
| 实时对话 | ✅（SpeechChat） | ❌ | ❌ | ❌ |
| 完全公开数据 | ✅ | ❌ | ❌ | ❌ |
| 多语言 | 英/韩 | 10语言 | 18+语言 | 中/英 |
| 许可证明确性 | ⚠️ 待确认 | ✅ Apache 2.0 | ✅ Apache 2.0 | ✅ |

---

## 七、总结与建议

### 7.1 适用场景

✅ **推荐使用 Krafton Raon 系列**：
- **研究目的**：全量训练数据开源，可完全复现（Raon-Speech / Raon-OpenTTS）
- **英韩双语项目**：Speech LLM 在英韩双语上全球第一
- **实时语音交互**：Raon-SpeechChat 全双工打断能力

⚠️ **暂不推荐**：
- **中文项目**：暂不支持中文
- **商业用途**：许可证尚未明确

### 7.2 下一步建议

1. 确认 HuggingFace 实际模型页面和许可证类型
2. 等待中文支持（如有规划）
3. 关注 GitHub 更新：`github.com/krafton-raon`

---

## 八、参考链接

- HuggingFace（搜索 `raon`）：https://huggingface.co/models
- 新闻来源：https://en.sedaily.com/news/2026/04/02/krafton-launches-ai-model-brand-raon-releases-four-open
- Microsoft MAI Voice 新闻：https://letsdatascience.com/news/microsoft-releases-mai-models-google-ships-gemma-4-769047fd

---

*本报告由免费语音克隆方案Agent自动生成 | 2026-04-07*
