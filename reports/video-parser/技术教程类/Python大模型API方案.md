# 技术教程类 - Python + 大模型 API 方案

## 方案对比

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| 阶跃星辰 Step-1o | 中文优化好、有免费额度 | 128MB限制 | 中文技术教程 |
| Google Gemini | 长视频支持（90分钟） | 成本较高 | 深度分析 |
| Qwen2.5-VL | 超长视频（1小时）、本地免费 | 显存要求高 | 中文长视频 |

---

## 方案一：阶跃星辰 Step-1o Video

### 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| step-1o-turbo-vision | 视频理解模型 |
| Files API | 视频上传加速 |
| Chat API | 对话接口 |

### 步骤流程

#### 1. 获取 API Key

在 [阶跃星辰开放平台](https://platform.stepfun.com/) 注册并获取 API Key

#### 2. 上传视频（可选）

```python
import requests

# 上传视频文件
response = requests.post(
    "https://api.stepfun.com/v1/files",
    headers={"Authorization": f"Bearer {API_KEY}"},
    files={"file": open("video.mp4", "rb")},
    data={"purpose": "storage"}
)
file_id = response.json()["id"]
```

#### 3. 调用视频理解 API

```python
import requests

url = "https://api.stepfun.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

payload = {
    "model": "step-1o-turbo-vision",
    "messages": [{
        "role": "user",
        "content": [
            {
                "type": "video_url",
                "video_url": {"url": "https://example.com/video.mp4"}
            },
            {
                "type": "text",
                "text": "分析这个Python教程视频的主要内容，提取关键代码和知识点"
            }
        ]
    }],
    "max_tokens": 1024
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(result["choices"][0]["message"]["content"])
```

### 适用场景

- 中文技术教程视频
- 代码演示视频
- 编程教学视频

### 避坑指南

#### 问题1：文件大小限制
**限制**：单个视频小于 128MB

**解决方案**：
```bash
# 使用 FFmpeg 切割视频（每120秒一段）
ffmpeg -i input.mp4 -acodec copy -f segment -segment_time 120 -vcodec copy -reset_timestamps 1 output_%d.mp4

# 压缩视频
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset fast output.mp4
```

#### 问题2：格式限制
**限制**：仅支持 MP4 格式

**解决方案**：
```bash
# 转换为 MP4
ffmpeg -i input.mkv -codec copy output.mp4
```

#### 问题3：处理时间长
**问题**：视频下载和审核需要较长时间

**建议**：
- 使用 CDN 或高速对象存储
- 设计等待交互提示用户

---

## 方案二：Google Gemini Video

### 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| Gemini 1.5 Pro | 长视频理解（最长90分钟） |
| Gemini 1.5 Flash | 快速处理 |

### 步骤流程

#### 1. 获取 API Key

在 [Google AI Studio](https://aistudio.google.com/app/apikey) 申请

#### 2. 调用 API

```python
import google.generativeai as genai
import requests

# 配置 API
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# 方式1：使用 URL
model = genai.GenerativeModel('gemini-1.5-pro')

# 方式2：直接上传视频文件
video = genai.upload_video(path="video.mp4")

response = model.generate_content([
    video,
    "分析这个技术教程视频的主要内容"
])

print(response.text)
```

### 适用场景

- 长时间技术教程
- 需要深度理解的复杂内容
- 多模态内容分析

### 避坑指南

#### 问题1：成本控制
**建议**：
- 使用 Gemini 1.5 Flash 降低成本
- 合理设置 max_tokens

#### 问题2：视频格式
**支持格式**：MP4, MOV, AVI 等常见格式

---

## 方案三：Qwen2.5-VL 视频理解（2026年新增）

### 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| Qwen2.5-VL-72B | 阿里通义千问最新版，支持1小时视频 |
| Qwen2.5-VL-7B | 轻量版本，显存要求低 |
| DashScope API | 阿里云 API 调用 |
| Ollama | 本地部署方案 |

### 步骤流程

#### 1. API 调用（DashScope）

```python
import dashscope
from dashscope import MultiModalConversation

# 配置 API Key
dashscope.api_key = "your-dashscope-api-key"

# 准备消息
messages = [{
    "role": "user",
    "content": [
        {"video": "https://example.com/tutorial.mp4"},
        {"text": "提取这个技术教程视频的关键步骤和知识点"}
    ]
}]

# 调用模型
response = MultiModalConversation.call(
    model='qwen2.5-vl-72b-instruct',
    messages=messages
)

# 解析结果
print(response.output.choices[0].message.content[0]['text'])
```

#### 2. 本地部署（Ollama）

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull qwen2.5-vl:72b

# 运行
ollama run qwen2.5-vl:72b
```

### 突出优势

- **超长视频**：支持最长1小时视频理解
- **时间感知**：支持细粒度时间戳定位
- **结构化输出**：原生支持JSON/坐标输出格式
- **中文优化**：对中文技术内容理解更精准
- **本地免费**：Ollama本地部署无API费用

### 适用场景

- 超长技术教程视频（B站课程等）
- 中文技术社区视频
- 需要结构化JSON输出的自动化流程
- 企业内部分析（本地部署保护隐私）

### 避坑指南

#### 问题1：显存要求
**72B模型**：需要约48GB显存
**7B模型**：需要约8GB显存

**解决方案**：
- 使用7B轻量版本
- 使用云GPU实例

#### 问题2：首次加载慢
**建议**：使用Ollama保持模型常驻内存

---

## 方案四：本地 Whisper + 大模型组合

### 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| FFmpeg | 提取音频 |
| Whisper (OpenAI) | 语音转文字 |
| 大模型 | 内容理解和整理 |

### 步骤流程

```python
import subprocess
import whisper

# 1. 提取音频
subprocess.run([
    "ffmpeg", "-i", "video.mp4", "-vn",
    "-acodec", "libmp3lame", "-q:a", "2",
    "audio.mp3"
])

# 2. 语音转写
model = whisper.load_model("base")
result = model.transcribe("audio.mp3", language="zh")

# 3. 内容理解
# 调用大模型 API 整理转录内容
```

### 适用场景

- 需要完整文字稿
- 本地处理需求
- 无需视频理解 API

---

## 总结

| 方案 | 视频限制 | 中文支持 | 成本 | 易用性 |
|------|----------|----------|------|--------|
| Step-1o | 128MB | ⭐⭐⭐⭐⭐ | 免费额度 | ⭐⭐⭐⭐ |
| Qwen2.5-VL | 1小时 | ⭐⭐⭐⭐⭐ | 免费/本地 | ⭐⭐⭐⭐ |
| Gemini | 90分钟 | ⭐⭐⭐ | 按量付费 | ⭐⭐⭐⭐ |
| 本地方案 | 无限制 | ⭐⭐⭐⭐ | 本地/免费 | ⭐⭐⭐ |

---

## 参考链接

- 阶跃星辰：https://platform.stepfun.com/docs/guide/video_chat
- Google Gemini：https://gemini.google.com/docs
- Qwen2.5-VL：https://zhihu.com/question/10742671583
- Ollama Qwen：https://ollama.com/library/qwen2.5-vl
- FFmpeg：https://ffmpeg.org/documentation.html

---

*更新时间：2026-03-16*
