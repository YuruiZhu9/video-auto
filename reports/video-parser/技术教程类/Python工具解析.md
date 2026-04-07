# 技术教程类视频 - Python工具解析

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| **MoviePy** | Python视频编辑库，裁剪/拼接/添加字幕 |
| **OpenCV** | 视频帧提取、图像处理 |
| **pytube / yt-dlp** | YouTube视频下载 |
| **deep-translator / googletrans** | 字幕翻译 |
| **LLM API (OpenAI/Anthropic)** | 字幕内容分析与提取 |

---

## 步骤流程

### 完整Pipeline示例（Python脚本）

```python
# step1_download.py
import subprocess
result = subprocess.run([
    "yt-dlp", "-x", "--audio-format", "mp3",
    "--output", "audio.%(ext)s",
    "https://youtu.be/xxxx"
], capture_output=True, text=True)

# step2_transcribe.py
import openai
client = openai.OpenAI()
with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        response_format="srt"
    )
with open("subtitle.srt", "w") as f:
    f.write(transcript)

# step3_analyze.py
from openai import OpenAI
client = OpenAI()
with open("subtitle.srt") as f:
    content = f.read()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一个专业的技术教程分析助手..."},
        {"role": "user", "content": f"请分析以下字幕，提取：1.核心概念 2.代码示例 3.操作步骤\n\n{content}"}
    ]
)
```

---

## 适用场景

- **批量处理**：多个技术教程视频批量转录分析
- **定制化pipeline**：根据业务需求自定义解析逻辑
- **集成到Agent**：作为子模块嵌入自动化工作流
- **字幕翻译**：英文教程自动翻译后分析

---

## 避坑指南

### 问题1：pytube无法下载（YouTube反爬）
**解决方案**：改用 `yt-dlp`，功能更全，更新更频繁
```python
subprocess.run(["yt-dlp", "-f", "bestaudio", url])
```

### 问题2：Whisper API费用
**解决方案**：
- 使用本地 Whisper CLI（免费）：`subprocess.run(["whisper", "audio.mp3"])`
- 或使用开源替代：OpenAI的Whisper模型可本地部署

### 问题3：SRT字幕时间码解析错误
**解决方案**：用 `pysrt` 库正规解析
```python
import srt
with open("subtitle.srt") as f:
    subs = list(srt.parse(f))
```

---

## 参考链接

- yt-dlp: `https://github.com/yt-dlp/yt-dlp`
- MoviePy: `https://zulko.github.io/moviepy/`
- OpenCV: `https://opencv.org/`
- Whisper: `https://github.com/openai/whisper`
- pysrt: `https://pypi.org/project/pysrt/`
