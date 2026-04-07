# 通用工具 — n8n YouTube 视频自动化解析工作流

> 🤖 维护：视频解析方法总结Agent  
> 📅 新增日期：2026-03-30  
> 🔗 来源：n8n 社区工作流 / toolify.ai

---

## 核心工具/API

| 工具 | 类型 | 能力描述 |
|------|------|----------|
| **n8n** | 开源自动化平台 | 连接 API/工具，构建自动化工作流 |
| **YouTube Transcript API** | Python 库 | 直接获取 YouTube 视频字幕/转录文本 |
| **YouTube Data API v3** | Google API | 获取视频元信息（标题、描述、标签）|
| **OpenAI GPT / Claude API** | LLM API | 字幕 → 结构化文本转换 |
| **Firecrawl** | 网页抓取 API | 补充视频描述、评论区信息 |
| **Apify** | 数据抓取平台 | YouTube 视频下载、评论抓取 |

---

## 核心能力

n8n 工作流实现：**YouTube 视频 → 自动获取字幕 → AI 结构化 → 输出笔记**，全流程无需人工干预，适合批量处理。

| 能力 | 说明 |
|------|------|
| **字幕自动获取** | YouTube Transcript API 无需浏览器自动化，支持 100+ 语言 |
| **AI 结构化输出** | 将字幕转为带时间戳的 Markdown / JSON 结构 |
| **批量处理** | 输入视频 URL 列表，自动批量处理 |
| **多渠道推送** | 结果可推送至 Notion、Slack、钉钉、飞书等 |
| **定时触发** | 配合 RSS 监控新视频，自动解析 |

---

## 步骤流程

### n8n 工作流设计（五步）

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────┐
│  触发器       │ → │  YouTube Transcript │ → │  字幕清洗    │
│ (Webhook/定时)│    │  API 获取字幕      │    │  (时间戳过滤) │
└─────────────┘    └──────────────────┘    └──────┬───────┘
                                                  ↓
┌─────────────┐    ┌──────────────────┐    ┌──────────────┐
│  推送结果    │ ← │  结构化输出        │ ← │  GPT/Claude  │
│ (钉钉/Notion)│    │  (Markdown/JSON) │    │  AI 转换     │
└─────────────┘    └──────────────────┘    └──────────────┘
```

### 详细步骤

**Step 1 — 安装依赖**

```bash
pip install youtube-transcript-api n8n
# n8n 需要 Node.js 18+
npm install -g n8n
```

**Step 2 — 创建 n8n Workflow**

```
Node 1: HTTP Request
  Method: GET
  URL: https://www.googleapis.com/youtube/v3/videos
  Query: part=snippet&id={VIDEO_ID}&key={API_KEY}

Node 2: Code (Python)
  from youtube_transcript_api import YouTubeTranscriptApi
  transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-Hans', 'en'])
  # 输出：[{text, start, duration}, ...]

Node 3: Code (清洗)
  # 过滤静音、重复，保留有效字幕段
  cleaned = [s for s in transcript if len(s['text']) > 5]

Node 4: OpenAI / Claude (AI 转换)
  system: "你是一个专业的视频内容分析师..."
  prompt: f"将以下字幕转为结构化笔记：{cleaned}"
  
Node 5: Output (钉钉 Webhook / Notion)
```

**Step 3 — 核心 Python 代码示例**

```python
from youtube_transcript_api import YouTubeTranscriptApi
import openai

video_id = "dQw4w9WgXcQ"  # 替换为实际视频 ID

# 获取字幕（自动选择中文或英文）
try:
    transcript = YouTubeTranscriptApi.get_transcript(
        video_id, 
        languages=['zh-Hans', 'zh-Hant', 'en']
    )
except:
    # fallback 到自动生成字幕
    transcript = YouTubeTranscriptApi.get_transcript(
        video_id, 
        languages=['en']
    )

# 合并为纯文本
text = " ".join([s['text'] for s in transcript])

# AI 结构化
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "你是视频笔记专家，输出结构化Markdown"},
        {"role": "user", "content": f"总结以下视频内容，输出：\n1. 核心主题\n2. 关键观点（3-5点）\n3. 时间线摘要\n\n视频字幕：{text}"}
    ]
)
structured_output = response.choices[0].message.content
print(structured_output)
```

---

## 适用场景

- **B站/YouTube 技术UP主批量追踪**：配合 RSS 监控 + n8n 定时触发，新视频自动解析
- **企业内部视频知识库**：批量处理培训视频，自动生成笔记存 Notion
- **行业情报自动化**：监控竞品 YouTube 频道，新视频自动解析推钉钉
- **播客/演讲存档**：无字幕视频先用 Whisper 转录，再接 n8n 结构化

---

## 避坑指南

- **字幕不可用**：约 20% YouTube 视频无字幕 → fallback 到 Whisper 转录
- **API 配额**：YouTube Data API 有每日配额限制，批量抓取需申请配额提升
- **字幕语言**：非中英视频需确认字幕语言代码（如日语 `ja`，韩语 `ko`）
- **长视频分段**：超过 2 小时的视频，字幕可能分段获取，需合并处理
- **n8n 节点超时**：AI 节点处理大字幕时注意 timeout 设置

---

## 参考链接

- YouTube Transcript API：https://github.com/jdepoix/youtube-transcript-api
- n8n YouTube 视频转结构化笔记工作流：https://www.toolify.ai/zh/n8n/youtube-video-transcription-and-ai-structuring-tool
- n8n 官网：https://n8n.io
- Firecrawl：https://firecrawl.dev
