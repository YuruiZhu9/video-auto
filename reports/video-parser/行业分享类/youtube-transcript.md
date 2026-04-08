# 行业分享类 - YouTube/B站字幕 + LLM 总结

> 解析类型：行业分享、技术会议、产品发布会  
> 核心方法：字幕提取 + 多模态 LLM 分析  
> 更新时间：2026-04-08

---

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| **summarize skill** | OpenClaw 一站式总结工具 |
| **youtube-transcript-api** | YouTube 字幕提取 |
| **智谱 GLM-4-Flash** | 免费 LLM（200万Tokens/天）|
| **videos_understand** | OpenClaw 内置视频理解 |

---

## 步骤流程

### 方案 A：summarize skill 一键总结（推荐）

```bash
# YouTube 视频总结
summarize "https://youtu.be/VIDEO_ID" --youtube auto --length medium

# 提取字幕（不总结）
summarize "https://youtu.be/VIDEO_ID" --youtube auto --extract-only
```

### 方案 B：YouTube 字幕提取 → LLM 结构化

```python
from youtube_transcript_api import YouTubeTranscriptApi
import requests

# Step 1: 提取字幕
def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(
        video_id, languages=['zh-Hans', 'zh', 'en']
    )
    return " ".join([s['text'] for s in transcript])

# Step 2: LLM 结构化
def summarize_industry(text):
    prompt = f"""将以下行业分享内容整理为结构化笔记：
1. 提炼3-5个核心观点
2. 列出关键数据/案例
3. 总结主要结论
4. 标注行业趋势

内容：{text[:8000]}"""

    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={"Authorization": "Bearer YOUR_KEY"},
        json={"model": "glm-4-flash", "messages": [{"role": "user", "content": prompt}]}
    )
    return resp.json()["choices"][0]["message"]["content"]
```

### 方案 C：B站视频字幕提取

```python
import requests

def get_bilibili_subtitle(bvid):
    """获取B站字幕"""
    resp = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}").json()
    cid = resp['data']['cid']
    sub_url = f"https://api.bilibili.com/x/web-interface/subtitle?sessdata=YOUR_SESSDATA&aid={resp['data']['aid']}&cid={cid}"
    sub = requests.get(sub_url).json()
    return sub.get('data', {}).get('subtitles', [])
```

### 方案 D：videos_understand 直接分析

适用：发布会、路演、无字幕视频

```python
videos_understand(
  videos_info=[{
    "file": "/workspace/industry_event.mp4",
    "prompt": """分析这个行业分享视频：
1. 演讲主题和核心议题
2. 前3-5个最重要观点（带时间戳）
3. 关键数据/案例/公司
4. 行业趋势判断
5. 新产品/创新发布"""
  }]
)
```

---

## 适用场景

| 场景 | 推荐方案 |
|------|----------|
| YouTube 有字幕视频 | 方案 A summarize skill |
| YouTube 无字幕视频 | 方案 B + Whisper |
| B站有字幕视频 | 方案 C B站字幕API |
| B站无字幕/发布会 | 方案 D videos_understand |

---

## 避坑指南

### ⚠️ YouTube 字幕不可用
解决：summarize skill 自动降级到 Whisper，或用 videos_understand

### ⚠️ B站需要登录
解决：更新 SESSDATA cookie，或直接用 videos_understand 分析

### ⚠️ 长视频分段
超过1小时建议分段总结，每段200段落：

```python
def chunk_transcript(transcript, chunk_size=200):
    chunks = []
    for i in range(0, len(transcript), chunk_size):
        chunk_text = " ".join([s['text'] for s in transcript[i:i+chunk_size]])
        chunks.append({"text": chunk_text, "start": transcript[i]['start']})
    return chunks
```

---

## 参考链接

- summarize skill：/app/openclaw/skills/summarize/SKILL.md
- youtube-transcript-api：https://github.com/jdepoix/youtube-transcript-api
- 智谱AI：https://open.bigmodel.cn/
