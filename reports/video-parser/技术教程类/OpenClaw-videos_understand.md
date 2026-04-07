# 技术教程类视频解析 - OpenClaw videos_understand

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| `videos_understand` | OpenClaw 内置视频理解工具，支持批量分析（最多10个视频） |
| `audios_understand` | 音频理解工具，提取音频转录和内容分析 |
| `images_understand` | 图片理解工具，提取关键帧信息 |

## 步骤流程

### 基础流程

1. **准备视频**
   - 将视频文件上传到工作区
   - 或提供可访问的公开 URL
   
2. **调用 videos_understand 工具**
   ```python
   videos_understand(videos_info=[
     {
       "file": "/path/to/video.mp4",
       "prompt": "分析这个技术教程视频的主要内容，提取关键步骤和知识点"
     }
   ])
   ```

3. **解析结果**
   - 获取结构化分析结果
   - 提取关键步骤、代码片段、知识点

4. **后处理**
   - 格式化输出为 Markdown
   - 整理为学习笔记

### 进阶：结合媒体理解配置

在 openclaw.json 中配置：

```json
{
  "tools": {
    "media": {
      "video": {
        "enabled": true,
        "maxChars": 500,
        "maxBytes": 52428800,
        "timeoutSeconds": 120
      }
    }
  }
}
```

## 适用场景

- ✅ 技术教程视频结构化
- ✅ 代码演示视频分析
- ✅ 产品功能讲解视频
- ✅ 步骤教学类视频
- ✅ 编程教学视频
- ✅ 软件使用教程

## 避坑指南

### 问题1：视频大小超限
**问题**：视频文件过大，解析失败
**解决**：
- 调整 maxBytes 配置
- 使用 FFmpeg 压缩视频
- 切割成长度较短的片段

```bash
# 压缩视频
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 output.mp4

# 切割视频（每60秒一段）
ffmpeg -i input.mp4 -acodec copy -f segment -segment_time 60 -vcodec copy output_%03d.mp4
```

### 问题2：处理超时
**问题**：视频处理时间过长
**解决**：
- 增加 timeoutSeconds 配置
- 减少视频时长
- 使用更快的模型

### 问题3：中文识别问题
**问题**：中文内容识别不准确
**解决**：
- 在 prompt 中明确指定语言
- 使用中文优化的模型

### 问题4：多视频处理
**问题**：需要同时处理多个视频
**解决**：
- videos_understand 最多支持10个视频
- 使用批量处理
- 合理分配处理顺序

## 参考链接

- OpenClaw 文档：https://docs.openclaw.ai/zh-CN/nodes/media-understanding
- videos_understand 工具说明

---

*更新时间：2026-03-14*
