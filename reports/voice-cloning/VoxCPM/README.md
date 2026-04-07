# VoxCPM 1.5 — 开源语音克隆技术报告

> 🤖 免费语音克隆方案Agent | 2026-03-27
> 模型来源：[OpenBMB/VoxCPM](https://github.com/OpenBMB/VoxCPM) | Apache 2.0

---

## 一、模型概述

VoxCPM 1.5 是 **OpenBMB（面壁智能）** 于 **2025年12月5日** 开源发布的端到端语音克隆 TTS 系统，基于 **MiniCPM-4** 大模型骨干，采用创新的 **LocDiT 扩散自回归架构**，无需离散 Tokenizer，直接从文本生成连续语音表征，突破了传统两阶段（TTS tokenizer + LM）范式的质量瓶颈。

**核心技术路线：** Diffusion Autoregressive（扩散自回归） + AudioVAE（音频变分自编码器）

**版本演进：**

| 版本 | 发布时间 | 参数量 | 音频采样率 | 核心特点 |
|------|----------|--------|-----------|---------|
| VoxCPM-0.5B | 2025-09-16 | 500M | 16kHz | 首个版本，验证路线 |
| **VoxCPM 1.5** 🆕 | **2025-12-05** | **800M** | **44.1kHz** | 质量飞跃，高保真，完整开源 |

---

## 二、核心优势

### 🏆 技术亮点

1. **Token-Free 架构（业界首创）**
   - 传统 TTS 需要：文本 → Tokenizer → LM → Decoder → Vocoder → 音频
   - VoxCPM：文本 → LocDiT 扩散 → AudioVAE 解码 → 音频
   - 端到端连续表征生成，避免离散 token 的量化误差，保留更多声学细节

2. **44.1kHz 高保真音频输出**
   - 44.1kHz = CD 级音质（所有开源 TTS 中最高采样率）
   - 对比：CosyVoice 3.0（24kHz）、Qwen3-TTS（24kHz）、GPT-SoVITS V4（48kHz）
   - 适合：音乐、人声、高保真配音、有声书

3. **Context-Aware 韵律生成**
   - 深度理解文本语义，自动推断情感、语调、重音
   - 不是简单拼接，而是真正的语义驱动韵律

4. **True-to-Life 零样本克隆**
   - 仅需 10-30 秒参考音频，即可克隆音色、口音、情感色彩
   - Captures: 音色(timbre) + 口音(accent) + 情感(emotion) + 节奏(rhythm) + 语速(pacing)

5. **LoRA 微调支持**
   - 支持全参数微调和 LoRA 高效微调
   - 低成本定制专属音色

### 📊 性能指标

| 指标 | 数值 |
|------|------|
| 参数量 | 800M |
| 音频采样率 | **44.1kHz**（全场最高） |
| RTX 4090 推理 RTF | **0.15**（即 6.67x 实时） |
| 流式推理 RTF | ~0.17 |
| 支持语言 | 中文 + 英文（双语） |
| 许可证 | **Apache 2.0**（完全免费商用） |

---

## 三、与其他主流方案对比

| 维度 | VoxCPM 1.5 🆕 | Qwen3-TTS | CosyVoice 3.0 | Higgs Audio V2 | LuxTTS |
|------|--------------|-----------|--------------|----------------|--------|
| 参数量 | 800M | 1.7B | 0.5B | 3B（压缩1B） | 未公开 |
| 音频采样率 | **44.1kHz** 🏆 | 24kHz | 24kHz | 24kHz | 48kHz |
| 架构 | LocDiT扩散 | 自回归 | 自回归 | 自回归+Diffusion | 扩散 |
| RTX 4090 RTF | **0.15** | ~0.1 | ~0.2 | ~0.2 | ~0.007 |
| 中文克隆 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 英文克隆 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 方言支持 | ❌ | 多语言 | 18+方言 | ❌ | ❌ |
| LoRA微调 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 流式推理 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 商业授权 | **Apache 2.0** | Apache 2.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 |

---

## 四、安装与使用

### 环境要求

- **Python：** 3.8+
- **GPU：** NVIDIA RTX 3090/4090（推荐），最小 6GB 显存
- **CUDA：** 11.8+ / 12.x
- **磁盘：** 模型约 3-4GB

### 安装（pip 一键）

```bash
pip install voxcpm
```

### 推理（Python API）

#### 零样本克隆

```python
import soundfile as sf
from voxcpm import VoxCPM

# 加载模型（自动从 HuggingFace 下载）
model = VoxCPM.from_pretrained("openbmb/VoxCPM1.5")

# ========== 模式1：文本直接合成（无克隆）==========
wav = model.generate(
    text="VoxCPM 是端到端语音合成的创新模型。",
    prompt_wav_path=None,
    prompt_text=None,
    cfg_value=2.0,
    inference_timesteps=10,
)
sf.write("output.wav", wav, model.tts_model.sample_rate)

# ========== 模式2：语音克隆 ===========
wav = model.generate(
    text="欢迎体验 VoxCPM 的语音克隆功能。",
    prompt_wav_path="ref_voice.wav",     # 参考音频（10-30秒）
    prompt_text="这是参考音频的文字内容", # 参考音频对应文本
    cfg_value=2.0,                        # LM引导强度（1.5-3.0）
    inference_timesteps=10,               # 扩散步数（越多越慢，质量越高）
)
sf.write("cloned.wav", wav, model.tts_model.sample_rate)
```

#### 流式推理

```python
import soundfile as sf
import numpy as np
from voxcpm import VoxCPM

model = VoxCPM.from_pretrained("openbmb/VoxCPM1.5")

# 流式生成（适合实时场景）
chunks = []
for chunk in model.generate_streaming(text="这是一个流式语音合成示例。"):
    chunks.append(chunk)

wav = np.concatenate(chunks)
sf.write("streaming_output.wav", wav, model.tts_model.sample_rate)
print(f"采样率: {model.tts_model.sample_rate} Hz")
```

#### 参数调优建议

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `cfg_value` | LocDiT 上的 LM 引导强度 | 2.0（默认），调高增强文本一致性 |
| `inference_timesteps` | 扩散推理步数 | 10（默认），调高提升质量（推荐 10-20） |
| `normalize` | 是否启用外部 TN 工具 | False（默认） |
| `denoise` | 是否启用外部去噪 | False（默认） |
| `retry_badcase` | 失败重试模式 | True（推荐开启） |

### CLI 命令行使用

```bash
# 直接合成（无克隆）
voxcpm --text "你好，这是 VoxCPM 语音合成。" --output output.wav

# 带克隆
voxcpm --text "欢迎体验语音克隆。" \
  --prompt-audio ref_voice.wav \
  --prompt-text "参考音频对应的文字内容" \
  --output cloned.wav

# 批量处理
voxcpm --input examples/input.txt --output-dir outs

# 克隆 + 批量
voxcpm --input examples/input.txt \
  --prompt-audio ref_voice.wav \
  --prompt-text "参考音频文字" \
  --output-dir outs
```

### Web Demo 启动

```bash
# 自动下载依赖模型（ZipEnhancer + SenseVoice）
python app.py
# 访问 http://localhost:7860
```

---

## 五、参考音频准备规范

### 音频要求

| 要求项 | 规格 |
|--------|------|
| **格式** | WAV / MP3 |
| **采样率** | 16kHz 以上（模型内会重采样到 44.1kHz 输出） |
| **时长** | 10-30 秒（推荐） |
| **声道** | 单声道 |
| **内容** | 清晰普通话或英语，覆盖多种句式 |
| **环境** | 安静、无混响、无背景音乐 |
| **文字标注** | 必须提供对应的文本转写 |

### 录音文本示例（中文普通话）

```
今天天气真不错，阳光明媚，适合出门散步。
人工智能技术正在改变我们的生活方式。
这个新产品非常好用，我已经推荐给朋友了。
小明在图书馆看书，妈妈在厨房做饭。
那座古老的桥跨越了整条河流。
```

### 预处理（如参考音频采样率不匹配）

```python
import soundfile as sf

# 重采样到 16kHz（输入给 VoxCPM）
audio, sr = sf.read("input.wav")
if sr != 16000:
    import librosa
    audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    sf.write("input_16k.wav", audio, 16000)
```

---

## 六、微调训练

VoxCPM 支持两种微调方式，适配不同硬件条件：

### 方式一：全参数微调（效果最好，需要资源多）

```bash
python scripts/train_voxcpm_finetune.py \
    --config_path conf/voxcpm_v1.5/voxcpm_finetune_all.yaml
```

### 方式二：LoRA 高效微调（推荐，资源友好）

```bash
python scripts/train_voxcpm_finetune.py \
    --config_path conf/voxcpm_v1.5/voxcpm_finetune_lora.yaml
```

**LoRA 配置说明：**
- 参数量减少 ~80%，显存需求降低约 60%
- 训练数据：10-30 分钟高质量音频即可获得良好效果
- 训练硬件：RTX 3090 可完成 LoRA 微调

---

## 七、社区生态（亮点）

VoxCPM 拥有活跃的开源社区，提供多种部署方案：

| 项目 | 说明 | 适用场景 |
|------|------|----------|
| **ComfyUI-VoxCPM** | ComfyUI 插件，图形化工作流 | 设计师、内容创作者 |
| **VoxCPM-NanoVLLM** | NanoVLLM 加速推理 | 高吞吐生产环境 |
| **VoxCPM-ONNX** | ONNX 导出，CPU 推理 | 边缘设备、无 GPU 环境 |
| **VoxCPMANE** | Apple Neural Engine 后端 | iOS/macOS 端侧部署 |
| **voxcpm_rs** | Rust 重实现 | 高性能嵌入式系统 |

---

## 八、与 OpenClaw Skills 集成

### 集成方案

VoxCPM 可通过 Python 脚本 + OpenClaw exec 工具集成到工作流：

#### 步骤1：创建推理脚本

```python
#!/usr/bin/env python3
"""vox_cpm_infer.py - VoxCPM 语音克隆推理脚本"""
import argparse
import soundfile as sf
from voxcpm import VoxCPM
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True, help="待合成文本")
    parser.add_argument("--ref_audio", type=str, default=None, help="参考音频路径")
    parser.add_argument("--ref_text", type=str, default=None, help="参考音频对应文字")
    parser.add_argument("--output", type=str, default="output.wav", help="输出路径")
    parser.add_argument("--cfg", type=float, default=2.0, help="CFG 引导强度")
    parser.add_argument("--steps", type=int, default=10, help="推理步数")
    args = parser.parse_args()

    print(f"加载模型 openbmb/VoxCPM1.5 ...")
    model = VoxCPM.from_pretrained("openbmb/VoxCPM1.5")

    print(f"合成文本: {args.text}")
    wav = model.generate(
        text=args.text,
        prompt_wav_path=args.ref_audio,
        prompt_text=args.ref_text,
        cfg_value=args.cfg,
        inference_timesteps=args.steps,
    )

    sf.write(args.output, wav, model.tts_model.sample_rate)
    print(f"✅ 已保存到 {args.output}")

if __name__ == "__main__":
    main()
```

#### 步骤2：OpenClaw 调用

```python
# OpenClaw exec 调用
result = exec("""
cd /workspace && python vox_cpm_infer.py \
    --text "欢迎使用语音克隆功能。" \
    --ref_audio /workspace/voice-cloning/ref-audio/my_voice.wav \
    --ref_text "这是一段参考音频的文字。" \
    --output /workspace/voice-cloning/outputs/result.wav \
    --steps 10
""")
```

#### 步骤3：注册为 Skill（可选）

在 `/root/.openclaw/skills/` 下创建 `vox-cpm/SKILL.md`，实现标准化调用。

---

## 九、常见问题

| 问题 | 解决方案 |
|------|----------|
| 推理速度慢 | 降低 `inference_timesteps` 至 8；使用 NanoVLLM 加速 |
| 克隆音色不稳定 | 确保参考音频质量（安静、清晰）；增加 `cfg_value` 至 2.5 |
| 中文发音错误 | 使用高质量中文参考音频；参考音频语言与目标语言一致 |
| 显存不足（OOM） | 减小 batch；使用 `dtype=float16`；流式推理 |
| 生成音频有噪声 | 开启 `denoise=True`；检查参考音频质量 |
| 情感表达不足 | 选用情感丰富的参考音频；增加 `inference_timesteps` |

---

## 十、适用场景

✅ **推荐场景：**
- 高保真配音（44.1kHz，CD 级音质）
- 有声书制作（音色自然，节奏可控）
- 音乐/人声合成（最高采样率）
- 中文 + 英文双语项目（原生双语支持）
- LoRA 定制音色（品牌 IP、虚拟主播）
- 企业级生产部署（Apache 2.0，RTF 0.15 速度快）

⚠️ **注意场景：**
- 多方言需求 → 优先选 CosyVoice 3.0（18+方言）
- 极低显存（<4GB）→ 优先选 LuxTTS（1GB）或 Kokoro-82M（0.5GB）
- 非中英语言 → 优先选 Qwen3-TTS（10语言）或 Fish Audio S2 Pro（80+语言）

---

## 十一、资源链接

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/OpenBMB/VoxCPM |
| HuggingFace | https://huggingface.co/openbmb/VoxCPM1.5 |
| ModelScope | https://modelscope.cn/models/OpenBMB/VoxCPM1.5 |
| 在线 Demo | https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo |
| 技术报告 | https://arxiv.org/abs/2509.24650 |

---

*本报告由免费语音克隆方案Agent自动生成*
*收录版本：VoxCPM 1.5（2025-12-05，Apache 2.0）*
