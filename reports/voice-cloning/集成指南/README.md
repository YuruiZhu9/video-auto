# OpenClaw 语音克隆集成指南

> 适用版本：OpenClaw 2.x | 目标助手：小M（钉钉）

---

## 1. 集成架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw 主助手（小M）                   │
│                  接收用户文字/语音请求                        │
└────────────────────────┬────────────────────────────────────┘
                         │ 触发
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   语音克隆子系统                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Qwen3-TTS │  │CosyVoice2 │  │ F5-TTS   │  │ ChatTTS  │  │
│  │(克隆首选)│  │(稳定阿里) │  │(极速推理)│  │(无需克隆)│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │              │        │
│       └──────────────┴──────────────┴──────────────┘        │
│                              │                                │
│                              ▼                                │
│                   ┌──────────────────┐                        │
│                   │  音频文件(.wav)   │                        │
│                   └────────┬─────────┘                        │
└─────────────────────────────┼───────────────────────────────────┘
                              │ TTS发送
                              ▼
                    ┌──────────────────┐
                    │   钉钉消息推送     │
                    │   直接发送音频文件  │
                    └──────────────────┘
```

---

## 2. 目录结构规划

```
/workspace/voice-cloning/
├── models/                  # 模型存储（按需下载）
│   ├── qwen3-tts/
│   ├── cosyvoice2/
│   └── f5-tts/
├── ref-audio/               # 参考音色音频
│   ├── my-voice.wav         # 自己的声音
│   ├── demo-male.wav        # 示例：男声
│   └── demo-female.wav      # 示例：女声
├── results/                  # 生成结果
│   └── [日期]/
├── scripts/                  # 推理脚本
│   ├── qwen3_tts_infer.py
│   ├── cosyvoice_infer.py
│   ├── f5_tts_infer.py
│   └── chattts_infer.py
├── api_server.py             # FastAPI服务（可选）
├── env_setup.sh              # 环境安装脚本
└── README.md
```

---

## 3. 环境一键安装

```bash
#!/bin/bash
# /workspace/voice-cloning/env_setup.sh

set -e

echo "=== 安装语音克隆环境 ==="

# 创建conda环境
conda create -n voice-cloning python=3.10 -y
conda activate voice-cloning

# 安装PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# 安装主要依赖
pip install qwen3-tts
pip install cosyvoice
pip install ChatTTS

# 安装辅助工具
pip install soundfile numpy scipy fastapi uvicorn

# 下载模型（使用HF镜像）
export HF_ENDPOINT=https://hf-mirror.com

echo "=== 安装完成 ==="
echo "激活环境：conda activate voice-cloning"
```

**执行安装：**
```bash
bash /workspace/voice-cloning/env_setup.sh
```

---

## 4. 各方案推理脚本

### 4.1 Qwen3-TTS 推理脚本

```python
#!/usr/bin/env python3
# /workspace/voice-cloning/scripts/qwen3_tts_infer.py

import sys
import os
import soundfile as sf
from qwen3_tts import Qwen3TTS

def tts(text, ref_audio=None, voice_desc=None, output="output.wav"):
    """
    文字转语音
    
    参数:
        text: 要转换的文字
        ref_audio: 参考音频路径（用于克隆）
        voice_desc: 自然语言声音描述
        output: 输出文件路径
    """
    model = Qwen3TTS(
        model_path="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        quantize="int8"
    )
    
    kwargs = {"text": text, "language": "auto"}
    
    if ref_audio and os.path.exists(ref_audio):
        kwargs["ref_audio"] = ref_audio
    elif voice_desc:
        kwargs["voice"] = voice_desc
    
    audio = model.generate(**kwargs)
    sf.write(output, audio, 24000)
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python qwen3_tts_infer.py <文本> [参考音频] [输出路径]")
        sys.exit(1)
    
    text = sys.argv[1]
    ref_audio = sys.argv[2] if len(sys.argv) > 2 else None
    output = sys.argv[3] if len(sys.argv) > 3 else "/workspace/voice-cloning/results/output.wav"
    
    os.makedirs(os.path.dirname(output), exist_ok=True)
    result = tts(text, ref_audio=ref_audio, output=output)
    print(f"音频已生成: {result}")
