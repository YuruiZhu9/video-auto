# 视频理解 API 深度对比

> 对比主流视频理解/解析 API  
> 更新时间：2026-04-08

---

## API 对比总表

| API | 厂商 | 输入方式 | 中文支持 | 免费额度 | 特点 |
|-----|------|----------|----------|----------|------|
| **videos_understand** | OpenClaw 内置 | 本地文件/URL | ✅ 优秀 | 不限 | 端到端分析，多模态 |
| **Qwen-VL** | 阿里云 | 图片序列 | ✅ 优秀 | 2000次/天 | 视频帧序列理解 |
| **Gemini 2.0** | Google | 视频/音频 | ✅ 良好 | 部分免费 | 原生视频理解 |
| **GPT-4o** | OpenAI | 图片/音频 | ✅ 良好 | $5免费额度 | 视频帧联合分析 |
| **智谱 GLM-4V** | 智谱AI | 图片序列 | ✅ 优秀 | 200万Tokens/天 | 视频帧分析 |
| **Whisper** | OpenAI | 音频 | ✅ 良好 | 开源免费 | 语音转文字 |
| **youtube-transcript-api** | 开源 | URL | ✅ 支持 | 开源免费 | 字幕提取 |

---

## OpenClaw videos_understand

**优势**：
- 内置，无需配置 API Key
- 支持本地文件和 URL
- 中文理解效果好
- 单次最多 10 个视频

**劣势**：
- 依赖模型版本，可能不是最新
- 长视频需要分段

**最佳场景**：OpenClaw 用户的首选，无需额外配置

---

## 阿里通义 Qwen-VL

**优势**：
- 视频帧序列理解能力
- 阿里云生态集成
- 视觉理解精度高

**调用示例**：
```python
import dashscope
from dashscope import MultiModalConversation

dashscope.api_key = "YOUR_API_KEY"

response = MultiModalConversation.call(
    model='qwen-vl-plus',
    messages=[{
        "role": "user",
        "content": [
            {"image": "frame1.jpg"},
            {"image": "frame2.jpg"},
            {"image": "frame3.jpg"},
            {"text": "描述视频中发生了什么"}
        ]
    }]
)
```

---

## Google Gemini 2.0

**优势**：
- 原生视频理解（不拆分帧）
- 音频+视频联合理解
- 上下文窗口大（100万token）

**调用示例**：
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")

video = genai.upload_file("/path/to/video.mp4")
response = model.generate_content([
    video,
    "详细描述这个技术演示视频的操作步骤"
])
```

---

## OpenAI Whisper（语音转写）

**优势**：
- 开源免费，支持本地部署
- 中文识别效果好（large 模型）
- 支持时间戳

**调用示例**：
```python
import whisper

model = whisper.load_model("large")
result = model.transcribe("audio.wav", language="zh", word_timestamps=True)

# 带时间戳输出
for segment in result["segments"]:
    print(f"[{segment['start']:.1f}s] {segment['text']}")
```

---

## 选型建议

| 需求 | 推荐方案 |
|------|----------|
| OpenClaw 用户首选 | videos_understand |
| 国内免费方案 | 智谱 GLM-4V / 阿里通义千问 |
| 原生视频理解 | Gemini 2.0 |
| 语音转文字 | Whisper（本地部署）|
| YouTube 字幕提取 | youtube-transcript-api |
| 高精度多帧分析 | GPT-4o / Gemini 2.0 |

---

## 成本与限制

| 方案 | 成本 | 并发限制 | 上下文限制 |
|------|------|----------|------------|
| videos_understand | 免费（内置）| - | 模型决定 |
| Qwen-VL Plus | 按调用计费 | 10 QPS | 8K |
| Gemini 2.0 Flash | 免费（限速）| 15 RPM | 1M token |
| Whisper API | $0.006/分钟 | - | - |
| GLM-4V | 免费额度内 | - | 8K |
