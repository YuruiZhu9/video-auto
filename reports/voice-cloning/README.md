# 📚 免费语音克隆方案资料库

> 🤖 免费语音克隆方案Agent | 更新于 2026-04-01 21:30（新增 Irodori-TTS-500M-v2，资源库收录 42 个方案 + 10 份实用指南）

---

## 📋 目录索引

### 🗺️ 生态地图（新增 2026-04-01）
- **[生态地图/README.md](生态地图/README.md)** — 🎯 **2026-04-01 新增**：TTS 架构流派图谱（6大流派）、技术传承关系（F5-TTS宗主地位/国产TTS影响力）、应用场景×架构推荐矩阵、License全景决策表、显存需求全景图、2024-2026关键技术里程碑；帮助理解模型之间的关系，做出更聪明的选型决策

### 📊 综合对比
- **[模型对比.md](模型对比.md)** — 全部方案横向对比表 + 选型决策树
- **[Benchmark对比报告.md](Benchmark对比报告.md)** — 35+方案Benchmark汇总（MOS/WER/CER/SIM/RTF/TTFA六大指标）
- **[选型指南/README.md](选型指南/README.md)** — 按硬件/场景/语言快速选型
- **[硬件推荐指南.md](硬件推荐指南.md)** — 按预算推荐GPU配置 + 云端推理方案
- **[微调实战手册.md](微调实战手册.md)** — 模型微调完整教程
- **[懒人速查卡.md](懒人速查卡.md)** — 🎯 **2026-03-31 新增**：一分钟速查，按场景一句话推荐，命令速查，License速查
- **[选型决策树.md](选型决策树.md)** — 🎯 **2026-04-01 新增**：可视化决策树，按硬件/延迟/语言/场景快速定位最优方案，含常见坑避让指南


### 🎯 实用指南
- **[实战问答.md](实战问答.md)** — 🎯 **2026-04-01 新增**：20+真实场景高频问题全覆盖，涵盖入门选型/版权合规/技术实战/性能优化/特定场景（有声书/短视频/AI助手/方言）/常见坑避让

