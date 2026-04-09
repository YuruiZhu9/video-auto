# 视频解析全链路自动化 — GitHub Actions Pipeline

> 🤖 Agent：视频解析方法总结Agent（小M）
> 📅 创建时间：2026-04-09
> 📁 路径：`/workspace/reports/video-parser/通用工具/`

---

## 一、方案概述

利用 GitHub Actions + OpenClaw 构建"视频URL → 自动解析 → 结构化输出 → 钉钉推送"全链路自动化。无需人工介入，定时或触发式执行。

**典型应用场景**：
- 订阅的 B站/YouTube UP主发布新视频后自动解析摘要
- 技术教程发布后自动归档到知识库
- 每日行业分享视频批量解析

---

## 二、核心工具/API

| 工具 | 作用 |
|------|------|
| **GitHub Actions** | 调度层，支持 Cron 定时 + webhook 触发 |
| **yt-dlp** | 视频下载/字幕提取，支持 B站/YouTube 等1000+平台 |
| **FFmpeg** | 音频提取、截帧、格式转换 |
| **OpenAI Whisper（API / 本地）** | 音频转文字 |
| **OpenClaw Agent** | 视频结构化理解 + 钉钉推送 |
| **GitHub Secrets** | 安全存储 API Key（OPENAI_API_KEY、DINGTALK_WEBHOOK 等） |
| **GitHub Artifacts** | 解析结果存档 |

---

## 三、Pipeline 架构图

```
触发条件（任选）
├─ Cron: 0 9 * * *（每天早9点）
├─ Repository Dispatch（手动触发）
└─ Webhook（GitHub API / IFTTT 触发）

↓

GitHub Actions Runner（ubuntu-latest）
  │
  ├─ Step 1: 读取视频列表
  │    └─ video-list.csv 或 issue body
  │
  ├─ Step 2: yt-dlp 下载视频 + 字幕
  │    └─ youtube.com → video.mp4 + subtitles.vtt
  │
  ├─ Step 3: FFmpeg 提取音频
  │    └─ video.mp4 → audio.mp3
  │
  ├─ Step 4: Whisper 转录（本地 whisper.cpp 或 API）
  │    └─ audio.mp3 → transcript.json
  │
  ├─ Step 5: OpenClaw Agent 结构化理解
  │    └─ transcript.json + frames → structured-notes.md
  │
  ├─ Step 6: 生成 GitHub Pages 或存档为 Artifacts
  │    └─ structured-notes.md → GitHub Pages 静态站点
  │
  └─ Step 7: 钉钉通知
       └─ Webhook → 摘要卡片消息
```

---

## 四、GitHub Actions Workflow 配置

### 4.1 基础配置 `.github/workflows/video-parse.yml`

```yaml
name: Video Auto-Parse Pipeline

on:
  # 定时触发（每天北京时间9点）
  schedule:
    - cron: '0 1 * * *'  # UTC 1:00 = 北京 9:00
  
  # 手动触发（repository_dispatch）
  repository_dispatch:
    types: [video-parse-trigger]
  
  # 代码推送触发（用于测试）
  push:
    branches: [main]
    paths:
      - 'video-list.csv'
      - '.github/workflows/video-parse.yml'

jobs:
  video-parse:
    runs-on: ubuntu-latest
    timeout-minutes: 120
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install yt-dlp openai python-dotenv
          # 安装 FFmpeg
          sudo apt-get update && sudo apt-get install -y ffmpeg
          # 安装 whisper.cpp（本地转录，零API成本）
          git clone https://github.com/ggerganov/whisper.cpp
          cd whisper.cpp && bash models/download.sh base.en
          cd .. && make -C whisper.cpp

      - name: Read video list
        run: python parse_video_list.py

      - name: Download & transcribe videos
        run: python scripts/batch_transcribe.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Extract key frames
        run: python scripts/extract_frames.py

      - name: OpenClaw agent structured analysis
        run: |
          curl -X POST http://localhost:8080/api/agent/run \
            -H "Authorization: Bearer ${{ secrets.OPENCLAW_API_KEY }}" \
            -d '{"task": "分析 /workspace/videos/ 目录下的视频，生成结构化笔记"}'
        # 注：需要自建 OpenClaw API 服务端点

      - name: Generate structured notes
        run: python scripts/generate_notes.py

      - name: Archive results
        uses: actions/upload-artifact@v4
        with:
          name: video-parse-results-${{ github.run_number }}
          path: output/

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output/pages
          publish_branch: gh-pages

      - name: Send DingTalk notification
        run: python scripts/dingtalk_notify.py
        env:
          DINGTALK_WEBHOOK: ${{ secrets.DINGTALK_WEBHOOK }}
```

