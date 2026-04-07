# 技术教程类 - OpenClaw Media Understanding 2026 完整配置指南

> 更新日期：2026-03-22
> 维护者：小M

---

## 核心工具/API

| 工具 | 功能描述 | 说明 |
|------|----------|------|
| `videos_understand` | 视频内容理解工具，批量分析最多10个视频 | OpenClaw 内置 |
| `audios_understand` | 音频理解/转录工具 | OpenClaw 内置 |
| `images_understand` | 图片理解工具 | OpenClaw 内置 |
| `media.config` | OpenClaw 媒体理解配置系统 | 配置文件 |
| Gemini CLI | 本地视频理解 fallback | 无需 API Key |
| whisper / whisper-cpp | 本地音频转录 | CLI 工具 |

---

## 一、Media Understanding 系统架构（2026版）

OpenClaw 的媒体理解系统支持**三大能力**，每种均可配置多模型级联 fallback：

```
inbound 附件（图片/音频/视频）
        ↓
  媒体理解管道
   /    |    \
图片   音频   视频   ← 三大能力独立配置
 |      |      |
v   v  v      v
模型1  模型1  模型1   ← 每个能力支持多模型级联
 ↓    ↓     ↓
模型2  模型2  模型2
 ↓    ↓     ↓
 ...  ...   ...
```

---

## 二、Provider 支持矩阵（2026年）

| 能力 | 支持的 Provider | 推荐模型 |
|------|----------------|---------|
| **图片** | OpenAI / Anthropic / Google / MiniMax / pi-ai | gpt-5.2, claude-opus-4-6, gemini-3-flash-preview |
| **音频** | OpenAI (Whisper) / Groq / Deepgram / Google / Mistral | whisper-1, deepgramnova, gemini-2.0-flash-exp |
| **视频** | **仅 Google（Gemini API）** | gemini-3-flash-preview, gemini-3-pro-preview |

> ⚠️ **视频理解仅 Gemini API 原生支持**，其他 Provider 的视频能力均通过 Gemini CLI fallback 实现。

---

## 三、Auto-Detect 自动检测顺序

如果未配置模型，OpenClaw 按以下顺序自动检测可用方案：

### 音频（Audio）
1. `sherpa-onnx-offline`（本地，需配置 `SHERPA_ONNX_MODEL_DIR`）
2. `whisper-cpp`（本地 CLI，需 `WHISPER_CPP_MODEL` 或内置 tiny 模型）
3. `whisper`（Python CLI，自动下载模型）
4. **Provider 级联**：OpenAI Whisper → Groq → Deepgram → Google

### 视频（Video）
1. **Gemini CLI**（本地 fallback，无需 Key）
2. **Provider**：Google Gemini API

### 图片（Image）
1. **Provider 级联**：OpenAI → Anthropic → Google → MiniMax

---

## 四、完整配置示例

### 4.1 高质量视频理解配置（推荐）

```json5
{
  tools: {
    media: {
      models: [
        // 图片理解
        { provider: "openai", model: "gpt-5.2", capabilities: ["image"], maxBytes: 10485760 },
        { provider: "anthropic", model: "claude-opus-4-6", capabilities: ["image"] },
        { provider: "google", model: "gemini-3-flash-preview", capabilities: ["image", "video", "audio"] },
      ],
      video: {
        enabled: true,
        maxChars: 800,       // 视频理解输出上限（默认500，建议调大）
        maxBytes: 52428800,  // 50MB（最大支持）
        timeoutSeconds: 180, // 超时时间
        models: [
          {
            provider: "google",
            model: "gemini-3-flash-preview",
            prompt: "详细分析这个技术教程视频，提取关键步骤、代码示例、技术要点。用中文回答。",
            maxChars: 800,
          },
          // Fallback：Gemini CLI 本地处理
          {
            type: "cli",
            command: "gemini",
            args: [
              "-m", "gemini-3-flash",
              "--allowed-tools", "read_file",
              "Read the video at {{MediaPath}}. Describe all key technical content, code examples, and steps in <= {{MaxChars}} characters. Respond in Chinese.",
            ],
            maxChars: 800,
            maxBytes: 104857600, // CLI 模式可支持更大文件
            capabilities: ["video"],
          },
        ],
      },
      audio: {
        enabled: true,
        echoTranscript: true,       // 输出中包含原文
        echoFormat: '📝 "{transcript}"',
        maxBytes: 20971520,         // 20MB
        models: [
          { provider: "openai", model: "whisper-1" },
          { provider: "groq", model: "whisper-large-v3", maxBytes: 25000000 },
          { type: "cli", command: "whisper", args: ["--model", "medium", "{{MediaPath}}"] },
        ],
      },
    },
  },
}
```

### 4.2 中文技术教程优化配置

