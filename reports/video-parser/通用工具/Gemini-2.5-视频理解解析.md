# Gemini 2.5 视频理解 — 原生多模态视频分析

## 核心工具/API

| 工具 | 用途 |
|------|------|
| **Gemini 2.5 Pro** | 原生多模态视频理解（音频+视觉+文字联合推理） |
| **Gemini API** | YouTube 视频 URL 直接输入，支持视频理解 |
| **Google AI Studio** | 在线视频理解应用开发和测试 |
| **Vertex AI** | 企业级 Gemini 视频分析部署 |
| **p5.js** | 将视频内容转化为交互式动画 |
| **Video To Learning App 模板** | Google AI Studio 官方入门模板 |

---

## 核心技术方法

### 1. 原生多模态架构
Gemini 2.5 是**首个原生多模态模型**，无缝整合音视频信息与代码生成能力，开创性地将视频理解与代码生成结合。

### 2. 视频处理规格

| 参数 | 标准模式 | 低分辨率（low）模式 |
|------|---------|------------------|
| 帧采样率 | 1 fps，线性子采样 | 1 fps，线性子采样 |
| 最大帧数 | 最多 256 帧 | 最多 7200 帧（~6小时） |
| 上下文窗口 | 100万 token | 200万 token |
| VideoMME 准确率 | **85.2%** | 84.7% |

### 3. 核心能力一览

| 能力 | 说明 | 适用场景 |
|------|------|---------|
| **时刻检索**（Moment Retrieval） | 利用音视频线索定位特定片段 | 从 1 小时视频中找到某段讲解 |
| **时间推理**（Temporal Reasoning） | 解决计数等复杂时序问题 | 视频中某动作重复了几次 |
| **密集字幕生成** | 详细描述视频每段内容 | 自动生成视频描述 |
| **视频转交互应用** | 视频内容→可交互学习应用 | 教程视频→练习题 App |
| **视频转动画** | 生成 p5.js 动画保持时间顺序 | 视频可视化复现 |

---

## 步骤流程

### 方式一：Google AI Studio（推荐入门）

```
1. 打开 https://aistudio.google.com/
2. 选择 "Video To Learning App" 或新建 Chat
3. 上传视频或粘贴 YouTube URL
4. 输入 Prompt（如"总结本视频核心内容"）
5. 获取结构化输出（摘要/章节/关键帧描述）
```

### 方式二：Gemini API 编程调用

```python
import google.genai as genai

client = genai.Client(api_key="YOUR_API_KEY")

# 直接上传 YouTube 视频 URL
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=[{
        "role": "user",
        "parts": [{
            "file_data": {
                "mime_type": "video/*",
                "file_uri": "https://www.youtube.com/watch?v=VIDEO_ID"
            }
        }, {
            "text": "总结这个视频的核心内容，提取关键时间点和要点。"
        }]
    }]
)
print(response.text)
```

### 方式三：视频帧 + Gemini API（精细控制）

```python
import base64, requests, glob

# 1. FFmpeg 提取关键帧
import subprocess
subprocess.run([
    "ffmpeg", "-i", "video.mp4", "-vf", "fps=1/30,scale=1280:-1",
    "-q:v", "2", "frames/frame_%04d.jpg"
], check=True)

# 2. 批量发送给 Gemini
import google.genai as genai
client = genai.Client(api_key="YOUR_API_KEY")

frames = sorted(glob.glob("frames/*.jpg"))[:20]
parts = [{"text": "这是视频关键帧，描述每帧内容："}]
for f in frames:
    with open(f, "rb") as img:
        parts.append({"inline_data": {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img.read()).decode()
        }})

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=[{"role": "user", "parts": parts}]
)
print(response.text)
```

---

## 适用场景

- **长视频理解**（1小时以上）：Gemini 2.5 低分辨率模式支持~6小时视频
- **多模态联合推理**：需要同时理解画面+语音+文字的复杂视频
- **行业分析报告**：Gemini 视频→结构化洞察→生成 PPT/文档
- **时刻精准检索**：从长视频中定位特定内容片段
- **视频内容可视化**：将视频转为交互式动画/p5.js 应用

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| YouTube URL 视频无法访问 | 地区限制 | 使用本地视频文件上传 |
| 视频太长被截断 | 超出帧数限制 | 使用 low 媒体分辨率模式（200万token） |
| API 调用超时 | 单次请求数据量过大 | 预处理：先 Whisper 转录，按段落分段调用 |
| 隐私顾虑 | 视频上传到 Google | 使用本地 whisper-cpp + 帧提取，数据不上传 |
| 成本过高 | 高频调用 Gemini API | 优先用 FFmpeg+Whisper+LLM 组合，成本更低 |

---

## 性能基准对比（2026年）

| 模型 | VideoMME 准确率 | 长视频支持 | 多模态原生 |
|------|--------------|---------|---------|
| **Gemini 2.5 Pro** | **85.2%** | ✅ ~6小时 | ✅ |
| GPT-4.1 (直接) | ~42% | 有限 | ❌ 需预处理 |
| GPT-4o (直接) | 36.6% | 有限 | ❌ 需预处理 |
| 人类水平 | 84.3% | ✅ | ✅ |
| 关键帧选择 (FOCUS) | +11.9% | ✅ | ✅ |

> Gemini 2.5 在 VideoMME 基准测试中**已超越人类水平**（84.3%）

---

## 参考链接

- Gemini API 视频理解文档: https://ai.google.dev/gemini-api/docs/video-understanding
- Google AI Studio: https://aistudio.google.com/
- Video To Learning App 模板: https://aistudio.google.com/u/1/apps/bundled/video-to-learning-app
- Gemini 2.5 博客: https://developers.googleblog.com/en/gemini-2-5-video-understanding/