### 4.2 视频列表读取 `parse_video_list.py`

```python
#!/usr/bin/env python3
"""读取待解析视频列表"""
import csv, os
from pathlib import Path

VIDEO_LIST_FILE = "video-list.csv"
OUTPUT_DIR = Path("output/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def read_video_list() -> list[dict]:
    """从 CSV 读取视频列表"""
    videos = []
    if not Path(VIDEO_LIST_FILE).exists():
        print(f"⚠️ {VIDEO_LIST_FILE} 不存在，创建空列表")
        return videos
    
    with open(VIDEO_LIST_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status', '').strip() != 'done':
                videos.append({
                    "url": row['url'].strip(),
                    "title": row.get('title', 'Untitled'),
                    "tags": row.get('tags', '').split(','),
                    "platform": detect_platform(row['url']),
                })
    return videos

def detect_platform(url: str) -> str:
    if 'bilibili.com' in url or 'b23.tv' in url:
        return 'bilibili'
    elif 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'xiaohongshu.com' in url:
        return 'xiaohongshu'
    return 'unknown'

if __name__ == "__main__":
    videos = read_video_list()
    print(f"📋 待解析视频数量: {len(videos)}")
    for v in videos:
        print(f"  - [{v['platform']}] {v['title']}: {v['url']}")
```

### 4.3 批量转录 `batch_transcribe.py`

```python
#!/usr/bin/env python3
"""批量下载视频并转录"""
import subprocess, json, time
from pathlib import Path
from parse_video_list import read_video_list

OUTPUT = Path("output/videos")
OUTPUT.mkdir(parents=True, exist_ok=True)

def download_and_transcribe(video: dict, index: int):
    video_dir = OUTPUT / f"video_{index:03d}"
    video_dir.mkdir(exist_ok=True)
    
    # Step 1: yt-dlp 下载（优先提取字幕和音频）
    url = video['url']
    print(f"📥 下载中 [{index}]: {url}")
    
    subprocess.run([
        "yt-dlp",
        "--output", str(video_dir / "video.%(ext)s"),
        "--write-auto-subs",          # 自动字幕
        "--write-subs",                # 手写字幕
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--no-playlist",
        url
    ], check=True)
    
    # Step 2: Whisper 转录（优先本地 whisper.cpp）
    mp3_files = list(video_dir.glob("*.mp3"))
    if not mp3_files:
        print(f"⚠️ 无音频文件，跳过: {url}")
        return None
    
    mp3_path = mp3_files[0]
    transcript_path = video_dir / "transcript.json"
    
    print(f"🎙️ 转录中: {mp3_path.name}")
    
    # 优先使用本地 whisper.cpp（零成本）
    try:
        result = subprocess.run([
            "./whisper.cpp/main",
            "-m", "whisper.cpp/models/ggml-base.en.bin",
            "-f", str(mp3_path),
            "--output-json",
            "-of", str(video_dir / "whisper_output")
        ], capture_output=True, text=True, timeout=600)
        
        # 读取 whisper.cpp 输出
        if (video_dir / "whisper_output.json").exists():
            return json.loads((video_dir / "whisper_output.json").read_text())
    except Exception as e:
        print(f"⚠️ whisper.cpp 失败，切换到 OpenAI API: {e}")
    
    # Fallback: OpenAI Whisper API
    import openai
    with open(mp3_path, "rb") as f:
        transcript = openai.Audio.transcribe(
            "whisper-1", f,
            response_format="verbose_json"
        )
    
    result = {
        "text": transcript["text"],
        "segments": transcript.get("segments", [])
    }
    transcript_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == "__main__":
    videos = read_video_list()
    results = []
    for i, video in enumerate(videos):
        try:
            result = download_and_transcribe(video, i)
            results.append({"video": video, "result": result, "status": "success"})
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            results.append({"video": video, "status": "error", "error": str(e)})
        time.sleep(2)  # 避免触发平台限流
    
    # 保存汇总结果
    Path("output/batch_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2)
    )
```

### 4.4 钉钉通知 `dingtalk_notify.py`

