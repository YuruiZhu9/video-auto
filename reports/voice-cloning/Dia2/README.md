# Dia2 — 流式对话 TTS，Apache 2.0 完全开源

> 🤖 免费语音克隆方案Agent | 新增于 2026-03-26

---

## 基本信息

| 项目 | 信息 |
|------|------|
| **GitHub** | https://github.com/nari-labs/dia2 |
| **HuggingFace** | https://huggingface.co/nari-labs/Dia2-2B |
| **开发者** | Nari Labs |
| **Stars** | 快速增长中 |
| **最新版本** | Dia2-1B / Dia2-2B（2025年底发布） |
| **许可证** | ✅ **Apache 2.0**（可免费商用） |
| **语言支持** | 🌐 **仅限英文**（最长2分钟生成） |
| **声音克隆** | ⚠️ 非直接克隆，但支持音色前缀控制 |

---

## 核心亮点

- 🆓 **Apache 2.0 许可证**：完全免费，可商业使用
- ⚡ **流式生成**：不需要完整文本，输入即开始生成
- 🎭 **对话 TTS**：原生支持 `[S1]` / `[S2]` 多角色对话标签
- 😂 **非言语生成**：支持笑声 `(laughs)`、咳嗽 `(coughs)`、清嗓等标签
- 🎙️ **前缀音色控制**：通过参考音频影响输出音色
- 🔧 **CUDA 优化**：支持 CUDA Graph 加速推理

---

## 技术规格

| 参数 | Dia2-1B | Dia2-2B |
|------|---------|---------|
| 参数量 | 1B | 2B |
| 最大生成长度 | 2 分钟 | 2 分钟 |
| 最大上下文步数 | 1500 | 1500 |
| 帧率（Mimi codec） | ~12.5 Hz | ~12.5 Hz |
| 默认精度 | bfloat16 | bfloat16 |
| CUDA 要求 | 12.8+ | 12.8+ |

---

## 适用场景

| 场景 | 推荐度 | 说明 |
|------|--------|------|
| 英文对话助手 | ⭐⭐⭐⭐⭐ | 流式 TTS，无需等待完整文本 |
| 多角色对话 | ⭐⭐⭐⭐⭐ | 原生支持 `[S1]` / `[S2]` 标签 |
| 有情感的真实对话 | ⭐⭐⭐⭐ | 支持笑声、停顿等非言语标签 |
| 英文应用集成 | ⭐⭐⭐⭐ | Apache 2.0，完全免费商用 |
| 中文场景 | ❌ | 仅支持英文，不适合中文项目 |

---

## 与其他方案对比

| 维度 | Dia2 | ChatTTS v2 | Qwen3-TTS | CosyVoice2 |
|------|------|-----------|-----------|-----------|
| 发布时间 | 2025 | 2025 | 2026 | 2024 |
| 语言 | 仅英文 | 中英 | 10+语言 | 20+语言 |
| **许可证** | **Apache 2.0** ✅ | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| 克隆方式 | 前缀控制（非直接克隆） | 生成式 | 零样本克隆 | 零样本克隆 |
| 对话支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 非言语标签 | ✅ `(laughs)` `(coughs)` | 有限 | 部分 | 部分 |
| 流式推理 | ✅ 原生 | 有限 | 流式 | 流式 |
| 中文质量 | ❌ 不支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 安装与使用

### 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 准备输入文件（使用对话标签）
# input.txt 示例：
"""
[S1] Hey, have you tried the new AI model?
[S2] Yeah, it's incredible! The voice sounds so natural.
[S1] Does it support emotion tags?
[S2] (laughs) Absolutely! It can even do (coughs) and other nonverbal sounds.
"""
```

### CLI 推理（无音色控制）

```bash
uv run -m dia2.cli \
  --hf nari-labs/Dia2-2B \
  --input input.txt \
  --cfg 6.0 --temperature 0.8 \
  --cuda-graph --verbose \
  output.wav
```

### CLI 推理（带音色前缀控制）

```bash
uv run -m dia2.cli \
  --hf nari-labs/Dia2-2B \
  --input input.txt \
  --prefix-speaker-1 speaker1.wav \
  --prefix-speaker-2 speaker2.wav \
  --cuda-graph --verbose \
  output_conditioned.wav
```

### Gradio Web UI

```bash
uv run gradio_app.py
# 然后访问 http://localhost:7860
```

### Python API

```python
from dia2 import Dia2, GenerationConfig, SamplingConfig

# 加载模型
dia = Dia2.from_repo("nari-labs/Dia2-2B", device="cuda", dtype="bfloat16")

# 配置
config = GenerationConfig(
    cfg_scale=2.0,
    audio=SamplingConfig(temperature=0.8, top_k=50),
    use_cuda_graph=True,
)

# 生成（支持对话标签）
result = dia.generate(
    "[S1] Hello Dia2! [S2] Hi there! [S1] (laughs) This is amazing.",
    config=config,
    output_wav="dialogue.wav",
    verbose=True
)
```

### 带音色前缀的 Python API

```python
from dia2 import Dia2, GenerationConfig, SamplingConfig

dia = Dia2.from_repo("nari-labs/Dia2-2B", device="cuda", dtype="bfloat16")

config = GenerationConfig(
    cfg_scale=6.0,  # 更高 CFG 增强音色控制
    audio=SamplingConfig(temperature=0.8),
    use_cuda_graph=True,
)

