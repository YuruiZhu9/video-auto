# 开源项目演示类 — 视频解析与 README 提取方案

## 核心工具/API

- **GitHub CLI（gh）**：直接获取开源项目 README、Release Notes、代码仓库信息
- **yt-dlp**：下载 GitHub 项目演示视频（如 README 视频、GitHub Actions 演示）
- **Whisper**：将演示视频语音转文字，提取操作步骤和命令行
- **summarize**：一键总结 YouTube/GitHub Release 视频
- **ffmpeg**：截取演示视频关键帧，生成 GIF 动图用于 README

## 步骤流程

### 完整工作流：README → 视频下载 → 解析 → 更新文档

```
# Step 1: 获取项目 README
gh repo view owner/repo --json readme,description,url

# Step 2: 查找演示视频（YouTube/GitHub releases）
gh release list --repo owner/repo
# 或直接搜索：gh search repos "demo video" in:readme

# Step 3: 下载演示视频
yt-dlp "https://youtu.be/DEMO_VIDEO_ID" -o "demo.mp4"

# Step 4: 提取关键帧生成 GIF
ffmpeg -i demo.mp4 -vf "fps=1/10,scale=800:-1" \
       -loop 0 demo_preview.gif

# Step 5: 语音转写提取操作命令
ffmpeg -i demo.mp4 -vn -acodec libmp3lame demo_audio.mp3
whisper demo_audio.mp3 --model turbo --output_format txt

# Step 6: 整理成文档（README 更新素材）
```

### 快速方法：summarize 直接总结演示

```bash
# 直接总结演示视频
summarize "https://youtu.be/DEMO_VIDEO_ID" \
  --model google/gemini-3-flash-preview \
  --length medium

# 提取完整字幕（用于提取命令行和步骤）
summarize "https://youtu.be/DEMO_VIDEO_ID" \
  --youtube auto --extract-only -o demo_transcript.txt
```

## 适用场景

- GitHub 开源项目 README 演示视频（如 AutoGPT、LangChain 等热门项目）
- 技术产品 Demo（Vercel、Railway、Supabase 等平台的使用演示）
- CLI 工具操作演示（如 kubectl、docker、git 等命令教程）
- GitHub Actions / CI-CD 流水线演示
- 开源 AI 项目的论文解读视频（如 LLaMA、Stable Diffusion 发布视频）

## 避坑指南

- **视频水印**：部分 GitHub 演示视频有第三方水印，截帧时注意裁剪
- **命令时效性**：演示视频中的命令可能已过时（版本号、参数变化），需对照最新文档
- **字幕质量**：GitHub 项目演示视频往往没有字幕，Whisper 识别准确率依赖音频质量
- **权限问题**：部分私有仓库视频需登录下载，使用 `gh auth login` 认证
- **GIF 文件大小**：README GIF 建议压缩到 5MB 以内，用 `ffmpeg -r 10` 降低帧率

## 参考链接

- GitHub CLI：https://cli.github.com
- yt-dlp GitHub：https://github.com/yt-dlp/yt-dlp
- GitHub 项目视频资源：https://github.com/readme-ffmpeg（README 动画生成工具）
