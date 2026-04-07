# ChatTTS v2 快速上手

> 版本：v2 | 类型：生成式TTS（非克隆）| 难度：⭐（极简单）

---

## 核心定位

ChatTTS **不是** 语音克隆工具，而是对话式语音生成模型。
- ✅ 无需任何参考音频
- ✅ 自然度极高，专为对话场景设计
- ✅ 自动添加笑声、停顿、情感
- ❌ 无法复制特定人声

---

## 安装

```bash
pip install ChatTTS
```

---

## 基础使用

```python
import ChatTTS
import scipy.io.wavfile as wav
import torch
import numpy as np

chat = ChatTTS.Chat()
chat.load()

# 生成语音
wave = chat.generate(
    "今天天气真不错，我们去公园散步吧！顺便可以聊聊最近的学习计划。",
    params_refine_text=ChatTTS.Chat.RefineText(
        Prompt='[oral_2][laugh_0][breath_0]',
        Seed=42  # 固定种子
    ),
    params_infer_code=ChatTTS.Chat.InferCode(
        Speed=5  # 语速 1-9
    )
)

# 保存
audio = wave[0].cpu().numpy()
wav.write("output.wav", 24000, (audio * 32767).astype(np.int16))
```

---

## v2 新特性

| 特性 | v1 | v2 |
|------|----|----|
| 推理延迟 | 一般 | 显著降低 |
| 流式生成 | 支持 | 优化支持 |
| 情感控制 | 基础 | 增强 |
| 多语言 | 中文为主 | 中英均优化 |

---

## 音色控制

```python
# 通过种子固定音色（通过日志找到喜欢的种子号）
ChatTTS.Chat.RefineText(Seed=42)

# 语速调节
ChatTTS.Chat.InferCode(Speed=7)  # 1最慢，9最快

# 情感标记
# [oral_0-9] 口语化程度
# [laugh_0-2] 笑声强度
# [breath_0-3] 呼吸声
```

---

## OpenClaw 集成

```python
import subprocess

def chattts_generate(text, seed=42, speed=5):
    script = "/workspace/voice-cloning/scripts/chattts_infer.py"
    result = subprocess.run(
        ["python", script, text, str(seed), str(speed)],
        capture_output=True, text=True,
        timeout=60
    )
    return result.stdout.strip()
```
