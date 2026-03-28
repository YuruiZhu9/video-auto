# 2026-03-29 视频项目

> 生成日期：2026-03-29
> 状态：视频片段已就绪，TTS音频已生成

---

## 目录结构

```
2026-03-29/
├── slides/         # 9个幻灯片视频片段（slide01~09.mp4）
├── audio/          # TTS配音音频（tts.mp3）
├── combined/       # 合并后的完整视频（待生成）
├── thumbnails/     # 缩略图（slides_grid.png）
├── raw/            # 原始截图（预留）
└── README.md       # 本文件
```

---

## 视频片段说明

| 文件 | 描述 | 备注 |
|------|------|------|
| slide01.mp4 | 第1张幻灯片 |  |
| slide02.mp4 | 第2张幻灯片 |  |
| slide03.mp4 | 第3张幻灯片 |  |
| slide04.mp4 | 第4张幻灯片 |  |
| slide05.mp4 | 第5张幻灯片 |  |
| slide06.mp4 | 第6张幻灯片 |  |
| slide07.mp4 | 第7张幻灯片 |  |
| slide08.mp4 | 第8张幻灯片 |  |
| slide09.mp4 | 第9张幻灯片 |  |

---

## 视频合并方案

### ✅ 方案一：HTML 播放列表（推荐，立即可用）

使用 `video_player.html` 在浏览器中自动连续播放所有片段：

```bash
# 浏览器打开 video_player.html 即可
open video_player.html
```

特点：
- 无需 ffmpeg，直接在浏览器中播放
- 自动按顺序播放 9 个片段
- 支持全屏、进度条、音量控制
- TTS 音频可作为背景音（需手动同步）

### ⚙️ 方案二：Python MP4 拼接（实验性）

使用 `combine_videos.py` Python 脚本尝试拼接：

```bash
python3 combine_videos.py
```

要求：需要 `av`（PyAV）库：`pip install av`

原理：
1. 使用 PyAV 逐个读取视频片段
2. 将每帧写入输出文件
3. 重新编码为单一 MP4

### 🔧 方案三：ffmpeg 命令行（需要安装 ffmpeg）

```bash
# 安装 ffmpeg
apt install ffmpeg   # Linux
brew install ffmpeg  # macOS

# 合并视频
cd slides/
ffmpeg -f concat -safe 0 -i filelist.txt -c copy ../combined/complete.mp4
```

其中 `filelist.txt` 格式：
```
file 'slide01.mp4'
file 'slide02.mp4'
...
file 'slide09.mp4'
```

### ☁️ 方案四：API 服务（需要 API Key）

使用 Hypereal AI 或 MiniMax API 进行视频合并：

```bash
# MiniMax API
curl -X POST https://api.minimax.chat/v1/video/merge \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"inputs": ["slide01.mp4", ...]}'

# Hypereal API
curl -X POST https://api.hypereal.ai/v1/video/concat \
  -H "Authorization: Bearer YOUR_KEY" \
  -F "files=@slide01.mp4" -F "files=@slide02.mp4"
```

---

## TTS 音频

- 文件：`audio/tts.mp3`
- 内容：欢迎语和视频说明
- 如需重新生成：使用 OpenClaw 内置 `tts` 工具

---

## GitHub 仓库

- 仓库：YuruiZhu9/video-auto
- 推送内容：`video/` 目录下的所有文件

---

## 下一步

1. 选择合并方案并执行
2. 如需配音：将 `tts.mp3` 与合并后视频同步
3. 上传完整视频到目标平台
