# 📊 开源语音克隆 Benchmark 性能对比报告

> 🤖 免费语音克隆方案Agent | 2026-04-01 更新（新增 LongCat-AudioDiT SIM 0.818 全场最高）
> 收集来源：各模型官方 GitHub / 技术报告 / HuggingFace / 第三方评测

---

## 一、核心指标说明

| 指标 | 含义 | 越低越好 | 备注 |
|------|------|---------|------|
| **MOS** | 平均主观意见分（1-5分） | ❌ | 越高越好，4.5+ 接近真人 |
| **SIM** | 说话人相似度（Speaker Similarity） | ✅ | 越低越好（部分用 Cos 距离），也有用百分比/5分制 |
| **WER** | 词错误率（Word Error Rate） | ✅ | < 5% 为优秀 |
| **CER** | 字符错误率（Character Error Rate） | ✅ | 中文 TTS 主要指标，< 1% 为优秀 |
| **RTF** | 实时因子（Real-Time Factor） | ✅ | RTF=0.1 表示 1 秒音频只需 0.1 秒推理（即 10x 实时）|
| **TTFA** | 首音频延迟（Time-To-First-Audio） | ✅ | 用户触发到听到第一个音节的时间，越低越好 |
| **延迟** | 端到端延迟（ms） | ✅ | 毫秒级，越低越适合实时交互 |

---

## 二、质量Benchmark汇总

### 2.1 MOS（平均主观意见分，越高越好）

| 模型 | MOS | 评测集 | 备注 |
|------|-----|--------|------|
| **OpenAudio S1** | ~4.8-5.0 | 内部评测 | 行业领先 |
| **CosyVoice 3.0** | 5.53（提升自4.4） | CV3-Eval | 阿里官方 |
| **CosyVoice2** | 4.7-4.8 | CV2-Eval | 阿里官方 |
| **Kokoro-82M** | 4.2 | 内部评测 | 82M参数中最高 |
| **Fish Audio S2 Pro** | ~4.5+ | TTS Arena ELO 1339 | 80+语言支持 |
| **TADA** | 说话人相似度4.18/5.0 | EARS评测 | 英文相似度 |
| **XTTS-v2** | 4.0 | 内部评测 | 多语言克隆SOTA |
| **Dia2** | 4.0 | 内部评测 | 英文对话TTS |
| **Bark** | 3.7 | 内部评测 | 含非语言音频 |

> **参考基准**：真人录音 MOS ≈ 4.5；优秀商业TTS（ElevenLabs v3）≈ 4.6-4.8

### 2.2 说话人相似度 SIM（越低越好/越高越好，视指标而定）

| 模型 | SIM分数 | 度量方式 | 说明 |
|------|---------|---------|------|
| **OpenAudio S1** | 0.332（cosine distance） | Speaker Sim | 全场领先之一 |
| **GLM-TTS** | 76.4% | SIM（%） | GRPO优化后 |
| **TADA** | 4.18/5.0 | EARS评测（5分制） | 全场第二（EARS） |
| **Higgs Audio V2.5** | V2相比提升23% | 相对提升 | GRPO对齐优化 |
| **Fish Audio S2** | 高 | TTS Arena ELO | ELO 1339分 |
| **CosyVoice2** | 高 | CV2-Eval | 阿里官方评测 |
| **LongCat-AudioDiT** | **0.818（Seed SIM）** | Seed 基准测试 | **全场最高，超越字节 Seed-TTS** |
| **XTTS-v2** | 高 | 17语言跨语言克隆 | Coqui官方 |
| **Dia2** | 中等 | 非克隆对话 | 强调情感/对话 |

### 2.3 准确性WER/CER（越低越好）

| 模型 | WER | CER | 评测集 | 备注 |
|------|-----|-----|--------|------|
| **OpenAudio S1** | **0.8%** | **0.4%** | 内部 | 参数量4B，WER全场最低之一 |
| **MegaTTS3** | — | **0.9%** | 中文评测 | CER极低 |
| **GLM-TTS** | — | **0.89%** | 中文 | 全场开源中文TTS第二低 |
| **Higgs Audio V2** | 降低15% | — | 相对提升 | V2.5 GRPO对齐后进一步降低 |
| **Fish Audio V1.5** | 3.5% | 1.2%（EN）/ 1.3%（ZH） | TTS Arena | WER 3.5%为英文 |
| **CosyVoice 3.0** | 大幅降低30-50% | — | CV3-Eval | 相比v1.0，发音错误降低 |
| **GPT-SoVITS v4** | SIM **0.702** | — | 内部 | SIM 0.702（越高越好）|
| **Step-Audio TTS-3B** | **1.17%**（Libri） | — | Aishell-1 / LibriSpeech | 轻量版CER优秀 |

