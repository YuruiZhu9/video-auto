# OpenClaw video-vision Skill — 帧提取 + Vision AI 视觉理解

## 核心工具/API

| 工具 | 功能描述 |
|------|---------|
| **yt-dlp** | 从 YouTube/Bilibili 等平台提取视频元数据和直链 |
| **Playwright (Chromium)** | 浏览器方式抓取视频（fallback 路径） |
| **FFmpeg** | 按固定间隔从视频中提取关键帧 |
| **Vision AI 模型** | 将帧图像发送给视觉模型，输出语义理解结果 |
| **代理/HTTP** | 支持 HTTP/HTTPS/SOCKS5 代理 |
| **Cookie 注入** | 支持 Netscape/JSON 格式 Cookie 文件访问需登录内容 |

---

## 步骤流程

### 完整处理流程

```
用户输入：YouTube/Bilibili 视频链接
       ↓
① yt-dlp 获取视频元数据 + 直链URL
       ↓
② FFmpeg 按 interval（默认5s）均匀采样帧
       ↓（如yt-dlp失败）
③ Playwright 浏览器回退抓取
       ↓
④ 帧图片发送至 Vision AI（gpt-4o 等 OpenAI 兼容端点）
       ↓
⑤ 结构化输出：摘要 + 时间戳关键帧描述 + 标签
```

### 帧提取控制参数

```bash
# FFmpeg 帧提取（1张/5秒，上限20张）
ffmpeg -i video.mp4 -vf "fps=1/5,scale=1280:-1" \
  -q:v 2 frames/%03d.jpg

# 长视频智能采样（均匀分布于全长）
ffmpeg -i long_video.mp4 -vf "select='not(mod(n\,300))',scale=1280:-1" \
  -vsync vfr frames/frame_%04d.jpg
```

### Vision AI 调用（OpenAI 兼容端点）

```python
import base64, requests, glob, os

VISION_API_URL = os.getenv("VIDEO_VISION_API_URL", "https://api.openai.com/v1/chat/completions")
MODEL = os.getenv("VIDEO_VISION_MODEL", "gpt-4o")
API_KEY = os.getenv("VIDEO_VISION_API_KEY")

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

frames = sorted(glob.glob("frames/*.jpg"))
messages = [{"role": "system", "content": "你是一个视频内容分析助手。"}]

for i, frame in enumerate(frames[:20]):
    ts = i * 5  # 假设5秒间隔
    img_b64 = encode_image(frame)
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": f"这是视频第 {ts} 秒的截图，描述画面内容。"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
        ]
    })

response = requests.post(VISION_API_URL + "/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"model": MODEL, "messages": messages})
print(response.json())
```

---

## 适用场景

- **产品演示类视频**：截帧分析 UI/界面/GUI 操作流程
- **PPT 型教程**：提取每张幻灯片的核心文字
- **需代理访问的内容**：Geo-blocked / Age-restricted 视频
- **登录才能观看的私有视频**：通过 Cookie 注入认证
- **无字幕视频的视觉理解**：没有语音/字幕时唯一可用方案

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| yt-dlp 无法获取直链 | 平台反爬/地区限制 | 启用 Playwright 浏览器模式 |
| 帧太多导致 API 超限 | 长视频默认每5秒一帧 | 调大 `VIDEO_VISION_FRAME_INTERVAL`，设 `VIDEO_VISION_MAX_FRAMES=20` |
| API 费用爆炸 | 大量帧发送到 Vision 模型 | 优先用 `videos_understand`（单次调用 vs 多帧多次） |
| Cookie 格式错误 | 使用了错误格式 | 必须用 Netscape 格式或 `[{name, value, domain, path}]` JSON |
| Android/PRoot 环境 | Playwright 无法运行 | 设置 `VIDEO_VISION_MODE=ytdlp` 仅用 yt-dlp+FFmpeg |
| 直播流视频 | 无法回看/缓冲有限 | 标注为"直播内容"，仅处理当前缓冲片段 |

---

## 配置示例

```json
{
  "skills": {
    "entries": {
      "video-vision": {
        "enabled": true,
        "env": {
          "VIDEO_VISION_API_KEY": "sk-...",
          "VIDEO_VISION_MODEL": "gpt-4o",
          "VIDEO_VISION_MODE": "auto",
          "VIDEO_VISION_FRAME_INTERVAL": "10",
          "VIDEO_VISION_MAX_FRAMES": "15"
        }
      }
    }
  }
}
```

---

## 输出格式示例

```
Video Summary: Build a RAG System with LangChain
Platform: YouTube | Duration: 18:42 | Frames analyzed: 18

Summary:
本视频演示了使用 LangChain 构建 RAG 系统的完整流程，
从环境配置到向量数据库集成，循序渐进。

Key Moments:
- 0:30 — 讲师介绍 RAG 架构图，PPT 显示核心组件
- 3:15 — VSCode 中初始化 LangChain 项目
- 7:40 — 终端演示 Chroma 向量数据库加载
- 12:20 — 展示检索结果和生成答案的界面
- 16:05 — 总结三个常见陷阱

Topics detected: LangChain, RAG, Vector DB, Embedding, LangSmith
```

---

## 参考链接

- GitHub: https://github.com/maim010/openclaw-video-vision
- OpenClaw Skills 文档: https://docs.openclaw.ai/zh-CN/tools/skills
- Playwright: https://playwright.dev/
- FFmpeg: https://ffmpeg.org/
- yt-dlp: https://github.com/yt-dlp/yt-dlp