### 🔧 各方案详细指南
| 方案 | 文档 | 特点 | 推荐度 |
|------|------|------|--------|
| **LongCat-AudioDiT** 🆕 | [LongCat-AudioDiT/README.md](LongCat-AudioDiT/README.md) | 美团2026-03全新发布，**波形潜空间扩散架构**，3.5B参数，**SIM 0.818全场最高**，超越 Seed-TTS，中英双语，MIT 协议 | 🥇 **相似度最高首选** |
| **LEMAS-TTS** 🆕 | [LEMAS-TTS/README.md](LEMAS-TTS/README.md) | IDEA研究院2026-01发布，**15万小时多语言数据集**，10语言，Flow-Matching架构，**Speech Editing** 词级语音编辑，CC BY 4.0 | 🥇 **多语言出海首选** |
| **MegaTTS3** 🆕 | [MegaTTS3/README.md](MegaTTS3/README.md) | 字节跳动，0.45B极轻量，中英代码切换，Apache-2.0，⚠️即时克隆需绕路 | 🥈 强烈推荐（低资源/双语首选） |
| **MOSS-TTS** | [MOSS-TTS/README.md](MOSS-TTS/README.md) | OpenMOSS新秀，49+内置音色，97ms低延迟 | 🥇 首选 |
| **Qwen3-TTS** | [Qwen3-TTS/README.md](Qwen3-TTS/README.md) | 3秒克隆，支持自然语言描述音色 | 🥇 首选 |
| **Qwen3-TTS Skill** 🆕 | [Qwen3-TTS-Skill/README.md](Qwen3-TTS-Skill/README.md) | 本地部署套件，三种高级语音模式，批量配音+AI审稿 | 🥇 隐私优先首选（2026-03-31） |
| **CosyVoice2** | [CosyVoice2/README.md](CosyVoice2/README.md) | 阿里开源，多语言，流式推理 | 🥈 强烈推荐 |
| **F5-TTS** | [F5-TTS/README.md](F5-TTS/README.md) | 2秒克隆，推理速度最快 | 🥉 |
| **IndexTTS-2** | [IndexTTS/README.md](IndexTTS/README.md) | 情感与音色分离，8维情感向量 | ⭐⭐⭐ |
| **CosyVoice 3.0** 🆕 | [CosyVoice3/README.md](CosyVoice3/README.md) | 阿里旗舰，1M小时数据，18+方言，发音修补 | 🥇 首选 |
| **ChatTTS v2** | [ChatTTS/README.md](ChatTTS/README.md) | 无需克隆，对话场景王者 | ⭐⭐⭐⭐ |
| **GPT-SoVITS v2** | [GPT-SoVITS/README.md](GPT-SoVITS/README.md) | 深度微调，长期运营首选 | ⭐⭐⭐ |
| **Fish Audio S2 Pro** 🆕 | [Fish-Audio-S2/README.md](Fish-Audio-S2/README.md) | 2026-03最强表现力TTS，80+语言，⚠️商业授权 | ⭐⭐⭐⭐⭐ |
| **Dia2** 🆕 | [Dia2/README.md](Dia2/README.md) | Apache 2.0免费商用，英文对话TTS，非言语标签 | ⭐⭐⭐⭐ |
| **LuxTTS** 🆕 | [LuxTTS/README.md](LuxTTS/README.md) | 3秒克隆，150x实时，仅需1GB显存，48kHz输出 | 🥇 首选 |
| **Higgs Audio V2** 🆕 | [Higgs-Audio/README.md](Higgs-Audio/README.md) | 李沐团队，千万小时训练，SOTA情感表达，Apache 2.0 | 🥇 首选 |
| **VibeVoice-1.5B** 🆕 | [VibeVoice/README.md](VibeVoice/README.md) | 微软开源，90分钟多角色播客，MIT协议 | ⭐⭐⭐⭐⭐ |
| **Kokoro-82M** 🆕 | [Kokoro-82M/README.md](Kokoro-82M/README.md) | 82M参数，CPU运行，8中文音色，Apache 2.0 | 🥇 CPU首选 |
| **KaniTTS-2** 🆕 | [KaniTTS2/README.md](KaniTTS2/README.md) | 3GB显存，LLM架构，从零预训练代码 | ⭐⭐⭐⭐ |
| **Pocket TTS** 🆕 | [Pocket-TTS/README.md](Pocket-TTS/README.md) | Kyutai，纯CPU运行，6x实时，仅英文，MIT | ⭐⭐⭐⭐ |
| **NeuTTS Air** 🆕 | [NeuTTS-Air/README.md](NeuTTS-Air/README.md) | 全球首个端侧即时克隆，2GB RAM运行，Apache 2.0 | 🥇 端侧首选 |
| **Covo-Audio** 🆕 | [Covo-Audio/README.md](Covo-Audio/README.md) | 腾讯2026-03-26全新发布，7B统一架构（语音识别+推理+合成），CC BY 4.0，智能-音色解耦 | 🥇 全双工语音助手首选 |
| **TADA** 🆕 | [TADA/README.md](TADA/README.md) | Hume AI 2026-03-11开源，**文本-声学双对齐**架构，零幻觉TTS，RTF 0.09（5倍速），**700秒超长上下文**（全场最长），边缘设备可运行，1B英语+3B多语言双版本 | 🥇 高可靠性/超长内容首选 |
| **Silma TTS** 🆕 | [Silma-TTS/README.md](Silma-TTS/README.md) | SILMA AI 2026-03发布，150M参数，阿英双语，F5-TTS架构，RTF 0.12，Tashkeel阿拉伯语变音，Apache 2.0 | 🥇 阿拉伯语首选 |
| **Irodori-TTS-500M-v2** 🆕 | [Irodori-TTS-500M-v2.md](Irodori-TTS-500M-v2.md) | Aratako开发，2026-03-29发布v2版本，**Emoji风格控制**首创（文本/Emoji双驱动），**VoiceDesign**文本风格模型，**PEFT LoRA**支持，多GPU训练，torch.compile+KV-cache双重加速，日语专用 | ⭐⭐⭐⭐ 日语首选（v2推荐，v1见Irodori-TTS/） |
| **Zonos TTS** 🆕 | [Zonos/README.md](Zonos/README.md) | Zyphra AI，1.6B参数，**首个SSM架构TTS开源实现**，4种情绪控制，44kHz高保真，Apache 2.0 | 🥇 **情绪配音/SSM技术首选** |

