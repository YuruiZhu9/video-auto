# Video-auto 视频目录

> 视频项目主目录，按日期组织

## 目录结构

```
video/
├── 2026-03-29/          # 2026-03-29 批次视频
│   ├── slides/          # 幻灯片视频片段（9个 mp4）
│   ├── audio/            # TTS 配音音频
│   ├── combined/         # 合并后的完整视频
│   ├── thumbnails/       # 缩略图
│   ├── raw/              # 原始截图（预留）
│   ├── README.md          # 详细说明
│   ├── video_player.html  # HTML 播放列表（无需 ffmpeg）
│   └── combine_videos.py  # Python 拼接脚本（需 PyAV）
└── README.md              # 本文件
```

## 快速开始

1. **播放视频片段（无需安装任何工具）**
   ```bash
   # 在浏览器中打开 video_player.html
   open 2026-03-29/video_player.html
   ```

2. **合并视频（需要 ffmpeg 或 PyAV）**
   ```bash
   # 方式A：ffmpeg
   ffmpeg -f concat -safe 0 -i 2026-03-29/slides/filelist.txt \
     -c copy 2026-03-29/combined/complete.mp4
   
   # 方式B：Python PyAV
   pip install av
   python3 2026-03-29/combine_videos.py
   ```

3. **配音**
   - TTS 音频在 `2026-03-29/audio/tts.mp3`
   - 使用 ffmpeg 嵌入配音：
     ```bash
     ffmpeg -i combined/complete.mp4 -i audio/tts.mp3 \
       -c:v copy -c:a aac -shortest final_output.mp4
     ```

## 当前状态

| 项目 | 状态 |
|------|------|
| 视频片段（9个） | ✅ 就绪 |
| TTS 配音 | ✅ 已生成 |
| HTML 播放列表 | ✅ 已创建 |
| Python 拼接脚本 | ✅ 已创建 |
| 完整视频合并 | ⏳ 需选择方案 |