```

### 4.2 CosyVoice2 推理脚本

```python
#!/usr/bin/env python3
# /workspace/voice-cloning/scripts/cosyvoice_infer.py

import sys
import os
import soundfile as sf
from cosyvoice import CosyVoice

def cosyvoice_tts(text, ref_audio=None, output="output.wav"):
    """
    CosyVoice2 文字转语音
    
    参数:
        text: 要转换的文字
        ref_audio: 参考音频路径（用于克隆，3秒+）
        output: 输出文件路径
    """
    cosyvoice = CosyVoice('CosyVoice2-0.5B')
    
    if ref_audio and os.path.exists(ref_audio):
        # 零样本克隆模式
        result = cosyvoice.inference_zero_shot(
            text,
            ref_audio,
            "对应的参考音频文字（可选，自动识别）"
        )
    else:
        # 预训练音色模式
        result = cosyvoice.inference_sft(
            text,
            'female_zh'  # 可选: female_zh, male_zh, female_en, male_en
        )
    
    sf.write(output, result['speech'], result['sample_rate'])
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python cosyvoice_infer.py <文本> [参考音频] [输出路径]")
        sys.exit(1)
    
    text = sys.argv[1]
    ref_audio = sys.argv[2] if len(sys.argv) > 2 else None
    output = sys.argv[3] if len(sys.argv) > 3 else "/workspace/voice-cloning/results/output.wav"
    
    os.makedirs(os.path.dirname(output), exist_ok=True)
    result = cosyvoice_tts(text, ref_audio=ref_audio, output=output)
    print(f"音频已生成: {result}")
```

### 4.3 ChatTTS 推理脚本

```python
#!/usr/bin/env python3
# /workspace/voice-cloning/scripts/chattts_infer.py

import sys
import os
import torch
import ChatTTS
import numpy as np

def chattts_tts(text, seed=42, speed=5, output="output.wav"):
    """
    ChatTTS v2 文字转语音（无需参考音频）
    
    参数:
        text: 要转换的文字
        seed: 随机种子（固定音色）
        speed: 语速（1-9）
        output: 输出文件路径
    """
    chat = ChatTTS.Chat()
    chat.load()
    
    # 音色参数
    params_refine_text = ChatTTS.Chat.RefineText(
        Prompt='[oral_2][laugh_0][breath_0]',  # 情感控制
        Seed=seed
    )
    params_infer_code = ChatTTS.Chat.InferCode(
        Speed=Speed
    )
    
    # 生成
    wavs = chat.generate(
        text,
        params_refine_text=params_refine_text,
        params_infer_code=params_infer_code,
    )
    
    # 保存
    tensor = wavs[0].cpu()
    audio = tensor.numpy()
    import scipy.io.wavfile as wav
    wav.write(output, 24000, (audio * 32767).astype(np.int16))
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python chattts_infer.py <文本> [种子号] [语速] [输出路径]")
        sys.exit(1)
    
    text = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    speed = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    output = sys.argv[4] if len(sys.argv) > 4 else "/workspace/voice-cloning/results/output.wav"
    
    os.makedirs(os.path.dirname(output), exist_ok=True)
    result = chattts_tts(text, seed=seed, speed=speed, output=output)
    print(f"音频已生成: {result}")
```

---

## 5. OpenClaw Skills 集成

### 5.1 创建语音克隆 Skill

**文件路径：** `/root/.openclaw/skills/voice-cloning/SKILL.md`

```markdown
# Voice Cloning Skill

## 触发条件
当用户提到以下关键词时激活：
- "克隆我的声音"
- "用语音说..."
- "语音合成"
- "生成音频"
- 发送语音相关指令

## 执行流程

1. 解析用户请求（文本内容 + 是否需要克隆）
2. 选择合适的TTS模型
3. 执行推理脚本
4. 返回音频文件路径

## 模型选择逻辑

```
有参考音频？
├─ 是 + 克隆音色 → Qwen3-TTS（首选）或 CosyVoice2
├─ 是 + 快速生成 → F5-TTS
└─ 否 + 对话场景 → ChatTTS v2
```

## 脚本调用方式

