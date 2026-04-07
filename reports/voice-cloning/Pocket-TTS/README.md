# Pocket TTS — CPU即可运行的极速轻量TTS（Kyutai）

> 🤖 免费语音克隆方案Agent | 2026-03-27 新增

---

## 一、模型概览

| 指标 | 数值 |
|------|------|
| **发布时间** | 2026年1月13日 |
| **开发团队** | Kyutai Labs |
| **参数量** | **100M**（1亿） |
| **架构** | 连续潜在空间TTS |
| **推理设备** | **仅CPU**（无需GPU） |
| **CPU性能** | **6倍实时**（MacBook Air M4，仅用2核） |
| **首音频延迟** | **~200ms** |
| **支持语言** | 英语（当前版本） |
| **开源协议** | **MIT** |
| **GitHub** | [kyutai-labs/pocket-tts](https://github.com/kyutai-labs/pocket-tts) |
| **HuggingFace** | [kyutai/pocket-tts](https://huggingface.co/kyutai/pocket-tts) |
| **在线体验** | [kyutai.org/pocket-tts](https://kyutai.org/pocket-tts) |

---

## 二、核心亮点

### ⚡ CPU极速运行
- **无需GPU**，仅用2个CPU核心
- MacBook Air M4 上 **6倍实时**合成
- 首音频延迟仅 **~200ms**

### 🎤 语音克隆
- 使用任意 `.wav` / `.mp3` 文件作为音色提示
- 处理后保存为 `.safetensors`，快速加载复用
- 8个预设音色（alba, marius, javert, jean, fantine等）

### 🌊 流式输出
- 支持音频流式生成
- OpenAI兼容的流式服务器
- 实时对话场景可用

### 🔗 多语言绑定
- **pocket-tts-mlx**：Apple Silicon MLX后端
- **PocketTTS.cpp**：C++单文件运行时
- **sherpa-onnx**：C++/Python/JS/Java多语言绑定
- **ONNX Web**：WebAssembly浏览器运行

---

## 三、适用场景

| 场景 | 适配度 |
|------|--------|
| 无GPU环境（老电脑/服务器） | ⭐⭐⭐⭐⭐ |
| 边缘设备（树莓派/嵌入式） | ⭐⭐⭐⭐⭐ |
| 移动端TTS | ⭐⭐⭐⭐⭐ |
| 浏览器内嵌（WebAssembly） | ⭐⭐⭐⭐ |
| 快速原型/演示 | ⭐⭐⭐⭐ |
| 生产环境大规模部署 | ⭐⭐⭐⭐ |

> ⚠️ 当前版本仅支持英语，中文需等待后续版本。

---

## 四、安装与使用

### 安装

```bash
pip install pocket-tts
```

### CLI快速使用

```bash
# 生成音频
pocket-tts generate "Hello world." -o output.wav

# 启动HTTP服务
pocket-tts serve --port 8000

# OpenAI兼容流式服务
pocket-tts serve --streaming
```

### Python API

```python
from pocket_tts import TTSModel
import scipy.io.wavfile

tts_model = TTSModel.load_model()

# 预设音色
voice_state = tts_model.get_state_for_audio_prompt("alba")
audio = tts_model.generate_audio(voice_state, "Hello world.")
scipy.io.wavfile.write("output.wav", tts_model.sample_rate, audio.numpy())

# 语音克隆：任意音频文件
voice_state2 = tts_model.get_state_for_audio_prompt("my_voice.wav")
audio2 = tts_model.generate_audio(voice_state2, "Cloned voice speaking.")
scipy.io.wavfile.write("cloned.wav", tts_model.sample_rate, audio2.numpy())
```

### 预设音色一览

| 音色ID | 风格 |
|--------|------|
| `alba` | 清亮女声 |
| `marius` | 温暖男声 |
| `javert` | 深沉男声 |
| `jean` | 柔和男声 |
| `fantine` | 甜美女声 |
| `cosette` | 温柔女声 |
| `eponine` | 活泼女声 |
| `azelma` | 年轻女声 |

---

## 五、与主流方案对比

| 方案 | 参数量 | 设备 | CPU速度 | 中文 | 协议 |
|------|--------|------|---------|------|------|
| **Pocket TTS** | 100M | **仅CPU** | **6x实时** | ❌ | **MIT** |
| Kokoro-82M | 82M | CPU/GPU | 快 | ✅ | Apache 2.0 |
| LuxTTS | 小 | 1GB VRAM | 150x实时 | ✅ | Apache 2.0 |
| ChatTTS v2 | ~200M | GPU | 实时 | ✅ | MIT |

---

## 六、常见问题

| 问题 | 解决 |
|------|------|
| 中文支持 | 暂无，等待后续版本 |
| Windows运行 | 建议WSL或Docker方式 |
| 音质不够好 | 轻量模型权衡，英语场景完全可用 |
| 内存占用 | 首次加载约500MB-1GB |

---

## 七、合规使用

禁止：未经同意的声音模仿 / 深度伪造 / 冒充真实录音

---

## 八、相关资源

- [GitHub](https://github.com/kyutai-labs/pocket-tts)
- [HuggingFace](https://huggingface.co/kyutai/pocket-tts)
- [技术报告](https://kyutai.org/blog/2026-01-13-pocket-tts)
- [论文 arXiv](https://arxiv.org/abs/2509.06926)
- [MLX后端](https://github.com/kyutai-labs/pocket-tts-mlx)
- [C++版](https://github.com/nickswaerd/PocketTTS.cpp)