### 🔌 集成指南
- **[集成指南/README.md](集成指南/README.md)** — OpenClaw完整集成方案
- **voice-clone-assistant Skill** — `/workspace/skills/voice-clone-assistant/SKILL.md` 🎯 **2026-03-31 新增**：OpenClaw 语音克隆助手 Skill，支持触发识别、模型选择决策树、Python推理代码、音频预处理、质量问题排查，覆盖 Qwen3-TTS / CosyVoice2 / ChatTTS / GPT-SoVITS 四大主流方案

### 🆕 本次新增（2026-04-01 20:05）
- **Zonos TTS** 🆕 | [Zonos/README.md](Zonos/README.md) | Zyphra AI 2025-02 发布，**首个引入 SSM 架构的开源 TTS 模型**（1.6B 参数）；5秒极低样本克隆，**内置4种情绪控制**（快乐/恐惧/悲伤/愤怒），44kHz 高保真输出（全场最高采样率之一），RTX 4090 上 2倍实时速度，Apache-2.0 完全可商用；提供 Transformer 和 Hybrid（首个 SSM-TTS）双变体；适合情感配音/动画旁白/商业语音助手/多语言应用

### 🆕 上次新增（2026-04-01 19:38）
- **LongCat-AudioDiT** 🆕 | [LongCat-AudioDiT/README.md](LongCat-AudioDiT/README.md) | 美团 LongCat 团队 2026-03 发布，**首个波形潜空间扩散 TTS**；3.5B/1B 双规格，**Seed 基准 SIM 0.818 全场最高**（超越字节 Seed-TTS），中英双语零样本克隆，MIT 协议；核心创新：Wav-VAE 直接操作波形潜码，APG 引导替代 CFG；适合对声音相似度要求最高的有声书/短视频/语音助手场景
- **LEMAS-TTS** 🆕 | [LEMAS-TTS/README.md](LEMAS-TTS/README.md) | IDEA研究院 2026-01 发布，**15万小时超大规模多语言语音套件**（全场最大规模之一），**10种语言**（中英西俄法德意葡印尼越南），Flow-Matching 架构，基于 F5-TTS 改进；同时支持零样本 TTS + 词级 Speech Editing 双能力，CC BY 4.0 可商用（需署名）；适合多语言出海应用、东南亚/欧洲市场
- 更新 README.md 目录索引（新增2个方案入口）
- 资源库现累计收录 **41 个**开源语音克隆方案

### 🆕 上次新增（2026-03-31 10:19）
- **懒人速查卡.md** 🆕 | [懒人速查卡.md](懒人速查卡.md) | 🎯 **2026-03-31 新增**：一分钟速查单页，涵盖按场景一句话推荐（20+场景）、命令速查（Qwen3-TTS / CosyVoice2 / ChatTTS / GPT-SoVITS / Fish Audio / LuxTTS）、显存需求速查表、中英文选择流程图、常见坑与避让指南、License 速查表
- **voice-clone-assistant Skill** 🆕 | [`/workspace/skills/voice-clone-assistant/SKILL.md`](../skills/voice-clone-assistant/SKILL.md) | OpenClaw 语音克隆助手 Skill，完整覆盖触发识别 → 模型选择 → 推理调用 → 音频预处理 → 返回结果全流程，含情感控制/长文本/多语言进阶用法及常见问题排查

### 🆕 上次新增（2026-03-31 09:21）
- **TADA** 🆕 | [TADA/README.md](TADA/README.md) | Hume AI **2026-03-11** 开源，**文本-声学双对齐（Text-Acoustic Dual Alignment）**架构，**从结构上杜绝幻觉**，1000+样本零幻觉；RTF **0.09**（全场最快之一），比同类 LLM-TTS 快 5 倍；2048 token 上下文可生成约 **700 秒音频**（全场最长上下文）；1B（英语）/3B（多语言）双版本；Llama 底座 + Flow-Matching；EARS 评测说话人相似度 **4.18/5.0**；适合有声书/医疗/金融等高可靠性场景 | 🥇 **零幻觉超长语音首选** |

