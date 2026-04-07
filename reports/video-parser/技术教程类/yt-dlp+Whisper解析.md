# 技术教程类 — yt-dlp + Whisper 完整解析

## 核心工具/API

- **`yt-dlp`**（已安装于 `/app/.venv/bin/yt-dlp`，版本 2024.12.23）：支持 1800+ 站点，提取视频/音频/字幕。
- **`whisper` CLI**（本地，无需 API Key）：OpenAI 开源模型，支持 99 种语言，按需下载模型。
- **`ffmpeg`**：视频抽帧、音频切片、时间戳切分。
- **OpenAI Whisper API**（可选，需 `OPENAI_API_KEY`）：云端转写，精度更高，速度更快。

## 步骤流程

```
阶段一：下载
  ① 下载最佳画质+音频
     yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" URL

  ② 仅下载音频（速度更快，体积更小）
     yt-dlp -x --audio-format m4a --audio-quality 0 URL

  ③ 下载字幕（YouTube自动字幕）
     yt-dlp --write-subs --write-auto-subs --sub-lang zh-Hans,en URL

阶段二：转写
  ① 本地 Whisper（推荐 medium 模型，精度/速度平衡）
     whisper audio.m4a \
       --model medium \
       --language Chinese,English \
       --output_format srt \
       --output_dir ./transcripts/

  ② OpenAI API 转写（精度更高，适合专业内容）
     curl -X POST https://api.openai.com/v1/audio/transcriptions \
       -H "Authorization: Bearer $OPENAI_API_KEY" \
       -F "file=@audio.m4a" \
       -F "model=whisper-1" \
       -F "response_format=srt"

阶段三：结构化提取
  videos_understand 工具：
    prompt="请作为技术教程分析专家，提取：
    1. 视频主题与目标受众
    2. 核心知识点（按出现顺序）
    3. 所有代码/命令片段（含行号）
    4. 演示操作的关键时间节点
    5. 常见错误与解决方案
    6. 后续学习资源推荐"

阶段四：输出文档
  - 时间戳导航（基于SRT时间轴）
  - Markdown 格式结构化笔记
  - 代码块 + 注释
```

## 适用场景

- 需要**完整逐字稿**的技术视频（代码演示类）
- 多语言教程（中英双语内容）
- 需要生成**带时间戳的学习笔记**
- YouTube / Bilibili / Vimeo / 自建站点的视频

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| `yt-dlp` 下载 Bilibili 需要登录 | 添加 Cookie：`--cookies-from-browser chrome`，或手动导出 Cookie |
| Whisper 转写中文效果差 | 明确指定 `--language Chinese`；或用 `large-v3` 模型 |
| 视频时长超过2小时内存不足 | 使用 `whisper audio.m4a --split-on-word`，或先切分音频 |
| 字幕乱码 | yt-dlp 加 `--convert-subs srt --embed-subs` |
| API 转写超时 | 视频>25MB需分片：`ffmpeg -i video.mp4 -ss 0 -t 600 part1.mp4` |
| 免费API额度耗尽 | 优先使用本地 whisper CLI；或申请 OpenAI $5 额度 |

## 模型选择参考

| 模型 | 参数量 | 速度(CPU) | 精度 | 推荐场景 |
|------|--------|-----------|------|----------|
| tiny | 39M | 10x realtime | ★★★ | 快速预览 |
| base | 74M | 7x realtime | ★★★★ | 一般精度需求 |
| small | 244M | 2.5x realtime | ★★★★☆ | 平衡之选 |
| medium | 769M | < realtime | ★★★★★ | 高精度需求 |
| large-v3 | 1550M | 很慢 | ★★★★★ | 最佳精度 |

---

*推荐配置：教程视频用 `small`；重要内容深度解析用 `medium`*
