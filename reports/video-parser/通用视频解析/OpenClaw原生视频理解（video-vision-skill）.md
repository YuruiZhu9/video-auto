# 通用视频解析 - OpenClaw AI视频理解（openclaw-video-vision）

## 核心工具/API

| 工具/API | 类型 | 说明 |
|----------|------|------|
| **openclaw-video-vision** | OpenClaw Skill / NPM 包 | AI 驱动的视频理解全链路工具 |
| **yt-dlp** | 底层下载 | 快速视频下载，支持 YouTube/B站等 |
| **FFmpeg** | 底层处理 | 视频音频分离、格式转换 |
| **whisper.cpp** | 本地 ASR | 本地语音转文字，无需云端 |
| **视觉 AI（VLM）** | API 调用 | GPT-4o / Claude / Gemini 等多模态模型 |
| **Playwright** | 备选下载 | 浏览器模拟，用于 yt-dlp 失败场景 |

---

## 步骤流程

### 全自动流程（OpenClaw 对话式）

```
用户：总结这个 YouTube 视频：https://youtube.com/watch?v=xxx
        ↓
openclaw-video-vision 自动执行：
  ① yt-dlp 下载视频 / 提取字幕
  ② whisper.cpp 转录（可选，自动判断资源）
  ③ 按时间间隔采样关键帧
  ④ VLM 分析所有帧 → 生成结构化摘要（带时间戳）
        ↓
返回：带时间戳的关键内容 + 主题标签 + 摘要
```

### 手动执行流程

```bash
# 1. 安装
git clone https://github.com/maim010/openclaw-video-vision.git \
  ~/.openclaw/skills/video-vision
cd ~/.openclaw/skills/video-vision
npm install

# 2. 配置 API Key（可使用 OpenAI / Claude / Gemini 等）
export VIDEO_VISION_API_KEY="sk-..."
export VIDEO_VISION_API_URL="https://api.openai.com/v1"  # 可替换为 Claude 等

# 3. 运行
node src/index.js "https://youtube.com/watch?v=xxx"
# 或指定 B站
node src/index.js "https://bilibili.com/video/BV1xx411c7mD"
```

---

## 核心配置参数

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `VIDEO_VISION_API_KEY` | **必填** | 视觉模型 API 密钥 |
| `VIDEO_VISION_API_URL` | OpenAI 端点 | 可配置为 Claude/Gemini 等兼容端点 |
| `VIDEO_VISION_MODEL` | `gpt-4o` | 使用的视觉模型 |
| `VIDEO_VISION_MODE` | `auto` | `auto` / `ytdlp` / `browser`（自动降级） |
| `VIDEO_VISION_FRAME_INTERVAL` | `5` | 帧间隔（秒） |
| `VIDEO_VISION_MAX_FRAMES` | `20` | 每视频最大帧数 |
| `VIDEO_VISION_TRANSCRIPTION` | `auto` | `auto` / `on` / `off` |
| `VIDEO_VISION_LOW_RESOURCE` | `false` | 低资源模式（跳过转录） |
| `VIDEO_VISION_WHISPER_PATH` | `whisper-cli` | whisper.cpp 路径 |
| `VIDEO_VISION_WHISPER_MODEL` | `medium` | whisper 模型：tiny/base/small/medium/large-v3 |
| `VIDEO_VISION_PROXY` | — | 代理 URL（HTTP/HTTPS/SOCKS5） |
| `VIDEO_VISION_BROWSER` | `local` | `local` / `browserless` / `browserbase` / `steel` |

---

## 适用场景

- ✅ **YouTube/B站深度分析**：全自动解析+摘要，无需人工操作
- ✅ **长视频理解**：whisper.cpp 转录 + 视觉帧双重分析
- ✅ **多模态内容理解**：结合音频（文字稿）+ 视频（帧画面）双重输入
- ✅ **技术视频总结**：演示类视频的技术细节提取
- ✅ **需要完整控制**：完全本地自托管，无云服务依赖

---

## 避坑指南

### ⚠️ 资源要求

| 模式 | 最低要求 | 推荐 |
|------|----------|------|
| 标准模式 | 16核CPU + 16GB RAM | 开启 whisper.cpp 转录 |
| 低资源模式 | 任意配置 | 设置 `VIDEO_VISION_LOW_RESOURCE=true`，跳过转录 |

### ⚠️ B站视频下载注意

- B站部分视频需要登录 cookie 才能下载
- 解决方案：将浏览器 cookie（ Netscape 或 JSON 格式）配置到环境变量
- 参考：设置 `BROWSER_COOKIES_FILE` 指向 cookie 文件路径

### ⚠️ 模型选择建议

- **GPT-4o**：效果最好，速度快（推荐）
- **Claude Sonnet 4**：对长文本理解更好
- **Gemini 1.5 Pro**：上下文窗口大，适合超长视频

### 💡 获取最佳效果的配置

```bash
export VIDEO_VISION_API_KEY="your-key"
export VIDEO_VISION_FRAME_INTERVAL=3   # 更密集的帧
export VIDEO_VISION_MAX_FRAMES=30       # 允许更多帧
export VIDEO_VISION_TRANSCRIPTION=on    # 强制开启转录
export VIDEO_VISION_WHISPER_MODEL=medium  # 更高质量转录
```

---

## 安装命令

```bash
# 方式A：npm 安装（需要 GitHub Packages 认证）
npm install @maim010/openclaw-video-vision@latest \
  --registry=https://npm.pkg.github.com \
  --//npm.pkg.github.com/:_authToken=YOUR_GITHUB_TOKEN

# 方式B：git clone（推荐，简单）
git clone https://github.com/maim010/openclaw-video-vision.git \
  ~/.openclaw/skills/video-vision
cd ~/.openclaw/skills/video-vision
npm install

# 前置依赖
brew install ffmpeg yt-dlp          # macOS
# apt install ffmpeg yt-dlp         # Linux
```

---

## 与其他方案对比

| 能力 | openclaw-video-vision | BibiGPT | parse-video |
|------|----------------------|---------|-------------|
| 平台覆盖 | YouTube/B站/任意网页 | 30+平台 | 10+平台下载 |
| 本地运行 | ✅ 完整本地 | ❌ 云服务 | ✅ 完整本地 |
| 语音转录 | ✅ whisper.cpp | ✅ 云端AI | ❌ |
| 时间戳摘要 | ✅ AI生成 | ✅ AI生成 | ❌ |
| 视觉帧分析 | ✅ VLM | ✅ 云端AI | ❌ |
| 无水印下载 | ✅ | ❌ | ✅ |

---

## 参考链接

- GitHub：https://github.com/maim010/openclaw-video-vision
- 中文文档：https://maim010.github.io/openclaw-video-vision/zh/
- yt-dlp：https://github.com/yt-dlp/yt-dlp
- whisper.cpp：https://github.com/ggerganov/whisper.cpp