# 使用前缀音色
result = dia.generate(
    "[S1] Let's talk about AI today.",
    config=config,
    prefix_speaker_1="my_voice.wav",  # 音色参考
    output_wav="result.wav",
)
```

---

## 非言语标签详解

Dia2 的独特能力：生成自然的口语非言语声音。

| 标签 | 效果 |
|------|------|
| `(laughs)` | 自然笑声 |
| `(coughs)` | 清嗓/咳嗽 |
| `(sighs)` | 叹气 |
| `(pause)` | 长时间停顿 |
| `(clears throat)` | 清喉音 |
| `(sniffles)` | 吸鼻子 |

### 使用示例

```python
# 自然对话
dialogue = """
[S1] Hey, did you hear about the new AI release? (laughs)
[S2] No, what happened?
[S1] They released a model that can generate speech with emotions!
[S2] That's impressive! (sighs) AI is advancing so fast these days.
[S1] Want to try it out together?
[S2] Absolutely! (pause) Let me set up my environment first.
"""
```

---

## 前缀音色控制详解

虽然 Dia2 不是直接的语音克隆模型，但通过 **prefix conditioning** 可以影响音色：

```bash
# 使用参考音频作为音色前缀
uv run -m dia2.cli \
  --hf nari-labs/Dia2-2B \
  --input input.txt \
  --prefix-speaker-1 my_voice.wav \
  --prefix-speaker-2 another_voice.wav \
  output.wav
```

⚠️ **注意**：Dia2 团队明确说明"由于模型未经特定音色微调，每次生成的音色质量可能有所不同"。建议使用前缀控制或对目标音色进行微调以获得稳定输出。

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 只支持英文 | 确认使用场景；中文场景推荐 Qwen3-TTS 或 CosyVoice2 |
| 音色不稳定 | 使用 `--prefix-speaker` 指定音色前缀，或微调模型 |
| 显存不足 | 使用 Dia2-1B（1B参数，显存需求更低） |
| CUDA 版本问题 | 需要 CUDA 12.8+ 驱动 |
| 中文发音需求 | Dia2 不支持中文，换用 Qwen3-TTS / CosyVoice2 |

---

## OpenClaw 集成建议

Dia2 适合英文对话场景的 OpenClaw 集成：

```python
# 1. 安装
# uv sync（项目目录内）

# 2. Python 脚本调用
import subprocess

def generate_dialogue(text, output_path, prefix_audio=None):
    cmd = [
        "uv", "run", "-m", "dia2.cli",
        "--hf", "nari-labs/Dia2-2B",
        "--input", text,
        "--cuda-graph"
    ]
    if prefix_audio:
        cmd += ["--prefix-speaker-1", prefix_audio]
    cmd.append(output_path)
    subprocess.run(cmd)

# 3. 通过 OpenClaw exec 调用
```

---

## 即将推出的功能

| 功能 | 说明 |
|------|------|
| **Bonsai (JAX)** | JAX 实现版本 |
| **Dia2 TTS Server** | 真正的流式推理服务器 |
| **Sori** | Dia2 驱动的语音到语音引擎（Rust 实现） |

---

## 资源链接

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/nari-labs/dia2 |
| HuggingFace | https://huggingface.co/nari-labs/Dia2-2B |
| 在线体验 | https://huggingface.co/spaces/nari-labs/Dia2-2B |
| Discord | https://discord.gg/bJq6vjRRKv |

---

## 选型建议

```
英文对话场景？
├─ 需要商用 → Dia2 ✅（Apache 2.0，免费商用）
│             或 Qwen3-TTS ✅（英文支持好，克隆能力强）
│
├─ 对话助手/情感丰富 → Dia2 ✅（非言语标签，对话标签）
│
└─ 只需克隆音色 → Qwen3-TTS ✅（3秒克隆，英文优秀）

中文场景？
└─ Dia2 不适用 → Qwen3-TTS / CosyVoice2 / MOSS-TTS
```

---

*本报告由免费语音克隆方案Agent生成，基于2026年3月最新信息。*

---

## 🆕 Dia2-2B 专项（2026-04-12 新增）

| 指标 | 数据 |
|------|------|
| 模型名 | `nari-labs/Dia2-2B` |
| 参数量 | **2B**（另有 1B 变体 `Dia2-1B`）|
| GitHub Stars | **1.1k**（独立仓库 `nari-labs/dia2`）|
| 许可证 | **Apache 2.0**（可商用）|
| 音频编码器 | Kyutai Mimi codec（约 12.5 Hz 帧率）|
| CUDA 要求 | 12.8+ |
| 最大生成时长 | 2分钟（英语）|
| 核心功能 | 流式对话 TTS + 音频条件生成 |

### 与 Dia-1.6B 对比

| 对比项 | Dia-1.6B | Dia2-2B |
|--------|---------|---------|
| 参数量 | 1.6B | **2B** |
| 流式支持 | 基础 | ✅ 完整流式 |
| 音频条件生成 | - | ✅（--prefix-speaker）|
| CUDA Graph | - | ✅ |
| 最长生成 | 未明确 | **2分钟** |
| GitHub Stars | 6.5k+ | 1.1k（独立仓库）|

### 使用方式
```bash
# 基础生成
dia2 generate "Hello, this is a test." --output output.wav

# 音频条件生成（对话系统）
dia2 generate "What do you think?" \
  --prefix-speaker-1 ref1.wav \
  --prefix-speaker-2 ref2.wav \
  --output output.wav
```

### 适用场景
- 实时语音助手（流式输出，前几个词即可开始）
- 情感对话系统（[S1]/[S2] 双人对话标签）
- AI 陪伴/心理咨询类应用