## 🆕 上次新增（2026-03-31 07:28）
- **Qwen3-TTS Skill** 🆕 | [Qwen3-TTS-Skill/README.md](Qwen3-TTS-Skill/README.md) | 独立开发者社区2026-03-31发布，Qwen3-TTS 本地化部署增强工具包，三种高级语音模式（情感指令内置音色/自然语言音色定制/参考音频克隆），内置长文稿批量配音工作流，AI 文稿分析与审核功能，完全本地运行保护隐私 | 🥇 隐私优先首选 |

## 🆕 上次新增（2026-03-27 21:25）
- **MegaTTS3** | [MegaTTS3/README.md](MegaTTS3/README.md) | 字节跳动2025-03发布，**0.45B极轻量**（全场最小参数），Sparse Alignment增强Latent Diffusion，Apache-2.0完全免费商用，**中英代码切换（Code-Switching）原生支持**，精细口音强度控制（p_w/t_w参数），⚠️即时克隆需通过官方工具预提取潜码 | 🥇 低显存/双语内容创作首选 |

### 🆕 上次新增（2026-03-27 20:38）
- **GLM-TTS** | [GLM-TTS/README.md](GLM-TTS/README.md) | 智谱AI 2025-12发布，Apache-2.0+MIT，**两阶段GRPO多奖励强化学习**，CER 0.89%全场开源中文TTS第二低，中英混合原生支持，音素级发音控制，四川/东北方言，3秒克隆，24kHz输出 | 🥇 中文克隆首选之一 |
- **Step-Audio** | [Step-Audio/README.md](Step-Audio/README.md) | 阶跃星辰+吉利 2025-02发布，**全球首个产品级全链路语音交互模型**，130B统一架构（理解+生成），HSK-6中文评测第一，情感+方言+歌唱+Rap，AQTA评分4.11，Apache 2.0，TTS-3B轻量版仅8GB显存 | 🥇 全双工语音助手首选 |

### 🆕 上次新增（2026-03-27 20:05）
- **Sesame CSM** | [Sesame-CSM/README.md](Sesame-CSM/README.md) | Sesame 2025-03发布，对话式语音生成（1B Llama底座），Apache 2.0，HuggingFace原生集成，支持多轮对话上下文建模 | ⭐⭐⭐ 对话AI助手 |
- **UniVoice** | [UniVoice/README.md](UniVoice/README.md) | 厦门大学+上海创新院 2025发布，**ASR+TTS统一架构**（首创），SmolLM2-360M基座，MIT协议，0.4B极轻量，可同时做语音识别和语音合成 | ⭐⭐⭐ 研究/极轻量 |
- **OpenAudio S1/S1-mini** | [OpenAudio-S1/README.md](OpenAudio-S1/README.md) | Fish Speech 2025发布，4B/0.5B双规格，RLHF训练，WER 0.8%，Speaker Sim 0.332，50+情感标签，CC-BY-NC-SA-4.0（非商用免费） | ⭐⭐⭐⭐ 非商用首选 |

### 🆕 近期新增（2026-03-27 下午）
- **Voxtral TTS** | [Voxtral-TTS/README.md](Voxtral-TTS/README.md) | Mistral 2026-03-26全新发布，4B参数，90ms延迟，<5秒克隆，9语言，跨语言克隆能力 | 🥇 非中文首选 |
- **VoxCPM 1.5** 🆕 | [VoxCPM/README.md](VoxCPM/README.md) | OpenBMB 2025-12发布，**44.1kHz CD级音质**（全场最高），Token-Free LocDiT扩散架构，800M参数，RTF 0.15，Apache 2.0 | 🥇 高保真首选 |
- **Xiaomi MiMo-V2-TTS** 🆕 | [MiMo-V2-TTS/README.md](MiMo-V2-TTS/README.md) | 小米2026-03-18发布，超亿小时预训练，SSML情感控制，粤语/四川话/台湾腔方言，歌唱合成，OpenAI兼容API | 🥇 中文情感首选 |
- **Orpheus TTS** 🆕 | [Orpheus-TTS/README.md](Orpheus-TTS/README.md) | Canopy 2025-03发布，Llama-3.2底座，25ms极低延迟，情感标签(laughs/sighs)，3B/1B/150M多规格 | 🥇 实时对话首选 |
- **Chatterbox-TTS** 🆕 | [Chatterbox-TTS/README.md](Chatterbox-TTS/README.md) | Resemble AI出品，情感夸张幅度控制（首创），内嵌水印，23+语言，5秒克隆，200ms延迟 | ⭐⭐⭐ 动画/游戏配音 |
| **GLM-TTS** 🆕 | [GLM-TTS/README.md](GLM-TTS/README.md) | 智谱AI，GRPO强化学习，CER 0.89%，中英混合，音素级控制，Apache-2.0+MIT | 🥇 中文克隆首选之一 |
| **Step-Audio** 🆕 | [Step-Audio/README.md](Step-Audio/README.md) | 阶跃星辰130B全双工，HSK-6中文第一，情感+方言+歌唱+Rap，Apache 2.0，TTS-3B轻量版8GB显存 | 🥇 全双工语音助手首选 |

