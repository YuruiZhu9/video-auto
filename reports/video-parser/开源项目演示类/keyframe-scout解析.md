# 开源项目演示类 - keyframe-scout 智能关键帧提取

## 核心工具/API

- **keyframe-scout**
  - PyPI：https://pypi.org/project/keyframe-scout/
  - 类型：Python 包，专为 VLM/LLM 视频分析优化
  - 特点：自适应算法，自动选择最有信息量的帧

- **AutoCut（视频自动剪辑）**
  - GitHub：https://github.com/aegisALLEN/AutoCut
  - 功能：基于 Whisper 字幕自动剪切静音片段
  - 适合：演讲/教程视频的自动预处理

## 步骤流程

### keyframe-scout 安装与使用
```bash
pip install keyframe-scout

# 基本用法（为 VLM 优化提取）
keyframe-scout /path/to/video.mp4 \
  --output-dir ./frames \
  --max-frames 10

# 指定提取策略
keyframe-scout /path/to/video.mp4 \
  --strategy scene_change \  # 场景切换检测
  --output-dir ./frames

# 输出元数据 JSON
keyframe-scout /path/to/video.mp4 \
  --output-dir ./frames \
  --json-metadata metadata.json
```

### AutoCut 自动剪辑 Pipeline
```bash
# Step 1: 音频转写
whisper video.mp4 --model medium --output_format srt

# Step 2: 自动剪辑静音片段
python -m autocut --input video.mp4 --srt video.srt

# Step 3: 拼接保留片段
ffmpeg -f concat -safe 0 -i keep.txt -c copy output.mp4
```

## 适用场景

- ✅ 开源项目 README 配套视频的关键帧提取
- ✅ GitHub 项目 demo 视频摘要
- ✅ 技术分享 PPT 轮播自动检测
- ✅ 演讲视频的幻灯片边界识别
- ✅ 会议录像自动剪辑预处理

## 避坑指南

- **坑1：关键帧提取不准确**
  - 解决：检查 `--strategy` 参数：scene_change / uniform / content
  - 内容感知策略（content）效果最好但最慢

- **坑2：输出目录不存在**
  - 解决：自动创建，`--output-dir` 指定任意路径

- **坑3：视频太大处理慢**
  - 解决：先切分视频再逐段提取
  - ffmpeg -i video.mp4 -ss 0 -t 600 part1.mp4

## 参考链接

- keyframe-scout PyPI：https://pypi.org/project/keyframe-scout/
- AutoCut GitHub：https://github.com/aegisALLEN/AutoCut