```json5
{
  tools: {
    media: {
      video: {
        enabled: true,
        language: "zh",  // 明确指定中文
        models: [
          {
            provider: "google",
            model: "gemini-3-flash-preview",
            prompt: "你是一个专业的技术教程分析师。请详细分析这个视频：\n1. 视频主题和定位\n2. 关键知识点列表\n3. 代码示例和配置步骤\n4. 适用人群和学习路径\n5. 总结核心价值\n请全部用中文回答，输出结构化内容。",
            maxChars: 1200,
          },
        ],
      },
    },
  },
}
```

### 4.3 离线/隐私敏感场景配置（纯本地）

```json5
{
  tools: {
    media: {
      video: {
        enabled: true,
        models: [
          // Gemini CLI fallback（无需 API Key）
          {
            type: "cli",
            command: "gemini",
            args: [
              "-m", "gemini-3-flash",
              "--allowed-tools", "read_file",
              "Analyze this video thoroughly. Extract: topic, key steps, code examples, and technical takeaways. Output in Chinese. Limit to {{MaxChars}} chars.",
            ],
            maxChars: 800,
          },
        ],
      },
      audio: {
        enabled: true,
        models: [
          // whisper-cpp 本地转录
          {
            type: "cli",
            command: "whisper-cpp",
            args: ["-m", "$WHISPER_CPP_MODEL", "-f", "{{MediaPath}}", "-o", "{{OutputDir}}"],
            capabilities: ["audio"],
          },
          // 或 Python whisper
          {
            type: "cli",
            command: "whisper",
            args: ["--model", "large-v3", "--language", "zh", "{{MediaPath}}", "--output_format", "txt"],
          },
        ],
      },
    },
  },
}
```

---

## 五、videos_understand 工具详解

### 5.1 基础用法

```python
videos_understand(videos_info=[
  {
    "file": "/workspace/demo.mp4",
    "prompt": "分析视频内容，提取关键步骤和技术要点"
  },
  {
    "url": "https://example.com/video.mp4",
    "prompt": "What are the main topics and code examples in this tutorial?"
  }
])
```

### 5.2 技术教程专用 Prompt 模板

**模板A：步骤提取型**
```
请作为技术教程分析师，提取这个视频的：
1. 【主题】视频主要讲解什么问题/技术
2. 【前置知识】学习前需要什么基础
3. 【核心步骤】按时间顺序列出关键操作步骤
4. 【代码片段】提取所有出现的代码（标注时间戳）
5. 【知识点总结】用结构化方式总结关键概念
6. 【实战建议】给观众的学习建议
```

**模板B：项目评估型**
```
作为技术选型分析师，请评估这个开源项目演示视频：
1. 项目名称、技术定位、解决的问题
2. 核心技术栈和架构设计
3. 演示的功能优先级
4. 与同类方案相比的优缺点
5. 适用场景和局限性
6. 学习价值评估（1-10分）及理由
```

### 5.3 处理结果后处理

```python
# 结构化输出处理示例
result = videos_understand(videos_info=[...])
# result 类型：包含 content: str 的对象
# content 为模型输出的文本内容

# 提取时间戳相关代码
import re
code_blocks = re.findall(r'(\d{2}:\d{2}:\d{2})\n```[\s\S]*?```', result.content)

# 提取关键步骤
steps = re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|$)', result.content)
```

---

## 六、帧提取 Skill 详解

OpenClaw 内置 `video-frames` Skill，基于 FFmpeg 提取关键帧。

### 6.1 工具脚本

```bash
# 提取第一帧
{baseDir}/scripts/frame.sh /path/video.mp4 --out /tmp/frame.jpg

# 提取指定时间戳帧
{baseDir}/scripts/frame.sh /path/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg

# 批量提取（每秒1帧）
ffmpeg -i input.mp4 -vf "fps=1" frames/%04d.png

# 按场景变化提取关键帧（更智能）
ffmpeg -i input.mp4 -vf "select='eq(pict_type,PICT_TYPE_I)',showinfo" -fps_mode vcopy keyframes_%04d.png
```

### 6.2 帧提取 + images_understand 组合

```python
# 1. 提取关键帧
exec("ffmpeg -i demo.mp4 -vf \"fps=1/30\" -q:v 2 frames/%04d.jpg")

# 2. 批量理解帧
images_understand(image_info=[
  {"file": "frames/0001.jpg", "prompt": "这是什么内容？"},
  {"file": "frames/0002.jpg", "prompt": "这是什么内容？"},
  # ... 可同时处理最多20张
])
```

### 6.3 智能帧选择策略

| 策略 | 命令 | 适用场景 |
|------|------|---------|
| 固定间隔 | `fps=1` 或 `fps=1/60` | 均匀覆盖的教程视频 |
| 场景检测 | `select='scenecd'"` | 变化明显的内容 |
| 关键帧 | `select='eq(pict_type,PICT_TYPE_I)'` | 代码演示、PPT类视频 |
| 黑帧跳过 | `blackref=` + `skip_frame` | 含过渡动画的视频 |
| 自定义时间点 | `--time 00:05:30` | 已知关键时间点 |