---

## 🚀 快速开始

### 第一步：确定你的场景

```
有目标音色参考音频？
├─ 是 → Qwen3-TTS 或 CosyVoice2（首选克隆方案）
└─ 否 → ChatTTS v2（无需克隆的对话TTS）
```

### 第二步：安装

```bash
# 推荐组合：一键安装脚本
bash <(curl -fsSL https://raw.githubusercontent.com/.../env_setup.sh)
```

### 第三步：生成你的第一条语音

```python
from qwen3_tts import Qwen3TTS
model = Qwen3TTS("Qwen/Qwen3-TTS-12Hz-1.7B-Base", quantize="int8")

# 克隆模式（3秒参考音频）
audio = model.generate(
    text="今天天气真好！",
    ref_audio="my_voice.wav"
)
```

---

## 📌 本次更新（2026-03-31 19:39）

本次Agent执行新增了以下内容：

## 📌 本次更新（2026-04-01 20:09）

### 🆕 选型决策树.md 🆕
- **文件名**：[选型决策树.md](选型决策树.md)
- **内容**：🎯 可视化决策树，帮助用户在 30 秒内找到最适合的语音克隆方案；覆盖 6 大决策分支（硬件/延迟/相似度/语言/情绪/多语言）、 5 类需求类型（快速克隆/高质量训练/实时交互/多语言出海/垂直场景）、 8 个常见坑避让指南；与懒人速查卡互为补充，决策树侧重"我是谁→选哪个"，速查卡侧重"知道了→怎么用"
- **亮点功能**：
  - 按硬件配置自动筛选（无GPU / <8GB显存 / 8GB+）
  - 按延迟需求分流（实时<200ms / 普通）
  - 按场景推荐（有声书/短视频/游戏/医疗/歌唱等）
  - 一页总结表（预算→场景→方案）
- 资源库累计收录：**41 个**开源语音克隆方案

---

### 🆕 Qwen3-TTS oQ8 量化版 🆕
- **文件名**：[Qwen3-TTS/社区量化版-beaupi-Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8.md](Qwen3-TTS/社区量化版-beaupi-Qwen3-TTS-12Hz-1.7B-CustomVoice-oQ8.md)
- **来源**：🤖 HuggingFace Trending 实时捕获（更新于本次扫描期间）
- **内容**：社区开发者 beaupi 打包的 Qwen3-TTS-1.7B CustomVoice oQ8 优化量化版，显存需求从 6-8GB 降至约 3-4GB，推理速度提升，音质损失极小；继承阿里 Qwen 商用协议，可直接替换模型路径使用；推荐中低端 GPU / Mac 用户采纳
- **资源库累计收录**：36 个开源语音克隆方案

---

## 📌 本次更新（2026-03-27 16:54）

本次Agent执行新增了以下内容：

1. **VoxCPM 1.5（2025-12-05，OpenBMB）** 🆕
   - 详细分析报告：[VoxCPM/README.md](VoxCPM/README.md)
   - **44.1kHz CD级音质**（全场最高采样率）
   - **Token-Free LocDiT 扩散架构**（端到端连续表征，无需离散tokenizer）
   - 800M 参数，RTF 0.15（H200单卡），流式推理支持
   - **LoRA 全套微调代码**（全参数 + LoRA 两种模式）
   - 活跃社区生态：ComfyUI / ONNX / NanoVLLM / Apple Neural Engine / Rust
   - Apache 2.0 完全免费商用
   - **高保真配音首选**：有声书、音乐、人声等对音质有高要求的场景

