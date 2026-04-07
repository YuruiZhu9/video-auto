# 技术教程类 - video-frames 逐帧提取

## 核心工具/API

- **工具**: `ffmpeg`（通过 Skill `video-frames` 调用）
- **脚本**: `/app/openclaw/skills/video-frames/scripts/frame.sh`
- **Skill 路径**: `/app/openclaw/skills/video-frames/SKILL.md`

## 步骤流程

### 基础截帧
```bash
# 提取第一帧（封面帧）
frame.sh /path/to/video.mp4 --out /tmp/cover.jpg

# 提取指定时间戳帧
frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg

# 按帧索引提取
frame.sh /path/to/video.mp4 --index 60 --out /tmp/frame-60.png
```

### 批量提取
```bash
# 每隔 N 秒提取一帧
ffmpeg -i video.mp4 -vf "fps=1/30" frame_%04d.jpg

# 提取关键帧（场景切换时）
ffmpeg -i video.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr frame_%04d.jpg
```

## 适用场景

- **代码演示类教程**: 截取 IDE 界面，分析代码片段
- **UI/交互演示**: 提取关键交互步骤截图
- **算法可视化**: 截取算法执行各阶段画面
- **工具使用演示**: 截取命令行操作步骤
- **架构图解**: 从演示视频中提取架构图画面

## 避坑指南

| 问题 | 解决方案 |
|------|---------|
| 帧太模糊 | 用 `--index` 找到关键帧，用 PNG 格式保存 |
| 视频太长帧太多 | 先计算合理帧率：`总秒数/期望帧数` |
| 截帧时间不精确 | ffmpeg 按 GOP 定位，用 `--index` 直接指定帧号最准 |
| 画面比例不对 | 加 `-vf "scale=1280:-1"` 统一宽度 |
| 截到黑屏/过渡帧 | 先用 `ffmpeg -i video.mp4 -vf "fps=1/N,metadata=print"` 查看帧内容 |
| 颜色失真 | 避免过度压缩，PNG 或 `-q:v 2` 以上的 JPEG 质量 |

## 输出格式选择

| 格式 | 使用场景 | 建议 |
|------|---------|------|
| `.jpg` | 快速预览、分享 | 默认 |
| `.png` | UI/代码等高清晰需求 | PNG 格式 |
| `.webp` | 文件小、质量高 | libwebp 编码器 |
