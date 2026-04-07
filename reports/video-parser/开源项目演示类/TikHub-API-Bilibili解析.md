# TikHub API — Bilibili视频结构化数据提取

> 🤖 维护：视频解析方法总结Agent  
> 📅 新增日期：2026-03-29  
> 🔗 来源：TikHub.io 官方文档 / Cloudflare安全验证（需绕过）

---

## 核心工具/API

- **TikHub API**：Bilibili官方API代理，支持BV号/BV号批量获取视频元数据
- **API端点**：`https://api.tikhub.io/api/v1/bilibili/`
- **无需登录**：支持未登录访问（部分接口需Cookie）
- **认证方式**：Bearer Token（免费注册获取）

---

## 核心API端点

| 接口 | 功能 | 返回字段 |
|------|------|----------|
| `GET /api/v1/bilibili/web/fetch_video_info` | 单个视频基本信息 | 标题、封面、播放量、点赞、时长 |
| `GET /api/v1/bilibili/web/fetch_video_parts` | 获取视频分P信息 | 分P列表、各P时长 |
| `GET /api/v1/bilibili/web/fetch_video_subtitle` | 获取字幕列表 | 字幕URL、语言 |
| `GET /api/v1/bilibili/web/fetch_user_videos` | 获取UP主所有视频 | 视频列表、发布时间 |
| `POST /api/v1/bilibili/web/batch_video_info` | 批量视频信息 | 同 fetch_video_info，支持批量 |

---

## 步骤流程

### Step 1：注册获取API Key

访问 TikHub.io 注册 → 进入Dashboard → 创建API Key（免费额度：500次/天）

### Step 2：调用示例

```bash
# 获取单个视频基本信息
curl -X GET "https://api.tikhub.io/api/v1/bilibili/web/fetch_video_info?bvid=BV1xx4y1d7xx" \
  -H "Authorization: Bearer YOUR_API_KEY"

# 获取视频字幕列表（需cookie）
curl -X GET "https://api.tikhub.io/api/v1/bilibili/web/fetch_video_subtitle?bvid=BV1xx4y1d7xx" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Cookie: SESSDATA=your_sessdata"

# 批量获取（推荐）
curl -X POST "https://api.tikhub.io/api/v1/bilibili/web/batch_video_info" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"bvids": ["BV1xx4y1d7xx", "BV1yy4y1d7yy"]}'
```

### Step 3：Python集成

```python
import requests

TIKHUB_API_KEY = "your-api-key"
BASE_URL = "https://api.tikhub.io/api/v1/bilibili/web"

headers = {
    "Authorization": f"Bearer {TIKHUB_API_KEY}",
    "Content-Type": "application/json"
}

def get_video_info(bvid: str) -> dict:
    resp = requests.get(
        f"{BASE_URL}/fetch_video_info",
        params={"bvid": bvid},
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()["data"]

def get_video_subtitle(bvid: str, cookie: str = "") -> dict:
    headers["Cookie"] = cookie
    resp = requests.get(
        f"{BASE_URL}/fetch_video_subtitle",
        params={"bvid": bvid},
        headers=headers,
        timeout=10
    )
    return resp.json().get("data", {})

# 示例：获取视频信息 + 字幕
video = get_video_info("BV1xx4y1d7xx")
subtitles = get_video_subtitle("BV1xx4y1d7xx", cookie="SESSDATA=xxx")

print(f"标题: {video['title']}")
print(f"播放量: {video['stat']['view']}")
print(f"字幕: {subtitles}")
```

### Step 4：结合Whisper做深度解析

```python
import yt_dlp

def download_and_transcribe_bilibili(bvid, cookie=""):
    # 通过TikHub获取视频直链（需登录Cookie）
    url = f"https://www.bilibili.com/video/{bvid}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'/tmp/{bvid}.%(ext)s',
        'cookiefile': cookie,  # 使用B站cookie下载高画质
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info).replace('.fmp4', '.wav')
    
    # Whisper转录
    import whisper
    model = whisper.load_model("medium")
    result = model.transcribe(audio_path, language="zh")
    
    return result["text"]
```

---

## 适用场景

- **B站视频元数据提取**：批量获取播放量、点赞、评论数等
- **UP主动态监控**：追踪指定UP主的新发布视频
- **B站视频批量归档**：自动下载 + 转录完整pipeline
- **字幕自动化获取**：无需登录获取B站视频字幕文件

---

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| 字幕API返回空（B站AI字幕需登录） | 使用Whisper转录作为fallback |
| 免费额度用尽 | 升级付费套餐或使用备用API |
| Cookie过期 | 定期更新SESSDATA，或使用TikHub登录代理 |
| Cloudflare安全验证拦截 | 使用Python requests Session保持连接 |

---

## 参考链接

- TikHub官网：https://docs.tikhub.io
- bilibili-api-python（开源PyPI库）：https://pypi.org/project/bilibili-api-python/
- 妖狐数据B站API：https://api.yaohud.cn/doc/59
