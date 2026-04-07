# 技术教程类 - 本地 Whisper + Ollama 完整配置方案

> 🤖 维护：视频解析方法总结Agent  
> 📅 新增日期：2026-03-29  
> 🔗 来源：Ollama 官方 / Whisper 官方 / OpenClaw Skills

---

## 核心工具/API

| 工具 | 类型 | 能力描述 |
|------|------|---------|
| **Ollama** | 本地 LLM 运行时 | 支持 Qwen2.5、Llama3、Mistral 等模型，本地免费运行 |
| **Whisper** (OpenAI) | 本地语音识别 | 音频转文字，支持 99 种语言 |
| **Faster-Whisper** | Whisper 加速版 | 比原生快 4~5 倍，支持 GPU |
| **WhisperX** | Whisper 增强版 | 带词级时间戳 + 说话人分离 |
| **FFmpeg** | 音视频处理 | 音频提取、格式转换 |
| **OpenClaw Skill** | 本地工具封装 | `openai-whisper` / `openai-whisper-api` / `sag`（TTS）|

---

## 核心优势

```
完全本地运行 = 零 API 费用 + 隐私安全 + 离线可用
```

| 对比维度 | 纯 API 方案 | 本地 Ollama + Whisper |
|---------|-----------|----------------------|
| **费用** | 按调用量付费 | 完全免费（硬件成本） |
| **隐私** | 数据上传云端 | 所有数据留在本地 |
| **速度** | 依赖网络延迟 | 本地推理（GPU 加速） |
| **离线** | ❌ 不可用 | ✅ 完全可用 |
| **批量** | 费用累积 | ✅ 无额外成本 |
| **中文优化** | 取决于模型 | ✅ 可选优质中文模型 |

---

## 步骤流程

### 1. 安装 Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows：下载安装包 https://ollama.com/download

# 验证安装
ollama --version
```

### 2. 下载视频理解模型

```bash
# 中文优化模型（推荐）
ollama pull qwen2.5:7b          # 约 4.4 GB，中文理解好
ollama pull qwen2.5:14b         # 约 9.0 GB，中文理解更好

# 英文为主模型
ollama pull llama3.2:3b         # 约 2.0 GB
ollama pull mistral:7b          # 约 4.1 GB

# 多模态视频理解模型（如果有 GPU）
ollama pull llava:7b             # 支持图片理解（可用于帧分析）
```

### 3. 安装 Whisper 及其加速版

```bash
# 基础版（pip）
pip install openai-whisper

# 加速版（推荐，GPU 用户）
pip install faster-whisper

# 增强版（带时间戳 + 说话人分离）
pip install whisperx

# C++ 版（无需 Python，完全本地）
brew install whisper        # macOS
# 或
git clone https://github.com/ggml-org/whisper.cpp
cd whisper.cpp && mkdir build && cd build && cmake .. && make
```

### 4. 完整本地视频解析 Pipeline

```python
import subprocess
import json
from faster_whisper import WhisperModel
import requests

# ========== 阶段1：下载视频 ==========
def download_video(url, output_path="/tmp/input.mp4"):
    subprocess.run([
        "yt-dlp", "-f", "best[ext=mp4]",
        "-o", output_path, url, "--no-playlist"
    ], check=True)
    return output_path

# ========== 阶段2：提取音频 ==========
def extract_audio(video_path, audio_path="/tmp/audio.wav"):
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path, "-y"
    ], check=True, capture_output=True)
    return audio_path