---

## 七、完整 Pipeline 示例

### 场景：深度解析一个技术教程视频

```python
# === 阶段1：获取视频 ===
video_url = "https://www.bilibili.com/video/BVxxxxxxx"
exec(f"yt-dlp -o 'tutorial.mp4' '{video_url}'")

# === 阶段2：提取字幕 ===
exec("ffmpeg -i tutorial.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3")
exec("whisper audio.mp3 --model medium --language zh --output_format txt --output_dir .")
transcript = read("audio.txt")

# === 阶段3：视频理解 ===
video_result = videos_understand(videos_info=[{
  "file": "tutorial.mp4",
  "prompt": """详细分析这个技术教程视频：
  1. 主题与背景
  2. 关键步骤（带时间戳）
  3. 代码示例
  4. 知识点总结
  5. 学习建议"""
}])

# === 阶段4：帧提取 + 图像理解 ===
exec("ffmpeg -i tutorial.mp4 -vf \"select='eq(pict_type,PICT_TYPE_I)',select='not(n+1)',showinfo\" -fps_mode vcopy keyframes_%04d.png")
keyframes = exec("ls keyframes_*.png")

image_result = images_understand(image_info=[
  {"file": f, "prompt": "识别这段代码/界面内容，提取关键信息"} 
  for f in keyframes
])

# === 阶段5：整合输出 ===
final_report = f"""
# 技术教程深度解析报告

## 视频理解摘要
{video_result.content}

## 字幕全文
{transcript}

## 关键帧内容
{image_result}
"""
write("report.md", final_report)
```

---

## 八、避坑指南

### 坑1：视频文件过大被跳过
**现象**：视频上传后无理解结果
**原因**：`maxBytes` 限制，默认50MB
**解决**：
```json5
{ "video": { "maxBytes": 104857600 } }  // 放宽到100MB
```
或使用 FFmpeg 压缩：
```bash
ffmpeg -i input.mp4 -vcodec libx264 -crf 26 -preset fast output.mp4
```

### 坑2：中文内容识别不准确
**现象**：视频理解输出英文或中文乱码
**解决**：在 prompt 开头明确指定语言 + 在 config 中设置 `language: "zh"`
```json5
{ "video": { "models": [{ "prompt": "请用中文回答...", "language": "zh" }] } }
```

### 坑3：Provider Key 耗尽导致无 fallback
**现象**：Gemini API 返回 auth 错误
**解决**：配置 CLI fallback 作为兜底
```json5
{
  "video": {
    "models": [
      { "provider": "google", "model": "gemini-3-flash-preview" },
      { "type": "cli", "command": "gemini", "args": ["-m", "gemini-3-flash", ...] }
    ]
  }
}
```

### 坑4：长视频理解质量下降
**现象**：1小时以上视频只总结部分内容
**解决**：
1. 使用 FFmpeg 切割分段处理：
```bash
ffmpeg -i long.mp4 -f segment -segment_time 900 -c copy part_%03d.mp4
```
2. 使用 Qwen2.5-VL（支持最长1小时视频）

### 坑5：音频转录乱码/无输出
**现象**：Whisper 转录结果为空或乱码
**解决**：
```bash
# 检查音频流
ffprobe -v quiet -print_format json -show_streams input.mp4 | jq '.streams[] | select(.codec_type=="audio")'

# 转换格式后重试
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav
whisper output.wav --model medium --language zh
```

---

## 九、最佳实践总结

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 快速理解（<5分钟） | `videos_understand` 单次调用 | 一行代码完成 |
| 高质量理解（技术教程） | `videos_understand` + 精调 Prompt | 深度分析 |
| 中文长视频（>30分钟） | FFmpeg切割 + Qwen2.5-VL | 中文精准度更高 |
| 完整文字稿需求 | yt-dlp下载 + Whisper转录 + LLM总结 | 保留全部细节 |
| 隐私敏感场景 | 纯本地方案（Gemini CLI + whisper-cpp） | 数据不出本地 |
| 代码密集型视频 | FFmpeg关键帧提取 + images_understand | 代码OCR更清晰 |
| 多视频批量分析 | `videos_understand` 批量（≤10）+ 循环 | 并行高效 |

---

## 参考链接

- OpenClaw Media Understanding 文档：https://docs.openclaw.ai/nodes/media-understanding
- video-frames Skill：`/app/openclaw/skills/video-frames/SKILL.md`
- Gemini CLI：https://docs.google.com/generative-aiai/documentation
- Whisper：https://github.com/openai/whisper
- Qwen2.5-VL：https://www.modelscope.cn/models/Qwen/Qwen2.5-VL

---

*更新时间：2026-03-22*
