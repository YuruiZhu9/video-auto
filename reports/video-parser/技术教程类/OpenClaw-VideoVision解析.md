# 技术教程类 - OpenClaw Video Vision 解析

## 核心工具/API

| 工具 | 作用 | 说明 |
|------|------|------|
| **yt-dlp** | 视频下载与元数据提取 | 支持 YouTube、Bilibili 等 1000+ 平台 |
| **ffmpeg** | 音视频处理与帧提取 | 从直链提取帧，或本地文件处理 |
| **Playwright-core** | 浏览器渲染截图 | 备用方案，处理 yt-dlp 不支持的网站 |
| **OpenClaw 工具链** | 视频帧分析 | 调用 LLM 对提取的帧进行理解 |

## 步骤流程

```
输入：视频URL（如 YouTube / Bilibili 链接）
         │
         ▼
┌─────────────────────────────────┐
│  阶段1：yt-dlp 提取阶段          │
│  1. yt-dlp 获取视频元数据        │
│     - 标题、时长、分辨率         │
│     - 直链（m3u8/mp4）           │
│  2. 优先用 ffmpeg + 直链提取帧    │
│     （高效，无需下载完整文件）     │
│  3. 若直链 403/失效 → 下载本地文件 │
│     → 再用 ffmpeg 提取帧          │
└────────────────┬────────────────┘
                 │ 若全部失败
                 ▼
┌─────────────────────────────────┐
│  阶段2：浏览器回退阶段            │
│  1. Playwright-core 启动 Chromium│
│  2. 打开视频页面，渲染 JS         │
│  3. 截图提取关键帧               │
└─────────────────────────────────┘
                 │
                 ▼
         LLM 帧内容理解 → 结构化输出
```

### 配置三种模式（通过环境变量）

```bash
# 模式一：自动（默认）- 优先 yt-dlp，失败后回退浏览器
export VIDEO_VISION_MODE=auto

# 模式二：仅 yt-dlp - 不使用浏览器（适合 Android/PRoot/资源受限环境）
export VIDEO_VISION_MODE=ytdlp

# 模式三：仅浏览器 - 跳过 yt-dlp（适合 yt-dlp 不支持的网站）
export VIDEO_VISION_MODE=browser
```

## 适用场景

- ✅ **OpenClaw Agent 内置使用**：集成在 OpenClaw 工具链中，直接调用
- ✅ **多平台视频**：YouTube、Bilibili、以及 yt-dlp 支持的任何平台
- ✅ **有结构化解析需求**：需要结合 LLM 对视频帧内容做理解和总结
- ✅ **无法安装浏览器环境**：Android/PRoot/Termux → 使用 `ytdlp` 模式
- ❌ **纯本地视频文件**：优先使用 FFmpeg + Whisper 更高效

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 视频直链 403 Forbidden | 平台防盗链 | 切换到 `auto` 模式，自动回退到下载本地文件再处理 |
| Bilibili 视频无法获取直链 | 需要登录 Cookie | 配置 Cookie：设置 `BILIBILI_COOKIE` 环境变量 |
| Playwright 报错无 Chromium | 未安装浏览器 | 安装 Chromium：`npx playwright install chromium` |
| 帧提取质量差 | 分辨率/帧率设置不当 | 调整 `--fps` 和 `--resolution` 参数 |
| 内存占用过高 | 同时加载多个视频 | 使用 `ytdlp` 模式减少内存开销 |

### 决策流程图

```
能否安装 playwright-core + Chromium？
├── 否
│   └── 使用 VIDEO_VISION_MODE=ytdlp
│       需要：yt-dlp + FFmpeg
│
└── 是
    ├── 目标网站被 yt-dlp 支持？（YouTube、Bilibili 等）
    │   ├── 是  → VIDEO_VISION_MODE=auto（默认）
    │   └── 否  → VIDEO_VISION_MODE=browser
    │
    └── 想要避免浏览器开销？
        └── 是  → VIDEO_VISION_MODE=ytdlp
```

## 适用视频类型

| 视频类型 | 推荐模式 | 说明 |
|---------|---------|------|
| YouTube 教程 | `auto` | yt-dlp 完美支持 |
| Bilibili 技术视频 | `auto` + Cookie | 需配置 Cookie 获取完整内容 |
| 小众平台视频 | `browser` | yt-dlp 不支持时使用浏览器 |
| 长视频（>1小时） | `ytdlp` | 减少内存，浏览器开销大 |

## 参考链接

- GitHub: https://github.com/maim010/openclaw-video-vision
- 文档（中文）: https://maim010.github.io/openclaw-video-vision/zh/
- OpenClaw Skills: https://docs.openclaw.ai/zh-CN/tools/skills
- yt-dlp 支持平台: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