# ========== 阶段3：Whisper 转录 ==========
def transcribe(audio_path, output_path="/tmp/transcript.txt"):
    # 使用 Faster-Whisper（GPU 加速）
    model = WhisperModel("medium", device="cuda", compute_type="float16")
    
    segments, info = model.transcribe(
        audio_path,
        language="zh",
        beam_size=5,
        word_timestamps=True
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            start = format_time(seg.start)
            end = format_time(seg.end)
            f.write(f"[{start} - {end}] {seg.text}\n")
    
    return output_path

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ========== 阶段4：Ollama LLM 分析 ==========
def analyze_with_ollama(transcript_path, video_path):
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    prompt = f"""你是一个专业技术教程分析师。请根据以下视频文字稿，分析视频内容并输出结构化报告：

文字稿：
{transcript[:8000]}

请输出：
1. 【视频主题】一句话概括
2. 【关键步骤】按时间顺序列出操作步骤
3. 【代码示例】提取出现的所有代码片段
4. 【知识点总结】3-5个核心知识点
5. 【学习建议】给观众的建议
"""
    
    # 调用本地 Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False
        }
    )
    result = response.json()
    return result["response"]

# ========== 主程序 ==========
if __name__ == "__main__":
    import sys
    video_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com/video.mp4"
    
    print("📥 下载视频中...")
    video = download_video(video_url)
    
    print("🎙️ 提取音频中...")
    audio = extract_audio(video)
    
    print("📝 转录中（Whisper medium）...")
    transcript = transcribe(audio)
    
    print("🧠 LLM 分析中（Ollama qwen2.5:7b）...")
    report = analyze_with_ollama(transcript, video)
    
    print("\n" + "="*60)
    print("📊 分析报告：")
    print(report)
```

---

## 适用场景

- **隐私敏感视频**：医疗、法律、金融内部培训视频
- **批量转录需求**：需要处理大量视频，API 成本高
- **离线工作环境**：无网络或网络受限的服务器环境
- **中文技术教程**：Qwen2.5 中文理解优秀，成本为零
- **研究与实验**：需要反复调试视频解析流程

---

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| Ollama 模型下载慢 | 使用镜像：`export OLLAMA_HOST=https://ollama.npsv.cn` |
| Whisper 显存不足 | 使用 `int8` 量化：`compute_type="int8"`；或用 CPU：`device="cpu"` |
| 中文转录不准 | 使用 `large-v3` 模型 + `language="zh"`；加 prompt 提示词 |
| Ollama 响应慢 | 使用 7B 模型而非 14B；确保 GPU 显存充足 |
| 音频格式不支持 | 先转码：`ffmpeg -i input.mp4 -vn -acodec pcm_s16le audio.wav` |
| Whisper 幻觉（空音频段造假）| 使用 `--vad-filter true` 过滤静音；或用 WhisperX |

---

## 硬件配置建议

| 硬件 | 可用模型 | 说明 |
|------|----------|------|
| **无 GPU（CPU）** | Whisper tiny/base；Qwen2.5:1.8b | 速度慢，但可运行 |
| **6GB GPU** | Whisper medium (int8)；Qwen2.5:7b (int4) | 日常使用 |
| **12GB GPU** | Whisper medium (float16)；Qwen2.5:14b (int4) | 高质量转录+分析 |
| **24GB+ GPU** | Whisper large-v3；Qwen2.5:14b (float16) | 最佳质量 |

---

## 与 OpenClaw 的集成

```bash
# 在 OpenClaw 中调用本地 Ollama
# 在 openclaw.json 中配置：
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "models": [
          // 本地 Faster-Whisper
          {
            "type": "cli",
            "command": "python",
            "args": ["-c", 
              "from faster_whisper import WhisperModel;",
              "model = WhisperModel('medium', device='cuda', compute_type='float16');",
              "segments, _ = model.transcribe('{{MediaPath}}', language='zh');",
              "[print(f'{s.start:.2f}-{s.end:.2f}: {s.text}') for s in segments]"
            ]
          }
        ]
      }
    }
  }
}
```

---

## 参考链接

- Ollama 官网：https://ollama.com/
- Ollama 模型库：https://ollama.com/library
- Faster-Whisper：https://github.com/guillaumekln/faster-whisper
- WhisperX：https://github.com/m-bain/whisperX
- Whisper.cpp：https://github.com/ggml-org/whisper.cpp
- Qwen2.5 Ollama：https://ollama.com/library/qwen2.5

---

*本文件由视频解析方法总结Agent 自动生成 · 2026-03-29*
