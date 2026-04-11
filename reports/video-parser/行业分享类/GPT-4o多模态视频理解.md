# 行业分享类 - GPT-4o 多模态视频理解

## 核心工具/API

- **OpenAI GPT-4o**：
  - 端到端多模态模型，直接输入视频帧序列 + 音频理解
  - 支持视频内容问答、摘要、结构化信息提取
  - API 调用或 ChatGPT Plus 直接使用
- **OpenClaw videos_understand（内置）**：
  - 封装了多模态视频理解能力
  - 支持批量处理（最多 10 个视频并行）
  - 支持本地文件和 URL
- **Google Gemini**：
  - Gemini 1.5 / 2.0 系列支持超长视频（Gemini 2.0 支持 2 小时视频）
  - 上下文窗口巨大，适合分析超长视频
  - API：Vertex AI 或 Google AI Studio
- **Claude（Anthropic）**：
  - Claude 3.5 Sonnet / Opus 支持图像序列理解
  - 适合视频内容分析、逻辑推理类视频
- **咬嚼/通义智文国内模型**：
  - 智谱 GLM-4V：国内可用的多模态视频理解 API
  - 通义 VL-Max：阿里云视频理解服务

---

## 步骤流程

### 方案一：OpenClaw videos_understand（推荐，最简）

```python
# 直接调用 OpenClaw 内置 videos_understand 工具
videos_understand([{
    file: "https://example.com/video.mp4",
    prompt: `作为行业分析师，请深度分析这个视频：
    1. 视频主题和核心观点
    2. 行业趋势和关键数据
    3. 商业模式分析
    4. 竞争对手提及情况
    5. 关键技术/产品亮点
    6. 演讲者背景与风格评估
    7. 对行业的潜在影响
    请以结构化 JSON 格式输出。`
}])
```

### 方案二：GPT-4o 原生视频理解

```python
from openai import OpenAI
import base64
import requests

client = OpenAI(api_key="your-api-key")

# 方法1：通过 URL 传入视频（需公网可访问）
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "video_url",
                "video_url": {"url": "https://example.com/video.mp4"}
            },
            {
                "type": "text",
                "text": "请总结这个视频的核心内容，包括主题、关键数据和观点。"
            }
        ]
    }],
    max_tokens=4096
)
print(response.choices[0].message.content)

# 方法2：本地视频（需 base64 编码）
with open("video.mp4", "rb") as f:
    video_bytes = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "video",
                "video": {
                    "url": f"data:video/mp4;base64,{video_bytes[:100000]}"  # 截断示例
                }
            },
            {"type": "text", "text": "分析视频内容"}
        ]
    }]
)
```

### 方案三：GPT-4o 关键帧提取 + 分析（降低 Token 消耗）

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  FFmpeg      │ →  │  关键帧筛选  │ →  │  GPT-4o     │
│  抽帧         │    │  (10-20帧)   │    │  批量分析   │
└──────────────┘    └──────────────┘    └──────────────┘
```

```python
import subprocess
import base64

# Step 1: FFmpeg 等间隔提取 15 帧（覆盖 10 分钟视频）
subprocess.run([
    "ffmpeg", "-i", "industry_video.mp4",
    "-vf", "fps=1/40",  # 10分钟抽15帧
    "-q:v", "3",        # JPEG 质量
    "frames/%04d.jpg"
])

# Step 2: 批量 GPT-4o 分析（每帧附带时间戳推断）
import os
frames = sorted(os.listdir("frames/"))

analysis_results = []
for i, frame in enumerate(frames):
    with open(f"frames/{frame}", "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    estimated_time = i * 40  # 秒
    
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}},
                {"type": "text", "text": f"这是视频中大约 {estimated_time}秒 处的画面。请描述该画面的内容（演讲PPT/演示/场景等）。"}
            ]
        }]
    )
    analysis_results.append(f"[{estimated_time}s] {resp.choices[0].message.content}")

# Step 3: 综合总结
final_summary = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": f"根据以下视频帧分析结果，生成完整视频摘要：\n\n" + "\n".join(analysis_results)
    }]
)
```

### 方案四：Gemini 2.0 超长视频分析

```python
import google.generativeai as genai

genai.configure(api_key="your-gemini-api-key")

# 直接上传视频（Gemini 2.0 Flash 支持最长 2 小时）
video = genai.upload_video("long_industry_talk.mp4")

model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content([
    video,
    "分析这个行业分享视频：\n"
    "1. 核心议题和演讲框架\n"
    "2. 五大关键洞察\n"
    "3. 行业趋势预测\n"
    "4. 行动建议"
])
print(response.text)
```

---

## 适用场景

- ✅ 行业峰会/论坛演讲视频分析
- ✅ 产品发布会内容提取
- ✅ 商业路演/投资人说视频
- ✅ CEO 访谈、行业专家对话
- ✅ 快速了解视频核心观点（无需完整观看）
- ✅ 视频内容转图文文章/社交媒体摘要

---

## 避坑指南

### ⚠️ 坑1：API 直接传视频 Token 消耗巨大
- **问题**：直接传 MP4 文件容易超出上下文限制，费用高
- **解决**：先用 FFmpeg 抽帧，以图片序列传入（推荐 10-20 帧覆盖全程）

### ⚠️ 坑2：视频 URL 不可用/需登录
- **问题**：部分视频平台需要登录或视频无法公网访问
- **解决**：
  - 用 `yt-dlp` 先下载到本地
  - 或用 `summarize --youtube auto`（Apify fallback）提取字幕

### ⚠️ 坑3：国内模型调用限制
- **问题**：GPT-4o 在部分地区不可用，Gemini 需科学上网
- **解决**：
  - 智谱 GLM-4V：`zhipuai` SDK 国内直连
  - 通义 VL：`dashscope` SDK 阿里云内网调用
  - 火山引擎/腾讯云多模态 API

### ⚠️ 坑4：多语言视频翻译后理解偏差
- **问题**：非中文视频直接翻译可能产生术语误差
- **解决**：先用 Whisper 提取字幕保留原文，再让 GPT-4o 结合字幕 + 关键帧理解

---

## 参考链接

- GPT-4o 视频理解实战：https://jishuzhan.net/article/1916024739336933377
- GPT-4o 解读视频（CSDN）：https://blog.csdn.net/xindoo/article/details/143837432
- Whisper+GPT4 双语字幕翻译：https://zhuanlan.zhihu.com/p/664682407
- Gemini 视频分析 API：https://ai.google.dev/gemini-api/docs/video-understanding
- 12款AI模型音视频评测：https://cloud.tencent.com/developer/article/2554380
