# 技术教程类 - FFmpeg 8.0 Whisper 原生集成解析

> 更新日期：2026-04-06
> 来源：FFmpeg 官方文档 + rendi.dev

---

## 核心工具/API

- **FFmpeg 8.0**（2025年11月发布）：多媒体处理框架，内置 Whisper 音频过滤器
- **Whisper Filter**：FFmpeg 8.0 新增原生 ASR（自动语音识别）过滤器，无需独立安装 Whisper
- **GPU 加速**：支持 CUDA / Metal / Vulkan 等硬件加速
- **VAD（语音活动检测）**：内置静音检测，过滤纯音乐/背景噪音

---

## 步骤流程

### 一行命令直接出字幕

```bash
# 基础用法：从视频直接生成 SRT 字幕
ffmpeg -i input.mp4 -vf "whisper=model=medium" output.srt
```

### 完整流程（五步）

1. **确认 FFmpeg 8.0+ 版本**
   ```bash
   ffmpeg -version | head -1
   # 输出应包含 8.0 或更高
   ```

2. **下载 Whisper 模型文件**（首次使用自动下载到 `~/.cache/whisper/`）
   ```bash
   # 可手动预下载以节省首次运行时间
   whisper --model medium --output_format txt --output_dir /tmp input.mp3
   ```

3. **提取音频流**（可选，推荐用于大文件）
   ```bash
   ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
   ```

4. **执行 Whisper 转录**（多种输出格式）
   ```bash
   # 输出 SRT 字幕（带时间戳）
   ffmpeg -i audio.wav -vf "whisper=model=medium" out.srt

   # 输出 VTT 格式（Web 视频字幕）
   ffmpeg -i audio.wav -vf "whisper=model=medium:format=vtt" out.vtt

   # 输出 JSON 详细格式（含置信度）
   ffmpeg -i audio.wav -vf "whisper=model=medium:format=json" out.json

   # 指定语言（加速 + 提高准确率）
   ffmpeg -i audio.wav -vf "whisper=model=medium:language=zh" out.srt

   # GPU 加速（CUDA）
   ffmpeg -i audio.wav -vf "whisper=model=medium:device=cuda" out.srt
   ```

5. **用字幕文件精调或压制回视频**
   ```bash
   # 将字幕烧入视频
   ffmpeg -i video.mp4 -i out.srt -c:v copy -c:s mov_text output_with_subs.mp4
   ```

---

## 适用场景

- **技术教程视频**：自动生成字幕 → 时间戳对齐 → 结构化提取步骤
- **无字幕 YouTube/X/TikTok 视频**：一键生成可读字幕
- **长视频批量处理**：GPU 加速，适合 >1 小时视频
- **多语言内容**：支持 99+ 语言，中文/英文/日文均可识别
- **本地化场景**：不需要 OpenAI API Key，完全离线运行

---

## 避坑指南

### ⚠️ 坑1：FFmpeg 版本不对
**问题**：命令报错 `Filter not found: whisper`
**解决**：必须使用 FFmpeg 8.0+，确认版本号
```bash
ffmpeg -version | head -1
# 如 < 8.0，需从源码或包管理器升级
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg (或从 github.com/BtbN/FFmpeg-Builds 获取最新)
```

### ⚠️ 坑2：模型文件下载慢/失败
**问题**：首次运行下载模型卡住
**解决**：手动预先下载
```bash
# 使用 whisper CLI 单独下载
whisper --model medium --output_format txt --output_dir /tmp dummy.mp3
# 正常下载后再用 FFmpeg
```

### ⚠️ 坑3：音频声道/采样率不匹配
**问题**：Whisper filter 对音频格式有要求
**解决**：统一转为 16kHz 单声道
```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

### ⚠️ 坑4：含背景音乐的视频识别质量差
**问题**：背景音乐干扰语音识别
**解决**：先用 VAD 过滤，或提高识别模型（如 turbo → base → small）
```bash
# 在 whisper filter 中加入 VAD 参数
ffmpeg -i audio.wav -vf "whisper=model=medium:log_score_threshold=-1.0" out.srt
```

### ⚠️ 坑5：大文件内存不足
**问题**：长视频一次性加载内存爆炸
**解决**：分段处理或使用 GPU 加速版本

---

## 进阶用法：与 OpenClaw 工具链组合

### 组合1：FFmpeg 8.0 + whisper-cpp（完全本地零成本）
```bash
# 提取音频
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
# whisper-cpp 本地转录（无需 API Key）
whisper-cpp/main -m models/ggml-medium.bin -f audio.wav --output-srt
```

### 组合2：FFmpeg 提取帧 + Whisper 字幕 + videos_understand 对齐分析
```bash
# 1. 生成字幕
ffmpeg -i video.mp4 -vf "whisper=model=medium" subs.srt

# 2. 按字幕时间戳提取关键帧
# （用 Python 解析 SRT → FFmpeg 批量截帧）
ffmpeg -i video.mp4 -ss 00:05:23 -vframes 1 frame_05m23s.jpg

# 3. videos_understand 分析帧
```

---

## 参考链接

- FFmpeg Whisper Filter 文档：https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filter.html#whisper
- rendi.dev 教程：https://www.rendi.dev/post/ffmpeg-8-0-part-1-using-whisper-for-native-video-transcription-in-ffmpeg
- WebRTC.link 完整指南：https://webrtc.link/en/article/ffmpeg-whisper-speech-to-text/
