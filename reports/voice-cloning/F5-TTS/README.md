# F5-TTS 快速上手

> 版本：最新 | 类型：零样本语音克隆 | 难度：⭐⭐

## 核心优势
- 🚀 2秒极速克隆，业界最快之一
- ⚡ 推理速度最快：生成13秒音频仅需4.1秒（RTX 3090）
- 💾 显存占用低：比CosyVoice更低
- 🆓 完全开源：Apache 2.0许可

## 安装
```bash
git clone https://github.com/SWivid/F5-TTS.git
cd F5-TTS
conda create -n f5tts python=3.10 -y && conda activate f5tts
pip install -r requirements.txt
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download SWivid/F5-TTS --local-dir ckpts/
```

## 推理代码
```python
from f5_tts import load_model, infer
model = load_model("ckpts/F5-TTS")
wav = infer(
    text="今天我们测试F5-TTS克隆效果。",
    ref_audio="ref.wav",
    ref_text="参考音频转写文字"
)
# 保存
import scipy.io.wavfile as wavfile
wavfile.write("output.wav", 24000, wav)
```

## 性能对比
| 模型 | 参考音频 | 生成13秒耗时 | 显存占用 |
|------|----------|-------------|---------|
| **F5-TTS** | 2秒 | **4.1秒** | ~4GB |
| CosyVoice2 | 3秒 | ~20秒 | 4-6GB |
| Qwen3-TTS | 3秒 | ~10秒 | 6-8GB |
