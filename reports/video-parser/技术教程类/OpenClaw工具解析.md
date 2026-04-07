# OpenClaw 视频解析工具全解析

## 核心工具/API

### 1. videos_understand - 视频内容理解（推荐）

**功能描述**：OpenClaw内置的AI视频分析工具，可以直接理解视频内容并返回文本分析结果。

**支持能力**：
- 直接分析本地视频文件（mp4, avi, mov等）
- 支持URL远程视频分析
- 最大支持10个视频并行分析
- 适用于理解视频整体内容、提取关键信息

**调用方式**：
```python
# 直接调用 videos_understand 工具
videos_understand(videos_info=[
    {"file": "/path/to/video.mp4", "prompt": "分析这个视频的主要内容"}
])
```

### 2. video-frames - 视频帧提取

**功能描述**：使用ffmpeg从视频中提取单帧或短片段。

**核心工具**：
- **ffmpeg**：视频处理核心工具
- **frame.sh 脚本**：OpenClaw提供的便捷脚本

**提取命令**：
```bash
# 提取第一帧
./frame.sh /path/to/video.mp4 --out /tmp/frame.jpg

# 指定时间戳提取
./frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

### 3. summarize - 视频/音频总结

**功能描述**：总结URL、本地文件和YouTube链接的内容，支持提取字幕和转录。

**支持能力**：
- YouTube视频自动转录和总结
- 本地视频/音频文件分析
- 支持多种LLM模型（OpenAI, Anthropic, Google, xAI）
- 可以单独提取字幕（--extract-only）

**调用命令**：
```bash
# 总结YouTube视频
summarize "https://youtu.be/xxx" --youtube auto

# 提取字幕（仅转录）
summarize "https://youtu.be/xxx" --youtube auto --extract-only

# 总结本地文件
summarize "/path/to/video.mp4" --model google/gemini-3-flash-preview
```

### 4. images_understand - 视频帧图像分析

**功能描述**：当需要更精细的视频帧分析时，可以先用video-frames提取关键帧，然后用images_understand进行深度分析。

**调用方式**：
```python
images_understand(image_info=[
    {"file": "/tmp/frame.jpg", "prompt": "详细描述这张图片中的内容"}
])
```

## 步骤流程

### 完整流程一：快速视频理解（推荐）
```
1. 准备视频文件或URL
2. 直接调用 videos_understand 工具
3. 获取AI分析结果
```

### 完整流程二：深度帧分析
```
1. 准备视频文件
2. 使用 frame.sh 提取关键帧（指定时间点）
3. 使用 images_understand 分析每帧
4. 汇总所有帧的分析结果
```

### 完整流程三：带字幕的视频总结
```
1. 获取视频URL（YouTube等）
2. 使用 summarize --extract-only 获取字幕
3. 使用 summarize 总结视频内容
4. 如需特定时间段，可结合 frame.sh 提取
```

## 适用场景

### 场景一：快速了解视频大意
- 使用 `videos_understand` 直接获取视频核心内容
- 适用于：学习笔记、会议记录、教程摘要

### 场景二：提取视频中的具体信息
- 场景：需要提取视频中的代码、图表、数据
- 方法：提取关键帧 → images_understand分析

### 场景三：获取视频字幕/文字稿
- 使用 `summarize --extract-only` 提取字幕
- 适用于：学习、外语视频、生成文字稿

### 场景四：长视频分段落理解
- 将视频分段（用ffmpeg切割）
- 逐段使用videos_understand分析
- 汇总形成完整理解

## 避坑指南

### 问题1：视频文件太大
**解决方案**：
- 视频>100MB建议先压缩或分段
- 使用 `--time` 参数只分析特定时间段
- 可以先用ffprobe查看视频信息再决定处理方式

### 问题2：视频格式不支持
**解决方案**：
- 确认视频格式（mp4, avi, mov, mkv等常见格式）
- 如需转换，使用ffmpeg：`ffmpeg -i input.avi output.mp4`

### 问题3：YouTube视频无法解析
**解决方案**：
- 检查网络连接
- 尝试使用summarize的--youtube auto参数
- 考虑使用yt-dlp下载后本地处理

### 问题4：分析结果不准确
**解决方案**：
- 优化prompt，明确指出需要提取的信息类型
- 提供更多上下文给LLM
- 对于技术内容，可以指定要关注的专业术语

### 问题5：处理速度慢
**解决方案**：
- 减少同时处理的视频数量
- 使用更短的片段
- 考虑使用更快的模型（如flash版本）

## 参考链接

- OpenClaw视频工具文档
- videos_understand 工具说明
- video-frames Skill: /app/openclaw/skills/video-frames/
- summarize Skill: /app/openclaw/skills/summarize/
