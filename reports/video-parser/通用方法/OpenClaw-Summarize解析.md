# 通用方法 - OpenClaw Summarize 解析

> 适用于：YouTube、B站、本地文件等几乎所有视频

## 核心工具/API

- **summarize CLI**：OpenClaw 官方 Skill，封装了 YouTube/B站/本地文件/URL 的摘要逻辑
- **Google Gemini Flash**：默认模型，支持多模态理解
- **Apify**：YouTube 备用抓取（需 `APIFY_API_TOKEN`）
- **Firecrawl**：网页备用抓取（需 `FIRECRAWL_API_KEY`）

## 步骤流程

1. **安装 summarize skill**
   ```bash
   # 通过 clawhub 安装
   npx clawhub@latest install summarize
   ```

2. **YouTube 视频摘要**
   ```bash
   summarize "https://youtu.be/VIDEO_ID" --youtube auto
   summarize "https://youtu.be/VIDEO_ID" --youtube auto --extract-only  # 仅提取字幕
   ```

3. **B站视频摘要**
   ```bash
   summarize "https://www.bilibili.com/video/BVxxxxxx" --youtube auto
   ```

4. **本地视频摘要**
   ```bash
   summarize "/path/to/video.mp4" --model google/gemini-3-flash-preview
   ```

5. **控制输出长度**
   ```bash
   summarize "URL" --length short    # 短摘要
   summarize "URL" --length long     # 详细摘要
   summarize "URL" --length xxl      # 超长详细
   ```

6. **JSON 格式输出**（便于程序处理）
   ```bash
   summarize "URL" --json --out /tmp/result.json
   ```

## 适用场景

- 快速了解一个视频讲了什么（不用完整观看）
- 提取视频字幕文本（用于后续分析）
- YouTube/B站 等主流平台视频
- 无需本地下载，直接输入 URL 即可

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| YouTube 字幕提取失败 | 视频无字幕或地区限制 | 加上 `--youtube auto`，启用 Apify fallback |
| B站视频解析失败 | 非公开视频或需登录 | 下载到本地再用本地模式 |
| 摘要太短/太简单 | 默认 short 长度 | 用 `--length long` 或 `--length xxl` |
| API Key 未配置 | 环境变量缺失 | 设置 `GOOGLE_API_KEY` 或其他 provider key |
| 本地视频卡住 | 文件路径有空格 | 用引号包裹路径：`"/path/with spaces/video.mp4"` |

## 参考链接

- OpenClaw Summarize Skill：https://clawhub.ai/kn70pywhgf996kpa8xj89s57yhv26/summarize
- Apify YouTube Scraper：https://apify.com/apify/youtube-scraper
