# OpenClaw 语音克隆集成指南

> 更新：2026-03-23 | 适用模型：CosyVoice / OpenVoice / ChatTTS / RVC

---

## 一、集成架构总览

```
用户输入 ──→ OpenClaw Agent ──→ 选定 TTS/VC 引擎
    │                               │
    │       ┌───────────────────────┼────────┐
    │       ▼                       ▼        ▼
    │   CosyVoice 3.0        OpenVoice   ChatTTS
    │   (推荐首选)            (即时克隆)   (对话情感)
    │       │                    │        │
    │       └── 可选：RVC 变声 ──┘        │
    │               │                   │
    │               ↓                   │
    │         输出 WAV/MP3               │
    │               │                   │
    └───────────────┴──→ 通过消息通道发送音频
```

---

## 二、Skill 目录结构

```
/root/.openclaw/skills/voice-clone/
├── SKILL.md              ← 技能描述
├── scripts/
│   ├── cosyvoice_infer.py
│   ├── openvoice_infer.py
│   └── chattts_infer.py
```

---

## 三、完整集成代码

### CosyVoice 集成（推荐首选）

```python
# cosyvoice_infer.py
import os, sys, tempfile
from cosyvoice import CosyVoice

_model = None

def init_model():
    global _model
    if _model is None:
        print("[CosyVoice] Loading model...")
        _model = CosyVoice('CosyVoice-300M-Instruct')
        print("[CosyVoice] Model loaded!")
    return _model

def generate(text, reference_audio=None, instruction="", output_path=None,
             use_sft=False, speaker="中文女声") -> str:
    model = init_model()
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".wav")
    if use_sft:
        result = model.sft(text=text, speaker=speaker)
    else:
        assert reference_audio, "需要提供参考音频"
        result = model.instruct(text=text, reference_audio=reference_audio,
                                 instruction=instruction)
    with open(output_path, "wb") as f:
        f.write(result['audio'])
    print(f"[CosyVoice] Audio saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    text = sys.argv[1]
    ref = sys.argv[sys.argv.index("--ref")+1] if "--ref" in sys.argv else None
    inst = sys.argv[sys.argv.index("--inst")+1] if "--inst" in sys.argv else ""
    use_sft = "--sft" in sys.argv
    speaker = sys.argv[sys.argv.index("--speaker")+1] if "--speaker" in sys.argv else "中文女声"
    output = generate(text, ref, inst, use_sft=use_sft, speaker=speaker)
    print(f"Output: {output}")
```

### ChatTTS 集成（无需音色）

```python
# chattts_infer.py
import sys, tempfile, ChatTTS

_model = None

def init_model():
    global _model
    if _model is None:
        _model = ChatTTS.Chat()
        _model.load()
    return _model

def generate(text, output_path=None, lang="zh") -> str:
    model = init_model()
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".wav")
    wavs = model.chat(text, lang=lang)
    model.save_wav(output_path, wavs)
    print(f"[ChatTTS] Audio saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    text = sys.argv[1]
    result = generate(text)
    print(f"Output: {result}")
```

---

## 四、Agent 调用示例

```python
import subprocess

def tts_clone(text, reference_audio=None, instruction=""):
    """在 OpenClaw Agent 中调用 TTS"""
    if reference_audio:
        cmd = ["python", "/path/to/cosyvoice_infer.py", text,
               "--ref", reference_audio]
        if instruction:
            cmd.extend(["--inst", instruction])
    else:
        cmd = ["python", "/path/to/chattts_infer.py", text]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"TTS failed: {result.stderr}")
    return result.stdout.strip().split("\n")[-1]

# 使用示例：
# audio_path = tts_clone("你好，今天天气真不错！", reference_audio="user.wav")
# message.send_audio(channel="dingtalk", target=user_id, audio_path=audio_path)
```

---

## 五、推荐集成方案

```
最佳性价比组合：

  CosyVoice 3.0（默认引擎）
      ├── 参考音频 + 零样本克隆（3秒极速）
      ├── 预训练音色 SFT（无需录音）
      └── 情感指令控制

  ChatTTS（对话情感备选）
      └── 长对话场景（无需音色，情感预测最强）

  RVC（音色后处理）
      └── 对音色相似度要求极高时

  OpenVoice（跨语言克隆）
      └── 跨语言配音场景
```

**一键启动推荐**：CosyVoice 3.0 作为默认引擎，覆盖 95% 使用场景。
