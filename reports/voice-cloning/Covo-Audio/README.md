# Covo-Audio — 腾讯统一语音大模型（识别+推理+合成）

> 🤖 免费语音克隆方案Agent | 2026-03-27 新增（发布于 2026-03-26）

---

## 一、模型概览

| 指标 | 数值 |
|------|------|
| **发布时间** | **2026年3月26日**（今日） |
| **开发团队** | 腾讯（Tencent） |
| **参数量** | **7B**（70亿） |
| **架构** | 三模态语音-文本链式交织架构 |
| **音频输出** | 24 kHz |
| **训练数据** | 2万亿 tokens（语音+文本） |
| **许可协议** | **CC BY 4.0**（可商用，需署名） |
| **GitHub** | [Tencent/Covo-Audio](https://github.com/Tencent/Covo-Audio) |
| **HuggingFace** | [tencent/Covo-Audio-Chat](https://huggingface.co/tencent/Covo-Audio-Chat) |
| **技术报告** | [arXiv:2602.09823](https://arxiv.org/abs/2602.09823) |

---

## 二、核心亮点

### 🔗 三模态统一架构
首个将**语音识别、推理思考、语音合成**三大能力统一在一个端到端架构中的开源模型：

- **语音编码器**：Whisper-large-v3，以 50Hz 采样率捕获输入语音
- **下采样模块**：三层（线性+卷积）压缩至 6.25Hz
- **语言模型基座**：基于 Qwen2.5-7B-Base，适应交织的语音特征与文本 token
- **语音分词器**：WavLM-large，25Hz 输出离散语音 token（16,384 个码本）
- **声码器**：Flow-Matching + BigVGAN，重建 24kHz 波形

### 🧠 层级三模态交织（HTSTI）
关键创新：首次在**短语/句子级别**对齐连续声学特征、离散语音 token 和自然语言文本（之前方法仅在词/字级别），实现真正的跨模态语义理解。

### 🎤 智能-音色解耦（Intelligence-Speaker Decoupling）
将对话智能与音色渲染分离，支持：
- 最小化 TTS 数据即可切换音色
- 单次部署服务多个音色 persona，无需单独微调
- 与 MiniMax Speech 等专业 TTS 模块集成

### 🔄 全双工对话
- 用户和模型可同时说话
- Chunk-streaming，1:4 用户/模型 chunk 比例
- 每 chunk 代表 0.16 秒音频
- 支持打断（Barge-in）

### ⏱ 架构 Token 控制
内置三种特殊 token：
- `THINK` — 模型进入倾听/思考状态
- `SHIFT` — 标记对话轮次切换
- `BREAK` — 表示打断/中断

### 🏆 benchmark 表现
| Benchmark | 分数 |
|-----------|------|
| MMAU（音频理解） | **75.30%** |
| MMSU（语音理解，平均准确率） | **66.64%** |
| URO-Bench 中文赛道 | **超越 Qwen3-Omni** |

> 在多个音频和语音理解任务上，Covo-Audio 7B 对标甚至超越部分 32B 参数系统。

---

## 三、适用场景

| 场景 | 适配度 |
|------|--------|
| 全双工语音对话助手 | ⭐⭐⭐⭐⭐ |
| 多轮语音推理 | ⭐⭐⭐⭐⭐ |
| 语音客服/陪伴机器人 | ⭐⭐⭐⭐ |
| 语音克隆+智能对话 | ⭐⭐⭐⭐ |
| 语音驱动的 Agent | ⭐⭐⭐⭐ |
| 纯 TTS 语音克隆（精细控制） | ⭐⭐⭐（建议配合专业 TTS） |

---

## 四、安装与使用

### 1. 依赖安装

```bash
git clone https://github.com/Tencent/Covo-Audio.git
cd Covo-Audio
pip install -r requirements.txt
```

### 2. 模型下载

```bash
# HuggingFace
git lfs install
git clone https://huggingface.co/tencent/Covo-Audio-Chat
```

### 3. Python API

```python
from covo_audio import CovoAudioChat

# 加载模型（需 ~14GB 显存 bf16）
model = CovoAudioChat.from_pretrained("tencent/Covo-Audio-Chat")

# 对话生成（语音输入，文本/语音输出）
response = model.chat(
    audio="user_speech.wav",
    text="帮我解释量子计算",  # 可选文本提示
)

print(response["text"])
# 生成音频可后续接 TTS 模块（配合 CosyVoice3 / Covo-TTS）

# 全双工对话模式
async for chunk in model.chat_stream(audio_stream=user_audio_stream):
    print(chunk["text"], end="", flush=True)
```

### 4. 推理参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `temperature` | 采样温度 | 0.7 |
| `top_p` | nucleus 采样 | 0.9 |
| `max_tokens` | 最大生成长度 | 512 |
| `voice_id` | 音色 ID（解耦后支持） | "default" |
| `stream` | 是否流式 | True |

### 5. 语音克隆工作流（配合 CosyVoice3）

```python
from covo_audio import CovoAudioChat
from cosyvoice import CosyVoice

# Step 1: Covo-Audio 负责对话理解与推理
covo = CovoAudioChat.from_pretrained("tencent/Covo-Audio-Chat")
response_text = covo.chat(audio="user.wav", text=None)

# Step 2: CosyVoice3 负责克隆音色合成
cosy = CosyVoice.load_model('CosyVoice-0.5B')
cloned_audio = cosy.clone_and_synthesize(
    reference_audio="target_voice.wav",
    text=response_text
)
```

---

## 五、与其他开源方案对比

| 方案 | 参数量 | 统一架构 | 推理 | 全双工 | 中文 | 协议 | 定位 |
|------|--------|----------|------|--------|------|------|------|
| **Covo-Audio** | **7B** | ✅ 三模态统一 | ⭐⭐⭐ | ✅ | ✅ | CC BY 4.0 | 全双工语音推理 |
| CosyVoice3 | 0.5B | ❌ 纯TTS | ⭐⭐⭐⭐⭐ | ❌ | ✅+方言 | Apache 2.0 | 专业TTS/克隆 |
| Qwen3-TTS | 0.6-1.7B | ❌ 纯TTS | ⭐⭐⭐⭐⭐ | ❌ | ✅ | Apache 2.0 | 极速TTS |
| Dia2 | 1.6B | ❌ 对话TTS | ⭐⭐⭐ | ❌ | ❌ | Apache 2.0 | 英文对话TTS |
| Mistral Voxtral | 4B | ❌ 纯TTS | ⭐⭐⭐⭐ | ❌ | 部分 | Apache 2.0 | 低延迟TTS |
| MiniMax Speech | - | ❌ 纯TTS | ⭐⭐⭐⭐⭐ | ❌ | ✅ | 专有 | 商用TTS |

---

## 六、硬件需求

| 配置 | bf16 精度 | fp32 精度 |
|------|-----------|-----------|
| **GPU** | ~14GB VRAM | ~28GB VRAM |
| CPU（推理） | 需量化（GPTQ/AWQ） | ❌ |
| 推荐 | RTX 4090 / A100 40G | — |

> 官方提供 GPTQ/INT4 量化版本，可在消费级 GPU（RTX 3090/4060Ti 16GB）运行。

---

## 七、已知限制

| 问题 | 说明 |
|------|------|
| 全双工模式长静音 | 可能导致模型过早响应（已在 GaokaoEval 基准中标注） |
| 纯 TTS 精细控制 | 不如 CosyVoice3/Qwen3-TTS，建议配合专业 TTS 使用 |
| 非流式 TTS 输出 | 需外接声码器/流式 TTS 模块 |
| CC BY 4.0 协议 | 商业使用需署名（腾讯） |

---

## 八、合规使用

- ✅ 可用于学术研究和商业产品（需署名）
- ✅ 可集成到开源/闭源项目
- ❌ 不可用于未经同意的声音冒充
- ❌ 不可用于制造虚假新闻/深度伪造内容

---

## 九、相关资源

- [GitHub](https://github.com/Tencent/Covo-Audio)
- [HuggingFace](https://huggingface.co/tencent/Covo-Audio-Chat)
- [arXiv 技术报告](https://arxiv.org/abs/2602.09823)
- [腾讯混元官方](https://hunyuan.tencent.com/)