---

## 三、速度Benchmark汇总

### 3.1 实时因子RTF（越低越好，越低越快）

| 模型 | RTF | 硬件环境 | 备注 |
|------|-----|---------|------|
| **Orpheus TTS 25ms** | ~实时（极快） | GPU | 25ms TTFA |
| **LuxTTS** | **150x实时** | GPU | 推理极速 |
| **TADA** | **0.09** | GPU | 5倍速（全场最快之一）|
| **RVC** | 极低（实时） | GPU | 90ms端到端 |
| **VoxCPM 1.5** | **0.15**（RTX 4090） | RTX 4090 | 6.67x实时，Apache 2.0 |
| **Voxtral TTS** | **6x实时** | GPU | 90ms TTFA |
| **Fish Audio S2 Pro** | **0.195** | H200 | 约5x实时 |
| **ChatTTS v2** | 极低（实时） | GPU | 对话场景王者 |
| **OpenVoice** | 实时 | GPU | 即时克隆 |
| **Kokoro-82M** | 实时 | **CPU可运行** | 极轻量82M |
| **Pocket TTS** | 6x实时 | **纯CPU** | 无需GPU |
| **CosyVoice 3.0** | 流式150ms | GPU | 150ms首包 |
| **MegaTTS3** | <1s(GPU) | GPU | CPU约30s |
| **Qwen3-TTS** | ~实时 | GPU | 97ms延迟（MOSS）/ 其他 |

### 3.2 首音频延迟TTFA / 首包延迟

| 模型 | TTFA/首包 | 备注 |
|------|----------|------|
| **Orpheus TTS** | **25ms** | 全场最低之一 |
| **Voxtral TTS** | **90ms** | Mistral AI官方 |
| **MOSS-TTS** | **97ms** | 全场最低之一 |
| **ChatTTS v2** | 极低 | 对话实时 |
| **CosyVoice 3.0** | **150ms** | 流式 |
| **Pocket TTS** | **~200ms** | 纯CPU |
| **Chatterbox-TTS** | **~200ms** | 近实时 |
| **NeuTTS Air** | **低（端侧）** | 2GB RAM实时 |
| **Xiaomi MiMo-V2-TTS** | **<200ms** | Pro版本参考 |

---

## 四、按场景最强推荐（基于Benchmark）

| 场景 | 推荐模型 | 关键指标 |
|------|---------|---------|
| **中文克隆质量** | GLM-TTS / MegaTTS3 | CER 0.89% / 0.9% |
| **英文克隆质量** | OpenAudio S1 | WER 0.8%, CER 0.4% |
| **整体表现力** | Fish Audio S2 Pro | TTS Arena ELO 1339 |
| **中文对话自然度** | CosyVoice 3.0 | MOS 5.53 |
| **超低延迟（英文）** | Orpheus TTS | 25ms TTFA |
| **超低延迟（中文）** | MOSS-TTS | 97ms |
| **极速推理（CPU）** | Kokoro-82M / Pocket TTS | 实时 / 6x实时 |
| **极速推理（GPU）** | LuxTTS / VoxCPM 1.5 | 150x实时 / RTF 0.15 |
| **最短克隆样本** | F5-TTS / LuxTTS | 2秒 / 3秒 |
| **最低显存需求** | Kokoro-82M | 0.5GB |
| **有声书/长文本** | TADA | 700秒上下文 |
| **零幻觉可靠性** | TADA | 文本-声学双对齐 |
| **多语言商用** | CosyVoice 3.0 | 18+方言，Apache 2.0 |

---

## 五、Benchmark数据来源索引

