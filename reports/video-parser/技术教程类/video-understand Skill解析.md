# 技术教程类 - video-understand Skill解析

> HeyGen开源 | FFmpeg + Whisper本地视频理解 | ⭐4.7/1.7K安装

## 核心工具/API

| 工具 | 功能描述 | 安装方式 |
|------|---------|---------|
| **video-understand** | HeyGen开源Skill，FFmpeg帧提取+Whisper转录 | `npx skills add heygen-com/skills --skill video-understand` |
| **FFmpeg** | 场景检测、关键帧提取、音频抽取 | `brew install ffmpeg`（Mac）/ `apt install ffmpeg`（Linux） |
| **Whisper** | OpenAI语音识别（可选，需`pip install openai-whisper`） | 自动下载模型 |
| **Python 3.8+** | 运行环境 | 系统自带 |

**Skill基础信息：**
| 指标 | 数值 |
|------|------|
| 评分 | ⭐ 4.7/5.0（65条评价） |
| 周安装量 | 241 |
| 总安装量 | 1.7K |
| GitHub星星 | ⭐ 91 |
| 创建时间 | 2026年3月23日 |
| 作者 | HeyGen |

## 步骤流程

### 步骤1：安装Skill

```bash
# 通过npx安装（推荐）
npx skills add heygen-com/skills --skill video-understand

# 验证安装
python3 skills/video-understand/scripts/understand_video.py --help
```

### 步骤2：安装前置依赖

```bash
# FFmpeg（必需）
brew install ffmpeg          # macOS
# 或
sudo apt install ffmpeg     # Ubuntu/Debian

# 验证
ffmpeg -version
ffprobe -version

# Whisper（可选，用于语音转录）
pip install openai-whisper

# 首次运行Whisper会自动下载模型
```

### 步骤3：基础使用

**场景检测 + 转录（默认模式）：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4
```

**关键帧提取模式：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4 -m keyframe
```

**固定间隔采样模式：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4 -m interval
```

**限制最大帧数：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4 --max-frames 10
```

**指定Whisper模型大小：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4 --whisper-model small
```

**仅提取帧，跳过转录（加速）：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4 --no-transcribe
```

**安静模式（仅JSON输出）：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4 -q
```

**输出到文件：**
```bash
python3 skills/video-understand/scripts/understand_video.py video.mp4 -o result.json
```

### 步骤4：CLI参数速查表

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `video`（位置参数） | 输入视频文件路径 | 必需 |
| `-m, --mode` | 提取模式 | scene/keyframe/interval |
| `--max-frames` | 最大保留帧数 | 整数（默认20） |
| `--whisper-model` | Whisper模型大小 | tiny/base/small/medium/large |
| `--no-transcribe` | 跳过音频转录 | 开关 |
| `-o, --output` | 输出JSON文件路径 | 文件路径 |
| `-q, --quiet` | 安静模式 | 开关 |

## 适用场景

- ✅ **技术教程视频**：检测PPT切换/代码演示关键帧，配合字幕做结构化笔记
- ✅ **会议/演讲录像**：自动分段，生成带时间戳的文字记录
- ✅ **开源项目Demo**：提取关键演示帧，快速了解项目内容
- ✅ **产品演示视频**：捕捉核心功能界面，生成图文摘要
- ✅ **离线环境**：无需API密钥，本地完整运行
- ✅ **隐私敏感内容**：视频不上传，数据完全本地处理

## 避坑指南

### 问题1：ffmpeg未安装
**症状：** `FileNotFoundError: ffmpeg not found`
**解决：**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# 验证
ffmpeg -version
```

### 问题2：Whisper模型下载失败
**症状：** 运行卡住或报错网络错误
**解决：**
```bash
# 设置HF镜像
export HF_ENDPOINT=https://hf-mirror.com

# 或手动预下载模型
pip install openai-whisper
python -c "import whisper; whisper.load_model('base')"
```

