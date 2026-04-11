# 技术教程类 - Whisper 语音转写解析

## 核心工具/API

- **OpenAI Whisper**：业界领先的语音识别模型
  - `whisper-large-v3` / `whisper-large-v3-turbo`：最高准确率
  - `whisper-medium` / `whisper-small`：速度优先
  - 支持 100+ 语言，中英文识别优秀
  - 本地运行（Python）或 API 调用
- **GPT-4o-transcribe**（2025 新）：
  - OpenAI 新一代语音转文本 API
  - 相比 Whisper 在专业术语、口音适应性上更强
  - 支持 prompt 注入（提供上下文提升准确率）
- **summarize Skill**：整合了 Whisper + LLM 的端到端方案
  - 一行命令完成：音频提取 → 语音转写 → 内容总结
- **yt-dlp**：从 YouTube/视频网站提取音频/视频
  - `yt-dlp --extract-audio --audio-format mp3 URL`

---

## 步骤流程

### 方案一：summarize Skill（最简路径）

```bash
# YouTube 视频 → 字幕提取 → 摘要
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto --length long

# 仅提取字幕文本（长视频分段处理）
summarize "https://youtu.be/xxxx" --youtube auto --extract-only > transcript.txt
```

### 方案二：Whisper Python 本地转写

```python
import whisper
import yt_dlp

# Step 1: 下载音频（YouTube 示例）
def download_audio(youtube_url, output_path="audio.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return output_path

# Step 2: Whisper 转写
model = whisper.load_model("large-v3")
result = model.transcribe(
    "audio.mp3",
    language="zh",        # 指定语言（中英文混排建议留空自动检测）
    initial_prompt="这是一段技术教程视频，包含Python编程和AI相关内容。",
    # prompt 注入：提升专业术语识别率
    word_timestamps=True,  # 输出每个词的置信度和时间戳
)

# Step 3: 输出结果
print(f"语言：{result['language']}")
print(f"总时长：{result['duration']:.1f}秒")
for seg in result['segments']:
    print(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
```

### 方案三：GPT-4o-transcribe（高精度场景）

```python
import openai
import base64

# 音频文件读取
with open("audio.mp3", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

client = openai.OpenAI(api_key="your-api-key")

response = client.audio.transcriptions.create(
    model="gpt-4o-transcribe",
    file=open("audio.mp3", "rb"),
    prompt="技术教程内容，包含机器学习、Python编程和神经网络等专业术语。"
)

print(response.text)
```

### 方案四：Whisper + GPT-4 结构化总结 Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  音频提取     │ →  │  Whisper     │ →  │  GPT-4       │ →  │  结构化输出  │
│  (yt-dlp)    │    │  转写为文字  │    │  智能总结    │    │  JSON/Markdown│
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

```python
# 完整 Pipeline
def parse_video_to_structured(url, topic_hint=""):
    # 1. 提取音频
    audio_path = download_audio(url)
    
    # 2. Whisper 转写
    model = whisper.load_model("medium")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # 3. GPT-4 总结
    prompt = f"""你是一个专业的技术教程分析助手。请分析以下视频转写文本：
    
    主题提示：{topic_hint}
    
    转写内容：
    {result['text']}
    
    请提取并返回 JSON 格式：
    {{
        "title": "视频标题/主题",
        "duration": "视频时长（分：秒）",
        "key_points": ["核心知识点1", "核心知识点2"],
        "steps": [{{"step": 1, "time": "时间点", "action": "操作描述"}}],
        "code_snippets": ["代码片段列表"],
        "summary": "100字以内的摘要"
    }}"""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)
```

---

## 适用场景

- ✅ 技术教程视频（编程教学、工具使用演示）
- ✅ 会议/访谈/演讲录音整理
- ✅ 播客（Podcast）内容提取
- ✅ 无字幕视频的语音内容获取
- ✅ 需要精确时间戳的视频内容定位
- ✅ 多语言视频的翻译制作

---

## 避坑指南

### ⚠️ 坑1：Whisper 中文识别"口音幻觉"
- **问题**：说话带口音时，Whisper 可能产生错误汉字（谐音替代）
- **解决**：
  - prompt 注入专业术语：`initial_prompt="涉及 Python、TensorFlow、神经网络等专业词汇"`
  - 事后用 `word_timestamps` 定位，人工校验关键段落

### ⚠️ 坑2：YouTube 音频提取失败（版权/地区限制）
- **问题**：`yt-dlp` 遇到某些视频无法下载音频流
- **解决**：
  - 尝试 `yt-dlp -f "bestaudio[ext=m4a]" URL`
  - 使用 `summarize --youtube auto`（自动切换 Apify fallback）
  - 备用：本地视频直接处理

### ⚠️ 坑3：长音频内存溢出
- **问题**：1小时以上音频，`whisper.load_model()` 显存不足
- **解决**：
  - 使用 `whisper.small` 或 `whisper.tiny`（牺牲精度换速度/内存）
  - 分段处理：先切分音频再逐段转写
  - GPU 推理：`whisper.load_model("large-v3", device="cuda")`

### ⚠️ 坑4：多人对话视频说话人分离
- **问题**：Whisper 只输出纯文本，无法区分说话人
- **解决**：使用 Diarization（说话人分离）工具：
  - `pyannote.audio`（开源，开源版需申请使用）
  - AssemblyAI / Rev AI 等商业 API 带说话人分离

---

## 参考链接

- Whisper GitHub：https://github.com/openai/whisper
- yt-dlp GitHub：https://github.com/yt-dlp/yt-dlp
- GPT-4o-transcribe 文档：https://developers.openai.com/api/docs/guides/speech-to-text
- pyannote.audio（说话人分离）：https://github.com/pyannote/pyannote-audio
- Whisper 中文评测报告：https://cloud.tencent.com/developer/article/2554380