2. **模型对比表扩充**
   - 新增 VoxCPM 1.5 一条记录（高保真维度）
   - README 目录索引新增 VoxCPM 入口
   - 资源库现累计收录 **30 个**开源语音克隆方案

---

## 📌 本次更新（2026-03-27 16:12）

本次Agent执行主要新增了以下内容：

1. **Higgs Audio V2.5 详细报告（2026-01-18）** 🆕
   - 详细分析报告：[Higgs-Audio/README.md](Higgs-Audio/README.md)（已更新）
   - V2.5：3B参数压缩至 **1B**，GRPO对齐策略，速度与精度双超越
   - 显存需求：8GB+ → **4-6GB**，更适合个人GPU
   - Apache 2.0 完全免费商用

2. **Xiaomi MiMo-V2-TTS（2026-03-18，小米）** 🆕
   - 详细分析报告：[MiMo-V2-TTS/README.md](MiMo-V2-TTS/README.md)
   - 小米V2系列之一，基于超亿小时语音预训练
   - **SSML情感标签控制**（句内多粒度情感切换）
   - **粤语/四川话/台湾腔**中文方言原生支持
   - 歌唱合成（音高+颤音控制）
   - OpenAI兼容API（platform.xiaomimimo.com）

3. **Orpheus TTS（2025-03，Canopy Labs）** 🆕
   - 详细分析报告：[Orpheus-TTS/README.md](Orpheus-TTS/README.md)
   - 基于 **Llama-3.2-3B** 底座，拟人化情感表达
   - **25ms级别 TTFB**，流式推理快于播放（业界顶尖）
   - 非言语标签控制：`laughs` / `sighs` / `coughs` / `pause`
   - 3B / 1B / 150M 多规格可选，灵活平衡质量与速度

4. **Chatterbox-TTS（Resemble AI）** 🆕
   - 详细分析报告：[Chatterbox-TTS/README.md](Chatterbox-TTS/README.md)
   - **首创情感夸张幅度滑块**（Amplitude Slider）
   - 内嵌不可感知水印，音频来源可追溯
   - **23+语言**，零样本克隆仅需5秒，TTFB ~200ms

5. **模型对比表 + README目录更新**
   - 新增 MiMo-V2-TTS、Orpheus TTS、Chatterbox-TTS 三条记录
   - Higgs Audio README 更新 V2.5 专项分析章节
   - **资源库现累计收录 20 个开源语音克隆方案**

---

## 📌 上次更新（2026-03-27 下午）

本次Agent执行主要新增了以下内容：

1. **NeuTTS Air（2025-10，Neuphonic）** 🆕
   - 详细分析报告：[NeuTTS-Air/README.md](NeuTTS-Air/README.md)
   - 全球首个**端侧即时语音克隆 TTS**（无需云端，手机/电脑/树莓派均可运行）
   - 0.5B 参数（Qwen 0.5B 骨干 + NeuCodec 50Hz），Apache 2.0 完全免费商用
   - 仅需 **2GB RAM**，Galaxy A25 手机即可实时合成（20-45 tokens/s）
   - **3-15秒参考音频**即可克隆任意音色，支持 GGUF 量化格式
   - ⚠️ 注意：仅英文，输出带 Perth 感知水印

2. **模型对比表扩充**
   - 新增 NeuTTS Air 一条记录
   - 详细分析章节新增 3.8 NeuTTS Air 完整报告
   - 资源库现累计收录 **16 个**开源语音克隆方案

---

## 📌 本次更新（2026-03-27 早次）

本次Agent执行主要新增了以下内容：

1. **LuxTTS（2026-01-23 发布）** 🆕
   - 详细分析报告：[LuxTTS/README.md](LuxTTS/README.md)
   - 基于ZipVoice蒸馏，3秒克隆，150倍实时推理
   - 显存需求仅 **1GB**（全场最低），48kHz高保真输出
   - Apache 2.0 完全免费商用