```bash
conda activate voice-cloning

# Qwen3-TTS（克隆）
python /workspace/voice-cloning/scripts/qwen3_tts_infer.py \
  "要转换的文字" \
  "/workspace/voice-cloning/ref-audio/my-voice.wav" \
  "/workspace/voice-cloning/results/output.wav"

# ChatTTS（无需克隆）
python /workspace/voice-cloning/scripts/chattts_infer.py \
  "要转换的文字" \
  42 \  # 种子号
  5     # 语速
```

## 注意事项
- 首次运行需下载模型，请耐心等待
- 显存不足时使用 int8 量化版本
- 中文文本预处理：统一标点，去除特殊字符
```

### 5.2 OpenClaw Agent 调用示例

```python
# 在 OpenClaw agent 中调用语音克隆
async def generate_voice_message(text, voice_type="clone"):
    """
    生成语音消息
    
    参数:
        text: 要转换的文字
        voice_type: "clone"（克隆）或 "chat"（ChatTTS）
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/workspace/voice-cloning/results/{timestamp}.wav"
    
    if voice_type == "clone":
        ref_audio = "/workspace/voice-cloning/ref-audio/my-voice.wav"
        script = "/workspace/voice-cloning/scripts/qwen3_tts_infer.py"
        cmd = f"conda run -n voice-cloning python {script} '{text}' {ref_audio} {output_path}"
    else:
        script = "/workspace/voice-cloning/scripts/chattts_infer.py"
        cmd = f"conda run -n voice-cloning python {script} '{text}' 42 5 {output_path}"
    
    result = await exec(cmd, timeout=120)
    
    if result.success:
        return output_path
    else:
        raise Exception(f"语音生成失败: {result.stderr}")
```

---

## 6. 钉钉消息发送（message tool）

```python
# 发送语音消息到钉钉
import asyncio
from message import message

async def send_voice_to_dingtalk(audio_path, chat_id):
    """发送音频文件到钉钉"""
    
    # 使用 message 工具发送
    await message(
        action="send",
        channel="dingtalk",
        target=chat_id,
        media=audio_path,  # 本地音频文件路径
        caption="这是您请求的语音消息",
    )
    return True

# 调用
asyncio.run(send_voice_to_dingtalk(
    "/workspace/voice-cloning/results/output.wav",
    "03003745585526383319"  # 用户chat_id
))
```

---

## 7. 完整工作流示例

```
用户发送："请用我的声音朗读这段文字：今天天气真好"

1. OpenClaw 接收消息
       ↓
2. Skill 检测到关键词"克隆我的声音"
       ↓
3. 提取文本："今天天气真好"
       ↓
4. 调用 Qwen3-TTS 推理脚本
   conda activate voice-cloning
   python scripts/qwen3_tts_infer.py \
     "今天天气真好" \
     "ref-audio/my-voice.wav" \
     "results/20260324_193900.wav"
       ↓
5. 等待生成完成（约5-15秒）
       ↓
6. 发送音频到钉钉
   message(action=send, channel=dingtalk, target=user_chat_id, media=audio_path)
       ↓
7. 用户收到语音消息 ✓
```

---

## 8. 性能优化建议

| 优化项 | 方法 | 效果 |
|--------|------|------|
| **首次加载慢** | 预先加载模型到显存 | 节省5-10秒/次 |
| **显存不足** | 使用INT8量化 | 显存减半 |
| **频繁调用** | 启动API服务 | 支持并发 |
| **长文本** | 分段生成后拼接 | 避免OOM |
| **离线运行** | 下载完整模型到本地 | 无需网络 |

---

## 9. 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'qwen3_tts'` | 未激活conda环境 | `conda activate voice-cloning` |
| `CUDA out of memory` | 显存不足 | 使用 `--quantize int8` 或减小batch |
| `Failed to download model` | 网络问题/HF访问限制 | 设置 `HF_ENDPOINT=https://hf-mirror.com` |
| 生成的音频有杂音 | 采样率不匹配 | 使用 `soundfile` 重采样到16kHz |
| 音色不自然 | 参考音频质量差 | 更换高质量参考音频 |
| 推理卡住 | 模型加载失败 | 检查GPU驱动和CUDA版本 |
