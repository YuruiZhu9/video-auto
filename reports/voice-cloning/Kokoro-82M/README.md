# Kokoro-82M — 极致轻量高性能TTS（82M参数）

> 🤖 免费语音克隆方案Agent | 2026-03-27 新增

---

## 一、模型概览

| 指标 | 数值 |
|------|------|
| **发布时间** | 持续更新，v1.0/v1.1 |
| **参数量** | **82M**（8200万） |
| **模型大小** | **~165MB** |
| **输出采样率** | 24kHz |
| **克隆方式** | 预设音色 + 自定义音色（.pt） |
| **推理设备** | **CPU / GPU**（均支持） |
| **ONNX优化** | ✅，可在CPU高效推理 |
| **开源协议** | **Apache 2.0** |
| **GitHub** | [hexgrad/kokoro](https://github.com/hexgrad/kokoro) |
| **HuggingFace** | [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) |

---

## 二、核心亮点

### ⚡ 极致轻量
- 仅 **82M参数**，模型大小 ~165MB
- 可在 **CPU上高效运行**（ONNX优化）
- 适合树莓派、嵌入式等低功耗设备

### 🎤 内置多音色
- 8种预设英文音色（af_heart等）
- 8种中文音色（zf_xiaobei / zm_yunxi等）
- 支持加载自定义音色（.pt张量文件）

### 🌐 多语言支持
| 代码 | 语言 |
|------|------|
| a | 美国英语 |
| b | 英式英语 |
| e | 西班牙语 |
| f | 法语 |
| h | 印地语 |
| i | 意大利语 |
| j | 日语 |
| p | 巴西葡萄牙语 |
| **z** | **普通话中文** |

### 💯 开源免费商用
- **Apache 2.0** 协议
- 零成本，任意场景可用

---

## 三、中文音色一览

| 音色 ID | 性别 | 风格 | 推荐场景 |
|---------|------|------|----------|
| `zf_xiaobei` | 女声 | 温柔甜美 | 有声书、客服 |
| `zf_xiaoni` | 女声 | 清亮活泼 | 短视频配音 |
| `zf_xiaoxiao` | 女声 | 成熟稳重 | 新闻播报 |
| `zf_xiaoyi` | 女声 | 专业正式 | 教程讲解 |
| `zm_yunjian` | 男声 | 青春活力 | 游戏角色 |
| `zm_yunxi` | 男声 | 温柔细腻 | 有声小说 |
| `zm_yunxia` | 男声 | 成熟稳重 | 企业宣传 |
| `zm_yunyang` | 男声 | 浑厚有力 | 纪录片旁白 |

---

## 四、适用场景

| 场景 | 适配度 |
|------|--------|
| 低配置环境部署 | ⭐⭐⭐⭐⭐ |
| CPU优先场景 | ⭐⭐⭐⭐⭐ |
| 快速轻量TTS | ⭐⭐⭐⭐⭐ |
| 有声书/短视频配音 | ⭐⭐⭐⭐ |
| 多语言应用 | ⭐⭐⭐⭐ |
| 生产环境大规模部署 | ⭐⭐⭐⭐ |

---

## 五、安装与使用

### 基本安装

```bash
pip install kokoro>=0.9.4 soundfile
```

### 中文语音库安装（必需）

```bash
pip install misaki[zh]
```

### Linux额外依赖

```bash
apt-get install espeak-ng
```

### Docker快速部署

```bash
# 一键部署脚本
bash <(curl -fsSL https://raw.githubusercontent.com/chenjim/tts-hexgrad-kokoro/main/deploy.sh)
```

### 中文推理示例

```python
from kokoro import KPipeline

# 初始化中文pipeline
pipeline = KPipeline(lang_code='z')

# 生成语音
text = "今天天气真好，适合出去散步。"
generator = pipeline(text, voice='zf_xiaobei', speed=1, split_pattern=r'\n+')

for i, (gs, ps, audio) in enumerate(generator):
    import soundfile as sf
    sf.write(f'output_{i}.wav', audio, 24000)
    print(f"已保存: output_{i}.wav")
```

### HTTP服务部署

```python
# 保存为 server.py
from kokoro import KPipeline
from fastapi import FastAPI
import soundfile as sf
import io

app = FastAPI()
pipeline = KPipeline(lang_code='z')

@app.post("/tts")
async def tts(text: str, voice: str = "zf_xiaobei", speed: float = 1.0):
    generator = pipeline(text, voice=voice, speed=speed)
    audio_chunks = []
    for _, _, audio in generator:
        audio_chunks.append(audio)
    audio = sum(audio_chunks) if len(audio_chunks) > 1 else audio_chunks[0]
    
    buffer = io.BytesIO()
    sf.write(buffer, audio, 24000, format='WAV')
    return {"audio": buffer.getvalue().hex()}

# uvicorn server:app --host 0.0.0.0 --port 8000
```

### ONNX CPU高效推理

```bash
# 下载ONNX优化版本
huggingface-cli download hexgrad/Kokoro-82M-v1.1-ONNX --local-dir ./kokoro-onnx

# 使用ONNX runtime
python kokoro_onnx_infer.py --text "你好世界" --voice zf_xiaobei
```

---

## 六、与主流方案对比

| 方案 | 参数量 | 模型大小 | 中文支持 | 速度 | CPU支持 |
|------|--------|----------|----------|------|---------|
| **Kokoro-82M** | **82M** | **165MB** | ✅ 8音色 | 快 | ✅ |
| ChatTTS v2 | ~200M | 较大 | ✅ | 快 | ❌需GPU |
| CosyVoice 2 | ~500M | 较大 | ✅ | 实时 | ⚠️ |
| Qwen3-TTS | 600M/1.7B | 大 | ✅ | 实时 | ❌需GPU |
| MOSS-TTS | ~1B | 大 | ✅ | 实时 | ❌需GPU |

**结论**：Kokoro-82M是体积最小的方案，CPU可直接运行，适合资源受限或不想配置GPU的环境。

---

## 七、常见问题

| 问题 | 解决 |
|------|------|
| Mac M系列GPU加速 | `PYTORCH_ENABLE_MPS_FALLBACK=1` |
| 中文语音无法生成 | 确认安装了`misaki[zh]`，lang_code设为`z` |
| 音质不满意 | 尝试不同音色，中文推荐`zf_xiaobei`（温柔）或`zm_yunxi`（男声） |
| Windows安装 | 下载espeak-ng.msi安装器，地址：[github.com/espeak-ng/espeak-ng/releases](https://github.com/espeak-ng/espeak-ng/releases) |
| Docker部署 | 参考 [gitee.com/chenjim/tts-hexgrad-kokoro](https://gitee.com/chenjim/tts-hexgrad-kokoro) |

---

## 八、开源协议

**Apache 2.0** — 完全免费商用，权重可自由使用。

---

## 九、相关资源

- [GitHub仓库](https://github.com/hexgrad/kokoro)
- [中文模型v1.1](https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh)
- [ONNX版本](https://ai.gitcode.com/hf_mirrors/onnx-community/Kokoro-82M-v1.0-ONNX)
- [博客园部署指南](https://www.cnblogs.com/oddmeta/p/19776272)
- [Docker部署方案](https://www.h89.cn/archives/528.html)
