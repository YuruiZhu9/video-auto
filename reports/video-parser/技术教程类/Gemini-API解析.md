# 技术教程类 — Gemini API 视频分析方案

## 核心工具/API

- **Google Gemini API (Firebase AI Logic)**：`generateContent()` / `generateContentStream()` 支持直接传入视频文件（base64 或 Cloud Storage URL），自动融合音轨 + 视觉帧进行多模态理解
- **支持的模型**：Gemini 1.5 Pro / Gemini 2.0 Pro / Gemini 2.0 Flash
- **输入方式**：
  - `InlineDataPart`（base64）：适合 < 20MB 的小视频
  - Cloud Storage URL（`gs://bucket/file.mp4`）：适合大文件
  - YouTube 视频 URL（部分模型支持）
- **结构化输出**：支持 JSON Schema，可直接指定输出格式

---

## 步骤流程

```
1. 准备视频文件
   → 本地文件：base64 编码后传入
   → 云端文件：使用 Cloud Storage URL
   → 视频格式：MP4 / MOV / WEBM / FLV / 3GPP 等（见下表）

2. 构造 prompt
   → 指定分析目标（如"提取所有命令行"、"列出讲解的所有概念"）
   → 指定输出格式（JSON / Markdown）

3. 调用 API
   → 构造 Content.multi([promptPart, InlineDataPart])
   → model.generateContent(prompt)

4. 解析响应
   → response.text → 结构化字符串
   → 如需 JSON：指定 schema 进行结构化输出
```

### API 调用示例（Python）

```python
import base64

# 读取视频文件并 base64 编码
with open("video.mp4", "rb") as f:
    video_bytes = base64.b64encode(f.read()).decode("utf-8")

# 构造多模态输入
from google.genai import types

prompt = """你是一位技术教程分析师。请从视频中提取：
1. 讲解的所有技术概念（带时间戳）
2. 所有命令行和代码片段
3. 关键步骤和操作顺序
请用 Markdown 格式输出。"""

contents = [
    types.Content(
        parts=[
            types.Part(text=prompt),
            types.Part(
                inline_data=types.Blob(
                    mime_type="video/mp4",
                    data=video_bytes
                )
            )
        ]
    )
]

response = model.generate_content(contents=contents)
print(response.text)
```

### 支持的视频格式与 MIME 类型

| 格式 | MIME 类型 | 备注 |
|------|-----------|------|
| MP4 | `video/mp4` | ✅ 推荐 |
| MOV | `video/quicktime` | ✅ 推荐 |
| WEBM | `video/webm` | ✅ 支持 |
| FLV | `video/x-flv` | ⚠️ 部分平台 |
| MPEG | `video/mpeg` | ✅ 支持 |
| WMV | `video/wmv` | ⚠️ 部分平台 |
| 3GPP | `video/3gpp` | ✅ 支持 |

### 重要限制

| 限制项 | 值 |
|--------|-----|
| 单次请求文件大小上限 | **20 MB**（base64 编码会增加约33%体积）|
| 单次请求最多视频数 | 10 个 |
| 推荐最大时长 | ~10 分钟（20MB 内） |
| 超大文件处理 | 建议先 ffmpeg 压缩或分段 |

---

## 适用场景

- ✅ 需要精准结构化输出（JSON Schema）的场景
- ✅ 视频时长 < 20 分钟、质量适中的教程
- ✅ 需要融合视觉帧 + 音频联合理解的技术讲解
- ✅ 技术面试复盘、代码演示视频解析
- ✅ API 集成到自动化流水线（GitHub Actions / CI）

---

## 避坑指南

- **文件大小超限**：20MB 是硬限制，大视频先用 ffmpeg 压缩：
  ```bash
  # 压缩至 15MB，CRF=28（质量损失可接受）
  ffmpeg -i input.mp4 -vf "scale=1280:-2" -crf 28 output.mp4
  ```
- **base64 编码体积膨胀**：20MB 视频 base64 后约 27MB，超出 HTTP 请求体限制，需分段或用 Cloud Storage URL
- **长视频处理**：超过 10 分钟的视频建议先切分：
  ```bash
  # 切分为每段 5 分钟
  ffmpeg -i input.mp4 -c copy -f segment -segment_time 300 part_%03d.mp4
  ```
- **中文 prompt**：Gemini 2.0 对中文支持良好，直接用中文指令即可
- **API Key 安全**：不要将 Gemini API Key 硬编码在代码中，建议使用环境变量
- **音频优先 vs 视觉优先**：如信息主要在音频中，可在 prompt 中明确"重点分析音频内容，视觉帧作为辅助"

---

## 参考链接

- Firebase AI Logic 视频分析文档：<https://firebase.google.cn/docs/ai-logic/analyze-video>
- Gemini API 结构化输出：<https://firebase.google.cn/docs/ai-logic/generate-content>
- Google Cloud Storage 上传视频：<https://cloud.google.com/storage/docs/uploads-objects>
- Gemini 模型对比：<https://firebase.google.cn/docs/ai-logic/models>
