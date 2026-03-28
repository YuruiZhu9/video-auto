# Video-Auto Pipeline 优化方案

> 生成时间：2026-03-28T17:54:17.030Z

## 一、当前流水线瓶颈

### 1.1 视频合成（核心瓶颈）
- **ffmpeg 不可用**：容器环境无 root 权限，无法安装 ffmpeg
- **替代方案缺失**：当前使用 Python PIL 生成静态拼接图，无法生成视频
- **gen_videos MCP 工具限制**：可生成短视频但无法自动合成音频+视频流

### 1.2 其他瓶颈
- **Slide 生成**：HTML slide 无动画，仅静态导出 PNG
- **TTS**：当前为简化版本（未找到生成的音频文件），无法实现声音克隆
- **GitHub 推送**：手动 curl 命令，每次需手动获取 sha，无自动化

---

## 二、优化方向

### 2.1 视频合成方案（优先级 P0）
**推荐方案 A：MiniMax 视频 API**
- 申请地址：https://www.minimaxi.com/
- 支持文生视频、图生视频，适合 slide 转视频
- 免费额度：新用户赠送积分

**推荐方案 B：Hypereal AI Kling API**
- 申请地址：https://hypereal.ai/dashboard → API Keys
- Wan-2.5 模型，支持 5-10 秒视频生成
- 注册赠送 35 积分

**备选方案 C：MiniMax embedder + 本地合成**
- 将每张 slide 通过图生视频 API 生成短视频片段
- 使用 Python moviepy 或 Node.js fluent-ffmpeg（若 ffmpeg 可安装）
- 音频使用 TTS 结果，通过 Web Audio API 合成

### 2.2 Slide 生成优化（优先级 P1）
- 增加动画效果：reveal.js 支持幻灯片动画
- 固定 16:9 比例输出
- 支持多语言字幕导出（SRT/VTT）
- 生成视频时自动添加转场效果

### 2.3 TTS 升级（优先级 P1）
**推荐：Fish Audio API**
- 申请地址：https://fish.audio/
- 支持声音克隆，上传 30s 音频即可
- 免费额度：足够个人使用
- API 端点：`POST https://api.fish.audio/v1/tts`

**备选：ElevenLabs API**
- 支持高质量 TTS + 声音克隆
- 免费额度：每月 10,000 字符

### 2.4 GitHub Actions 自动构建（优先级 P2）
```yaml
# .github/workflows/build.yml
name: Auto Build
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install dependencies
        run: npm install
      - name: Generate slides
        run: node scripts/gen_slides.js
      - name: Generate TTS
        run: node scripts/gen_tts.js
      - name: Generate video
        run: node scripts/gen_video.js
      - name: Push artifacts
        run: |
          git config user.name "Video-Auto Bot"
          git config user.email "bot@video-auto.ai"
          git add -A
          git diff --staged --quiet || git commit -m "Auto build $(date)"
          git push
```

### 2.5 流水线健壮性（优先级 P2）
- **错误重试机制**：使用 axios-retry 或类似库，对 API 调用失败自动重试 3 次
- **进度通知**：Slack/钉钉 Webhook 通知各阶段完成状态
- **断点续传**：记录已完成的 slide index，失败后从断点继续
- **日志持久化**：构建日志写入 /workspace/agents/video-auto/logs/

---

## 三、下一步行动计划

| 优先级 | 任务 | 负责方 | 状态 |
|--------|------|--------|------|
| P0 | 申请 MiniMax API Key | 用户 | 待处理 |
| P0 | 测试图生视频 API | Agent | 待处理 |
| P1 | 接入 Fish Audio 声音克隆 | Agent | 待处理 |
| P1 | Slide 增加动画效果 | Agent | 待处理 |
| P2 | 配置 GitHub Actions | Agent | 待处理 |
| P2 | 增加错误重试机制 | Agent | 待处理 |

---

## 四、当前环境状态

```bash
# ffmpeg: 不可用（权限不足）
# PIL: 不可用（pip install 失败）
# Node.js sharp: 已安装（用于图片拼接）
# TTS 音频: 未找到（/tmp/openclaw/*.mp3 为空）
```

---

*本文档由 video-auto Agent 自动生成*