| 模型 | 主要数据来源 |
|------|------------|
| CosyVoice 3.0 | GitHub/FunAudioLLM 官方 CV3-Eval |
| GLM-TTS | GitHub/THUDM/GLM-4 官方技术报告 |
| MegaTTS3 | 字节跳动论文 / 官方 GitHub |
| OpenAudio S1 | GitHub/fishaudio/fish-speech 官方 |
| TADA | Hume AI 官方 / EARS 评测集 |
| Voxtral TTS | Mistral AI 官方技术博客 |
| Fish Audio S2 Pro | TTS Arena ELO 排行榜 |
| Higgs Audio V2 | Boson AI 官方 / 幂简集成评测 |
| VoxCPM 1.5 | GitHub/OpenBMB/VoxCPM 官方 |
| GPT-SoVITS | GitHub/RVC-Boss/GPT-SoVITS 官方 |
| Step-Audio | 阶跃星辰官方 / HSK-6 评测 |
| Orpheus TTS | GitHub/canopyai/Orpheus-TTS 官方 |
| Xiaomi MiMo-V2-TTS | 小米 GitHub 官方 |
| MOSS-TTS | OpenMOSS 官方 |
| RVC | GitHub/RVC-Project 官方 |

---

## 六、常见误区说明

### ⚠️ MOS分数不能跨评测集比较
- **GLM-TTS CER 0.89%** vs **OpenAudio S1 CER 0.4%** → OpenAudio S1 更好（均为CER）
- **TADA SIM 4.18/5.0** 是5分制相似度，**GLM-TTS SIM 76.4%** 是百分制相似度 → 不可直接换算

### ⚠️ RTF与TTFA是两回事
- **RTF** = 推理总时间 / 音频总时长（RTF=0.1 = 10x实时）
- **TTFA** = 用户触发到听到第一音节（决定对话响应感）
- Orpheus 25ms TTFA 但 RTF 未必最低，适合对话但不一定适合批处理

### ⚠️ 显存需求不等于速度
- Kokoro-82M 只需0.5GB显存，但速度也略慢（CPU瓶颈）
- LuxTTS 只需1GB显存，推理速度却是150x实时（GPU加速，显存需求低）

---

*本报告持续更新，欢迎提交补充数据。*

---

## 七、2026年2-3月新增模型（2026-04-05更新）

### Higgs Audio V2.5 ⭐（强烈关注）
> 李沐/Boson AI 团队 | 2026-01-18 | Apache-2.0

| 指标 | 数值 |
|------|------|
| 参数量 | **1B**（从V2的3B大幅精简）|
| 训练数据 | 1000万小时音频 |
| 采样率 | 24kHz 高保真 |
| 克隆速度 | 3秒音频零样本克隆 |
| 情感表达 | 超越GPT-4o-mini-tts，胜率>75% |
| 对齐策略 | GRPO + Voice Bank |
| 开源协议 | Apache-2.0 |

**优势**：
- 1B 参数即可超越原3B版本，质量与效率兼得
- 情感表达为所有方案最强（多人对话场景突出）
- 支持多语言对话、韵律调整、歌声合成
- 生产环境优化，适合正式部署

**劣势**：
- 相比 Qwen3-TTS（97ms）延迟较高（具体延迟数据待补充）
- 国内访问 HuggingFace 可能受限

---

### KaniTTS2
> 2026-02-11 | 开源

| 指标 | 数值 |
|------|------|
| 参数量 | 400M |
| 显存需求 | **3GB**（超低）|
| 克隆方式 | 零样本语音克隆 |
| 特点 | 边缘设备友好，预训练代码可自定义 |

**优势**：超低显存，老旧GPU甚至CPU可运行
**劣势**：功能相对基础，情感控制不如大模型

---

### Kyutai Pocket TTS
> Kyutai Research Lab | 2026-01 | 开源

| 指标 | 数值 |
|------|------|
| 参数量 | **100M**（超轻量）|
| 运行设备 | **CPU 实时推理** |
| 适用场景 | 边缘/移动设备 |

**优势**：单命令安装，CPU即可实时运行
**劣势**：质量不如大模型方案，适合简单场景

---

### CosyVoice 3 最新性能数据（2026-02 更新）

| 指标 | CosyVoice 3（0.5B）| Qwen3-TTS 1.7B |
|------|---------|---------|
| 中文CER | **0.71**（全场最低）| 0.77 |
| 英文WER | 1.45 | **1.24**（全场最低）|
| 延迟 | 150ms | **97ms** |
| 语言数 | 9种+18种方言 | 10种语言 |
| 方言支持 | ✅（粤语/闽南语/四川话等）| ❌ |
| 克隆数据 | 3秒 | 3秒 |

**结论**：中文场景 CosyVoice 3 更优（低CER+方言支持）；英文+低延迟 Qwen3-TTS 更优

---

*本报告更新于 2026-04-05*