### 问题3：视频太长，内存不足
**症状：** 处理大视频时内存溢出
**解决：**
```bash
# 限制最大帧数
python3 .../understand_video.py video.mp4 --max-frames 5 --no-transcribe

# 先分割视频，再分批处理
ffmpeg -i long_video.mp4 -ss 00:00 -t 30:00 part1.mp4
ffmpeg -i long_video.mp4 -ss 30:00 -t 30:00 part2.mp4
```

### 问题4：场景检测模式提取帧过多/过少
**症状：** 场景变化阈值不匹配
**解决：**
```bash
# 默认0.3阈值偏高，改用interval模式
python3 .../understand_video.py video.mp4 -m interval --max-frames 20

# 或修改脚本中的scene阈值
# 找到 scene_thresh = 0.3 改为 0.5（更敏感）或 0.2（更宽松）
```

### 问题5：SRT字幕格式问题
**症状：** 生成的字幕在某些播放器无法显示
**解决：** 使用FFmpeg后处理转标准格式
```bash
# 转标准SRT
ffmpeg -i output.srt -f srt output_fixed.srt

# 或转VTT
ffmpeg -i output.srt output.vtt
```

## 三种提取模式对比

| 模式 | 工作原理 | 优点 | 缺点 | 最佳场景 |
|------|---------|------|------|---------|
| `scene`（默认） | `select='gt(scene,0.3)'`检测场景变化 | 自动聚焦内容变化点 | 对缓慢渐变不敏感 | 演讲/PPT类教程 |
| `keyframe` | 提取I帧（编码关键帧） | 提取最精确 | 密集采样，大量冗余帧 | 已压缩视频，自然关键帧 |
| `interval` | 均匀时间间隔采样 | 结果可预测，可控 | 可能错过重要瞬间 | 固定节奏/规律性内容 |

> **提示**：scene模式如检测不到变化，会自动回退到interval模式

## 输出格式详解

```json
{
  "video": "video.mp4",
  "duration": 18.076,
  "resolution": {"width": 1224, "height": 1080},
  "mode": "scene",
  "frames": [
    {
      "path": "/abs/path/frame_0001.jpg",
      "timestamp": 0.0,
      "timestamp_formatted": "00:00"
    },
    {
      "path": "/abs/path/frame_0002.jpg",
      "timestamp": 5.5,
      "timestamp_formatted": "00:05"
    }
  ],
  "frame_count": 12,
  "transcript": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello and welcome to today's tutorial..."
    }
  ],
  "text": "Full transcript combining all segments...",
  "note": "Use the Read tool to view frame images for visual understanding."
}
```

**字段说明：**
- `video`：输入视频文件名
- `duration`：视频总时长（秒）
- `resolution`：视频分辨率
- `frames`：提取的帧列表，含路径+时间戳
- `transcript`：Whisper转录段落（带时间戳）
- `text`：完整转录文本

## 效果对比

| 指标 | 手动完成 | 使用video-understand |
|------|---------|---------------------|
| 完成时间 | ~98分钟 | **~9分钟** |
| 操作复杂度 | 多工具切换 | 单命令 |
| 可重复性 | 低，易出错 | 高，标准化 |
| 准确率 | 依赖人工 | FFmpeg+Whisper自动 |

## 与其他工具对比

| 工具 | 离线 | 场景检测 | Whisper | 评分 | 特点 |
|------|------|---------|---------|------|------|
| **video-understand** | ✅ | ✅ | ✅ | ⭐4.7 | HeyGen出品，本地全栈 |
| **Video Watcher** | ✅ | ✅ | ✅ | - | yt-dlp+FFmpeg+Whisper组合 |
| **BibiGPT** | ❌ | ❌ | ✅ | ⭐4.8 | 在线，UI友好，需API |
| **FFmpeg 8.0原生** | ✅ | ❌ | ✅ | - | 命令极简，仅字幕输出 |

## 参考链接

- HeyGen Skills GitHub：https://github.com/heygen-com/skills
- Skill详情页：https://skills.yangsir.net/skill/daily-video-understand
- whisper.cpp：https://github.com/ggerganov/whisper.cpp
- FFmpeg场景检测：https://ffmpeg.org/ffmpeg-filters.html#select_002c-select_002c-nsedselect_002c-nsselect
