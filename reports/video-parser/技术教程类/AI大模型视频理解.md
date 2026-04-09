# 技术教程类 - AI 大模型视频理解

> 适合对象：需要深度理解视频语义、提取结构化知识、自动生成摘要的场景

---

## 方法一：Google Gemini（原生多模态视频理解）

### 核心工具/API
- **API**：Google Gemini API (gemini-2.0-flash / gemini-1.5-pro)
- **说明**：Gemini 原生支持视频输入，可直接分析视频帧序列+音频
- **费用**：免费额度充足（gemini-2.0-flash 免费大量调用）

### 步骤流程
```
1. 安装 SDK：pip install google-genai
2. 配置 API Key：export GOOGLE_API_KEY="your_key"
3. 读取视频文件（本地或 GCS）
4. 调用 Gemini 分析：
   - 支持直接传视频文件（FFmpeg 提取帧或直接传 MP4）
   - 支持多轮对话追问视频内容
5. 提取结构化输出（JSON 格式）
```

### Python 示例
```python
import google.genai as genai
from google.genai import types

client = genai.Client(api_key="YOUR_API_KEY")

# 直接分析视频文件
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Content(
            parts=[
                types.Part.from_uri(
                    file_uri="gs://bucket/video.mp4",
                    mime_type="video/mp4"
                )
            ]
        ),
        "请详细描述这个技术教程视频的内容，包括：\n"
        "1. 视频主题\n"
        "2. 主要步骤和知识点\n"
        "3. 使用了哪些工具/技术\n"
        "4. 总结3个核心takeaway"
    ]
)
print(response.text)
```

### 适用场景
- 长视频（数小时）的快速结构化理解
- 技术教程的知识点提取和总结
- 多模态综合分析（画面+语音+文字同时理解）

### 避坑指南
- ⚠️ Gemini 免费版有速率限制，高频调用需申请付费配额
- ⚠️ 视频文件过大（>100MB）建议先切分或压缩
- ⚠️ 中文视频理解效果不如英文，可考虑先用 Whisper 转中文再分析

---

## 方法二：OpenAI GPT-4o / GPT-4V（视觉理解 + 函数调用）

### 核心工具/API
- **API**：OpenAI Vision (GPT-4o / GPT-4-turbo)
- **说明**：提取视频关键帧后，调用 Vision 模型分析每帧
- **函数调用**：支持 JSON Schema 输出，提取结构化知识

### 步骤流程
```
Pipeline 设计（三步）：

Step 1 - 关键帧提取
  └─ FFmpeg 或 video-frames-skill 提取 N 个关键帧（如每30秒一帧）
  └─ 建议分辨率：1080p 视频采样到 512x512 或 1024x1024

Step 2 - 帧序列分析
  └─ 将关键帧按时间顺序组合发给 GPT-4o
  └─ Prompt 示例："这是一系列技术教程视频的关键帧，
      请按时间顺序描述视频内容，提取步骤清单"

Step 3 - 结构化输出
  └─ 用 JSON Schema 约束输出格式
  └─ 提取：标题、步骤列表、工具清单、关键概念、时间戳摘要
```

### Python 示例
```python
import openai
from PIL import Image
import base64, io

# 读取关键帧（示例：3帧）
frames = ["frame_0s.jpg", "frame_30s.jpg", "frame_60s.jpg"]

content = []
for f in frames:
    img = Image.open(f)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    content.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"}
    })

content.append({
    "type": "text",
    "text": "这是视频的3个关键时刻帧，请按时间顺序描述视频内容"
})

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": content}],
    response_format={"type": "json_object"},
)
print(response.choices[0].message.content)
```

### 适用场景
- 需要精确结构化输出的知识提取
- 配合函数调用（function calling）自动写入笔记系统
- 画面信息丰富（图表、代码、UI）的教程分析

### 避坑指南
- ⚠️ OpenAI API 按 token 计费，关键帧分辨率不宜过高
- ⚠️ 每帧有 4K 限制，分辨率过高会被自动压缩
- ⚠️ 帧数不宜太多（建议 ≤ 20帧），否则上下文超出限制

