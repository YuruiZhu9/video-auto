# CosyVoice2 快速上手

> 版本：2.0 | 来源：阿里巴巴 FunAudioLLM | 难度：⭐⭐

---

## 核心优势

- 🎯 **3秒极速克隆**：无需微调，3秒音频即可复制音色
- 🌐 **多语言支持**：中/英/日/韩/粤等
- ⚡ **流式推理**：延迟极低，适合实时对话
- 🏢 **阿里背书**：经过大规模生产验证，稳定可靠

---

## 安装

```bash
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice
pip install -r requirements.txt
```

---

## 基础使用

```python
from cosyvoice import CosyVoice

# 加载模型（0.5B版本，显存约4-6GB）
cosyvoice = CosyVoice('CosyVoice2-0.5B')

# === 零样本克隆（3秒参考音频）===
result = cosyvoice.inference_zero_shot(
    text="今天天气真不错，适合出去散步。",
    ref_audio="my_voice.wav",      # 3秒参考音频
    ref_text="这是参考音频的转写文字"   # 可选
)

# === 使用预训练音色 ===
result = cosyvoice.inference_sft(
    text="欢迎收听本期节目。",
    speaker='female_zh'  # female_zh, male_zh, female_en, male_en
)

# === 流式推理（实时场景）===
result = cosyvoice.inference_stream(
    text="这是一段很长的文字，将被流式合成。",
    ref_audio="my_voice.wav"
)
for chunk in result:
    print("收到音频片段:", chunk.shape)
```

---

## Web界面部署

```bash
cd CosyVoice/webui
python app.py
# 访问 http://localhost:50000
```

---

## OpenClaw 集成脚本

```python
#!/usr/bin/env python3
# cosyvoice_infer.py
import sys, os, soundfile as sf
from cosyvoice import CosyVoice

def infer(text, ref_audio=None, speaker='female_zh', output='output.wav'):
    cosyvoice = CosyVoice('CosyVoice2-0.5B')
    
    if ref_audio and os.path.exists(ref_audio):
        result = cosyvoice.inference_zero_shot(text, ref_audio)
    else:
        result = cosyvoice.inference_sft(text, speaker)
    
    sf.write(output, result['speech'], result['sample_rate'])
    return output

if __name__ == "__main__":
    text = sys.argv[1]
    ref = sys.argv[2] if len(sys.argv) > 2 else None
    out = sys.argv[3] if len(sys.argv) > 3 else "output.wav"
    print(infer(text, ref, output=out))
```
