# 技术教程类 - OpenClaw 内置工具解析

## 核心工具/API

- **videos_understand**：OpenClaw 内置多模态视频理解工具，支持视频文件或 URL，直接输出文字描述和分析结果
- **audios_understand**：音频内容理解工具，适合从视频中提取纯音频后的深度分析
- **exec**：命令行工具，可调用 FFmpeg / yt-dlp / Whisper 等外部程序完成预处理
- **browser**：浏览器控制工具，适合抓取嵌在网页中的视频元信息（标题、描述、标签）

---

## 步骤流程

### 方案 A：纯内置工具（videos_understand）

1. **获取视频文件或 URL**
   - 若视频在本地，直接传入文件路径
   - 若视频在线，使用 `browser` 打开目标页面，复制视频 URL

2. **调用 videos_understand**
   ```python
   videos_understand(videos_info=[{
       "file": "/path/to/video.mp4",      # 本地路径
       # 或 "url": "https://example.com/video.mp4",
       "prompt": "请详细分析这个技术教程视频，提取：1) 主题 2) 关键知识点 3) 代码示例 4) 操作步骤（带时间戳）"
   }])
   ```

3. **后处理**
   - 整理输出为 Markdown 格式
   - 提取关键代码片段和命令
   - 按时间戳排列步骤

### 方案 B：预处理 + 内置工具（yt-dlp + videos_understand）

适用：在线视频（B站、YouTube等），需要下载后分析

1. `exec` 调用 yt-dlp 下载视频
   ```bash
   yt-dlp -o "%(title)s.%(ext)s" "https://www.bilibili.com/video/BVxxxx"
   ```
2. 调用 `videos_understand` 分析本地文件
3. 结合 yt-dlp 提取的字幕文件（--write-subs）进行补充

---

## 适用场景

- 技术教程类视频（编程教学、软件安装、工具使用）
- 学术讲座视频（论文解读、方法论讲解）
- 步骤演示视频（需提取精确操作步骤）
- 含有大量代码或命令行演示的视频

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 视频时长过长，分析超时 | videos_understand 对超长视频有限制 | 先用 FFmpeg 按章节分段，再分别分析 |
| 视频含水印，影响识别 | B站/YouTube下载默认带水印 | 用 yt-dlp --embed-thumbnail --no-watermark 参数，或下载高画质版本 |
| 代码片段截断 | 视频中代码一闪而过 | 降低播放速度截图：用 FFmpeg 慢放 0.5x 再分析 |
| 多人说话识别混乱 | 音频质量差 | 用 Whisper 预提取字幕辅助判断 |
| 内置模型不认识特定术语 | 垂直领域词汇 | 在 prompt 中提供术语表，或改用专业模型 |

---

## 参考链接

- OpenClaw 文档 - 媒体理解：https://docs.openclaw.ai/zh-CN/nodes/media-understanding
- videos_understand 工具说明：（内置于 OpenClaw）
