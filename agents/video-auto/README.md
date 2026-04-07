# 🎬 video-auto

> 输入主题 + 原始音频 → 自动生成带配音的网页 Slide 视频，推送到 GitHub

---

## 功能

1. **声音克隆** — 5秒音频样本，克隆你的专属声音（Fish Audio，免费开源）
2. **内容扩展** — 智谱 GLM-4-Flash（免费）对原始素材深度扩展
3. **场景智能分段** — FFmpeg场景检测 + 音频停顿双轨切分，避免碎片化
4. **网页 Slide** — AI 生成精美动画 HTML 演示文稿（浏览器直接打开）
5. **视频合成** — 克隆声音 + Slide 截图 → MP4 视频（支持过渡效果）
6. **GitHub 推送** — 自动同步到本仓库

---

## 快速开始

### 手动触发任务

向 Agent 发送：

```
主题：AI推荐系统的最新进展
音频：/workspace/agents/video-auto/audio/source/my_voice.wav
文本材料：
  推荐系统是信息过滤的核心...
  [你的原始素材]
```

### 自动触发

每天 06:00 / 12:00 / 18:00 / 00:00 自动检查 `/input/` 目录是否有新任务。

将 `topic.txt` 和 `material.md` 放入 `/input/` 目录即可自动触发。

---

## 目录结构

```
video-auto/
├── input/                  # 放置待处理的任务
│   ├── topic.txt           # 主题
│   └── material.md        # 原始素材
├── audio/
│   ├── source/            # 原始音频
│   └── cloned/            # 克隆的声音
├── content/
│   └── script.md          # 扩展后的演讲稿
├── slides/
│   └── output.html        # 网页 Slide（主输出）
├── video/
│   ├── scene_detector.py  # 🎬 场景检测（FFmpeg双轨切分）
│   ├── naming_utils.py    # 📋 统一文件命名规范
│   ├── complete_pipeline.py  # 全流程流水线
│   ├── gen_slide_*.py     # HTML Slide 生成
│   ├── merge_audio_video.py  # 音视频合并
│   ├── concat_mp4.py      # MP4 拼接
│   └── {date}/            # 每日任务输出
│       ├── slides/        # 视频片段
│       ├── audio/         # TTS音频
│       └── combined/      # 合并输出
└── logs/                  # 心跳执行日志
```

---

## 技术栈

| 环节 | 方案 | 费用 |
|------|------|------|
| 声音克隆 | Fish Audio（开源）| 免费 |
| TTS 备选 | MiniMax TTS | 免费层 |
| 内容扩展 | 智谱 GLM-4-Flash | 免费 |
| 场景分段 | scene_detector.py（FFmpeg双轨切分）| 免费 |
| Slide 生成 | ppt-html-generator Skill | - |
| 视频合成 | batch_image_to_video MCP | 免费 |
| 过渡效果 | naming_utils.py 统一命名 | 免费 |
| GitHub | GitHub API | 免费 |

---

## 运行状态

- **定时心跳**：06:00 / 12:00 / 18:00 / 00:00（Asia/Shanghai）
- **最近心跳**：查看 `/logs/` 目录