---

## 方法三：video-analyzer + Ollama（完全本地方案）

### 核心工具/API
- **视频分析**：video-analyzer（见 Python 工具篇）
- **LLM 推理**：Ollama（本地部署，支持 LLaVA、Qwen-Vision 等）
- **说明**：整套流程无需外网，完全免费

### 步骤流程
```
1. 安装 Ollama：curl -fsSL https://ollama.com/install.sh | sh
2. 下载 Vision 模型：ollama pull llava
3. 启动 Ollama 服务：ollama serve（后台运行）
4. 配置 video-analyzer 使用 Ollama 端点
5. 运行分析：video-analyzer video.mp4
```

### Ollama 支持的视觉模型
| 模型 | 参数量 | 视觉能力 | 推荐场景 |
|------|--------|---------|---------|
| llava | 7B | 基础 | 快速本地测试 |
| llava:13b | 13B | 较好 | 通用视频分析 |
| qwen2-vl | 7B | 优秀 | 中文视频首选 |
| internvl3 | 14B | 最强 | 高精度需求 |

### 适用场景
- 隐私敏感视频（医疗、内部培训）
- 离线环境（无网络服务器）
- API 费用敏感场景

### 避坑指南
- ⚠️ 本地推理速度慢，GPU 加速强烈建议（至少 8GB 显存）
- ⚠️ Ollama 默认不能并发请求，并行处理需启动多个实例

---

## 方法四：Claude（视频帧分析 + 结构化输出）

### 核心工具/API
- **API**：Anthropic Claude（via API）
- **说明**：通过视频帧提取 + Claude 视觉理解，支持超长上下文

### 步骤流程
```
1. 用 FFmpeg 提取视频关键帧（建议每分钟 3-5 帧）
2. 将帧序列发给 Claude 3.7 Sonnet（200K 上下文）
3. 使用 prompt engineering 引导结构化输出
4. 利用 Claude 的 MCP 工具直接写文件/调用 API
```

### 推荐 Prompt 模板
```
你是一位专业的技术教程分析师。
以下是这个视频的 {N} 个关键帧截图，按时间顺序排列。
请分析并输出 JSON 格式：
{
  "title": "视频标题",
  "duration": "视频时长",
  "summary": "200字以内的摘要",
  "steps": ["步骤1", "步骤2", ...],
  "tools": ["工具1", "工具2", ...],
  "concepts": ["概念1", "概念2", ...],
  "key_timestamps": [{"time": "0:30", "description": "..."}]
}
```

### 适用场景
- 需要深度推理和逻辑分析的视频教程
- 复杂概念解释类视频（学术演讲、论文解读）
- 与 Claude Code 结合做 AI 辅助学习笔记

### 避坑指南
- ⚠️ Claude 不支持直接输入视频，需先提取帧
- ⚠️ 帧数过多超出上下文窗口时分批处理
- ⚠️ Claude 3.5 Sonnet 视觉能力略弱于 GPT-4o

---

## 综合对比

| 方法 | 成本 | 速度 | 视频理解深度 | 本地化 | 上手难度 |
|------|------|------|-------------|--------|---------|
| Gemini 2.0 Flash | 免费大量 | 快 | ⭐⭐⭐⭐ | ❌ | ⭐ |
| GPT-4o | 按Token计费 | 快 | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐ |
| video-analyzer + Ollama | 完全免费 | 慢 | ⭐⭐⭐ | ✅ | ⭐⭐⭐ |
| Claude 3.7 Sonnet | 按Token计费 | 快 | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐ |

---

## 参考链接
- Google Gemini API：https://ai.google.dev/gemini-api
- OpenAI GPT-4o：https://platform.openai.com/docs/models/gpt-4o
- Ollama：https://ollama.com
- video-analyzer：https://github.com/byjlw/video-analyzer
- LLaVA 模型：https://github.com/haotian-liu/LLaVA