```python
#!/usr/bin/env python3
"""发送钉钉通知卡片"""
import os, json, requests
from pathlib import Path

WEBHOOK = os.environ.get("DINGTALK_WEBHOOK")
ARTIFACT_URL = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"

def send_dingtalk(results: list):
    """发送富文本消息卡片"""
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = len(results) - success_count
    
    # 构建 Markdown 内容
    content = f"""## 🎬 视频解析完成报告
**执行时间**: {os.environ.get('GITHUB_RUN_NUMBER', 'N/A')} 次运行
**成功**: {success_count} 部 ✅
**失败**: {failed_count} 部 ❌

### 成功解析
"""
    for r in results:
        if r['status'] == 'success':
            title = r['video'].get('title', '未知标题')
            url = r['video']['url']
            content += f"- [{title}]({url})\n"
    
    if failed_count > 0:
        content += f"\n### 失败列表\n"
        for r in results:
            if r['status'] != 'success':
                content += f"- {r['video']['url']}: {r.get('error', '未知错误')}\n"
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "🎬 视频解析完成",
            "text": content + f"\n\n[📦 查看完整结果]({ARTIFACT_URL})"
        }
    }
    
    response = requests.post(WEBHOOK, json=payload, timeout=10)
    if response.status_code == 200:
        print("✅ 钉钉通知已发送")
    else:
        print(f"❌ 钉钉通知失败: {response.text}")

if __name__ == "__main__":
    results_path = Path("output/batch_results.json")
    if results_path.exists():
        results = json.loads(results_path.read_text())
        send_dingtalk(results)
```

---

## 五、视频列表格式 `video-list.csv`

```csv
url,title,tags,priority,status
https://www.bilibili.com/video/BV1xxx,推荐系统架构详解,AI-推荐系统-架构,high,
https://www.youtube.com/watch?v=xxx,LLM最新进展2026,大模型-AI,medium,
https://www.bilibili.com/video/BV1yyy,Python异步编程教程,Python-后端,low,
```

---

## 六、触发方式详解

| 触发方式 | 配置 | 适用场景 |
|---------|------|---------|
| **Cron 定时** | `schedule: cron` | 每日/每周固定时间自动执行 |
| **手动触发** | `repository_dispatch` | 有新视频时手动启动 |
| **GitHub API** | `curl -X POST` | 外部系统（IFTTT/Zapier）集成 |
| **Issue 触发** | `/parse` 命令 | 用户在 Issue 中提交视频 URL |
| **Watch 仓库** | GitHub Actions Event | Star/Fork 时触发（适合开源工具） |

**Issue 触发示例**：
```yaml
on:
  issue_comment:
    types: [created]
jobs:
  parse:
    if: contains(github.event.comment.body, '/parse')
    steps:
      - name: Extract URL from issue
        run: |
          COMMENT_BODY="${{ github.event.comment.body }}"
          VIDEO_URL=$(echo "$COMMENT_BODY" | grep -oE 'https?://[^ ]+' | head -1)
          echo "VIDEO_URL=$VIDEO_URL" >> $GITHUB_ENV
```

---

## 七、避坑指南

| 问题 | 解决方案 |
|------|---------|
| GitHub Actions 时长限制（6小时） | 设置 `timeout-minutes: 120`，超长视频拆分为多个 Job |
| B站登录限制（bv号需 cookies） | 使用 `--cookies-from-browser chrome` 或 cookies.txt |
| Whisper API 费用 | 优先 whisper.cpp 本地转录，API 作为 Fallback |
| GitHub Secrets 额度 | 免费版 100 条；优先用 GitHub Artifacts 而非 Secrets 存储 |
| 钉钉 Webhook 过期 | 使用钉钉机器人的 "加签" 方式代替签名密钥 |
| 视频下载被限流 | yt-dlp 添加 `--sleep-requests 3` 延迟 |
| Actions 触发频率限制 | Cron 最小间隔 5 分钟；repository_dispatch 无限制 |

---

## 八、成本估算（月度）

| 项目 | 免费额度 | 超出费用 |
|------|---------|---------|
| GitHub Actions | 2000分钟/月（free） | $0.008/分钟 |
| OpenAI Whisper API | $0.006/分钟 | 按量 |
| whisper.cpp 本地 | **完全免费** | — |
| yt-dlp 下载 | 免费 | — |
| GitHub Artifacts | 500MB | $0.025/GB |

> 💡 **建议**：优先 whisper.cpp 本地转录（零成本），OpenAI Whisper API 仅作备用。

---

*本文档由视频解析方法总结Agent 自动生成 — 2026-04-09*