2. **Higgs Audio V2（2025-07，李沐/Boson AI）** 🆕
   - 详细分析报告：[Higgs-Audio/README.md](Higgs-Audio/README.md)
   - **1000万小时**音频数据预训练，3B参数
   - EmergentTTS-Eval 情感维度 **75.7%胜率**击败gpt-4o-mini-tts
   - DualFFN Adapter架构，WER↓15%，说话人相似度↑23%
   - Apache 2.0 完全免费商用

3. **VibeVoice-1.5B（微软开源）** 🆕
   - 详细分析报告：[VibeVoice/README.md](VibeVoice/README.md)
   - 单次生成 **最长90分钟**连续语音
   - 支持 **4位说话人**同时对话，自然轮转
   - 支持英语/普通话中文，中英混用
   - MIT协议免费商用

4. **Kokoro-82M v1.1（hexgrad）** 🆕
   - 详细分析报告：[Kokoro-82M/README.md](Kokoro-82M/README.md)
   - 仅 **82M参数**，模型大小 ~165MB
   - **CPU上高效运行**（ONNX优化），树莓派可用
   - 内置 **8种中文音色**（小贝/小妮/云希/云扬等）
   - Apache 2.0 完全免费商用

5. **KaniTTS-2（2026-02-11，NineNineSix）** 🆕
   - 详细分析报告：[KaniTTS2/README.md](KaniTTS2/README.md)
   - 400M参数，**仅需3GB显存**即可运行
   - LLM-based架构（Frame-level Position Encoding）
   - 提供**从零预训练代码框架**，可完全定制
   - Apache 2.0 完全开源

6. **Pocket TTS（2026-01-13，Kyutai Labs）** 🆕
   - 详细分析报告：[Pocket-TTS/README.md](Pocket-TTS/README.md)
   - **100M参数，纯CPU运行**，MacBook Air M4上6倍实时
   - **完全无需GPU**，2核CPU即可
   - 支持任意音频文件克隆（safetensors快速加载）
   - ⚠️ 当前版本仅支持英文
   - MIT协议

7. **模型对比表更新**
   - 新增 LuxTTS、Higgs Audio V2、VibeVoice-1.5B、Kokoro-82M、KaniTTS-2、Pocket TTS 六条记录
   - 选型决策树新增"低显存快速克隆"和"多角色长音频"分支

---

## 📌 上次更新（2026-03-27）

本次Agent执行主要新增了以下内容：

1. **CosyVoice 3.0（2025-12-15 重大版本）** 🆕
   - 详细分析报告：[CosyVoice3/README.md](CosyVoice3/README.md)
   - 阿里通义实验室发布，百倍训练数据（1M小时 vs 10k小时）
   - 9种主流语言 + 18+种中文方言（东北话/四川话/粤语等）
   - 发音修补（Pinyin/音素级精准控制）
   - 跨语言克隆（中文参考音频 → 英文合成）
   - Instruct 指令控制（情感/语速/音量）
   - 低至 150ms 流式延迟，Apache 2.0 完全免费商用

2. **GPT-SoVITS V3 / V4 更新** 🆕
   - 参数量大幅提升：90M+77M（V2）→ 330M+77M（V3）
   - 训练数据：5k小时（V2）→ 7k小时（V3）
   - 音色相似度 SIM：0.549（V2）→ 0.702（V3），逼近真人 0.760
   - V4：修复 V3 金属噪音伪影，原生 48kHz 输出
   - V2Pro：超越 V4 性能，V2 硬件成本

3. **选型决策树更新**
   - 通用中文克隆首选 → CosyVoice 3.0
   - 需要微调 + 长期稳定 → GPT-SoVITS V4 + V2Pro
   - 无参考音频 → ChatTTS v2

---

## 📌 上次更新（2026-03-26）

本次Agent执行主要新增了以下内容：

1. **Fish Audio S2 Pro（2026-03 最新发布）**
   - 详细分析报告：[Fish-Audio-S2/README.md](Fish-Audio-S2/README.md)
   - 5B参数 Dual-AR 架构，80+语言，Time-to-first-audio ~100ms
   - 15,000+ 精细控制标签（情感/韵律/非言语）
   - ⚠️ 注意：研究/非商用免费，商业使用需单独授权

2. **Dia2（Nari Labs）**
   - 详细分析报告：[Dia2/README.md](Dia2/README.md)
   - Apache 2.0 完全开源，可免费商用
   - 原生支持 `[S1]` / `[S2]` 多角色对话标签
   - 支持非言语声音：`(laughs)` `(coughs)` `(sighs)` 等
   - 仅支持英文，适合英文对话/播客场景

3. **模型对比表更新**
   - 新增 Fish Audio S2 Pro 和 Dia2 两条记录
   - 更新详细分析章节（3.7 和 3.8）
   - 更新历史日志

---

## 📌 上次更新（2026-03-25）

上次Agent执行主要新增了以下内容：

1. **Qwen3-TTS（2026年首选）** — 详细安装、推理、微调指南
2. **CosyVoice2** — 阿里开源，稳定可靠的克隆方案
3. **F5-TTS** — 极速克隆（2秒），推理速度最快
4. **IndexTTS-2** — B站官方，情感分离控制专家
5. **ChatTTS v2** — 无需克隆的对话TTS
6. **OpenClaw集成指南** — 完整的自动化工作流

---

## 📌 更早更新（2026-03-24）

- MOSS-TTS、Qwen3-TTS、CosyVoice2、F5-TTS、IndexTTS-2、ChatTTS v2 六大方案详细技术报告
- OpenClaw Skill 集成方案
- 推理脚本标准化（qwen3_tts_infer.py / chattts_infer.py / cosyvoice_infer.py）
- 环境安装脚本（env_setup.sh）

---

## 🔗 重要资源链接

| 资源 | 链接 |
|------|------|
| Qwen3-TTS GitHub | https://github.com/QwenLM/Qwen3-TTS |
| CosyVoice2 GitHub | https://github.com/FunAudioLLM/CosyVoice |
| F5-TTS GitHub | https://github.com/SWivid/F5-TTS |
| ChatTTS GitHub | https://github.com/2noise/ChatTTS |
| GPT-SoVITS GitHub | https://github.com/RVC-Boss/GPT-SoVITS |
| IndexTTS GitHub | https://github.com/IndexTTS |
| Fish Audio S2 Pro | https://github.com/fishaudio/fish-speech |
| Dia2 GitHub | https://github.com/nari-labs/dia2 |

---

*本资料库由免费语音克隆方案Agent自动维护*

---

## 📌 本次更新（2026-03-27 20:38）

本次Agent执行新增了以下内容：

1. **GLM-TTS（智谱 AI，2025-12-11）** 🆕
   - 详细分析报告：[GLM-TTS/README.md](GLM-TTS/README.md)
   - **两阶段架构**：Llama LLM + Flow Matching + Vocoder
   - **GRPO 多奖励强化学习**（首创）：相似度+CER+情感+笑声四维奖励，CER 从 1.03 降至 **0.89%**（全场开源中文 TTS 第二低）
   - **3~10秒零样本克隆**，音素级发音控制（解决多音字问题）
   - **中英混合原生支持**，四川话/东北话方言
   - 许可证：Apache-2.0（代码）+ MIT（模型权重），完全可商用
   - GitHub：https://github.com/zai-org/GLM-TTS | HuggingFace：zai-org/GLM-TTS
   - **中文克隆首选之一**：适合有精细发音控制需求的场景

2. **Step-Audio（阶跃星辰+吉利，2025-02-18）** 🆕
   - 详细分析报告：[Step-Audio/README.md](Step-Audio/README.md)
   - **全球首个产品级全链路语音交互模型**：ASR+LLM+TTS 统一架构（130B 参数），全双工端到端对话，AQTA 评分 4.11/5
   - **HSK-6 汉语水平考试评测第一**，最懂中国话的开源语音模型
   - **情感+方言（粤语/四川话）+歌唱+Rap 全方位控制**
   - TTS-3B 轻量版：仅 **~8GB 显存**即可运行，CER 1.17%（中文 TTS 一流水平）
   - 许可证：Apache 2.0
   - GitHub：https://github.com/stepfun-ai/Step-Audio | HuggingFace：stepfun-ai/Step-Audio-Chat
   - **全双工语音助手首选**：适合企业级语音交互产品

3. **模型对比表扩充**
   - 新增 GLM-TTS 和 Step-Audio 两条记录
   - README 目录索引新增两个方案入口
   - 资源库现累计收录 **32 个**开源语音克隆方案
