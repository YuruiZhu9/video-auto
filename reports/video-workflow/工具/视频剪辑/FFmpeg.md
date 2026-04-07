# FFmpeg 视频剪辑命令速查手册

> 更新日期：2026-04-04  
> 适用场景：AI视频管线自动化、批量合成、服务器端视频处理

---

## 安装

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (choco)
choco install ffmpeg

# Conda
conda install -c conda-forge ffmpeg
```

---

## 核心参数速查

| 参数 | 说明 |
|------|------|
| `-y` | 自动覆盖输出文件（不询问）|
| `-i input` | 输入文件 |
| `-c:v codec` | 视频编码器（如 libx264）|
| `-c:a codec` | 音频编码器（如 aac）|
| `-pix_fmt yuv420p` | 像素格式（兼容性最强）|
| `-shortest` | 以最短输入为结束时间 |
| `-vf` | 视频滤镜 |
| `-af` | 音频滤镜 |

---

## 实战命令库

### 1. 图片序列 + 音频 → 视频（最常用）

```bash
# 基础版（每张图停留1秒）
ffmpeg -y \
  -framerate 1 \
  -pattern_type glob -i 'slides/*.png' \
  -i voiceover.wav \
  -c:v libx264 -pix_fmt yuv420p \
  -shortest \
  output.mp4

# 进阶版（自动填充黑边，16:9宽屏）
ffmpeg -y \
  -framerate 1 \
  -pattern_type glob -i 'slides/*.png' \
  -i voiceover.wav \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" \
  -c:v libx264 -pix_fmt yuv420p \
  -shortest \
  output_16x9.mp4

# 进阶版2（9:16竖屏版，适合抖音/小红书）
ffmpeg -y \
  -framerate 1 \
  -pattern_type glob -i 'slides/*.png' \
  -i voiceover.wav \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -c:v libx264 -pix_fmt yuv420p \
  -shortest \
  output_9x16.mp4
```

### 2. 视频片段合并

```bash
# 创建文件列表
cat > filelist.txt << 'EOF'
file 'clip1.mp4'
file 'clip2.mp4'
file 'clip3.mp4'
EOF

# 合并（无重新编码，速度快）
ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy merged.mp4

# 合并（重新编码，保证统一格式）
ffmpeg -y -f concat -safe 0 -i filelist.txt \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac \
  merged_reencoded.mp4
```

### 3. 音视频混合

```bash
# 人声 + BGM 混合（人声100%，BGM 30%）
ffmpeg -y \
  -i video_no_audio.mp4 \
  -i voiceover.wav \
  -i background_music.mp3 \
  -filter_complex "
    [1:a]volume=1.0[voice];
    [2:a]volume=0.3[bgm];
    [voice][bgm]amix=inputs=2:duration=longest[aout]
  " \
  -map 0:v -map "[aout]" \
  -c:v copy \
  video_with_audio.mp4

# 音频音量标准化
ffmpeg -y -i video_with_audio.mp4 \
  -af "volume=normalize=peak:level=0.8" \
  normalized.mp4
```

### 4. 字幕处理

```bash
# 添加SRT字幕
ffmpeg -y -i video.mp4 \
  -vf subtitles=subtitle.srt \
  output_with_subtitle.mp4

# 内嵌ASS字幕（支持样式）
ffmpeg -y -i video.mp4 \
  -vf subtitles=subtitle.ass \
  output_with_ass.mp4
```

### 5. 格式转换

```bash
# MOV → MP4
ffmpeg -y -i input.mov -c:v libx264 -pix_fmt yuv420p output.mp4

# WebM → MP4
ffmpeg -y -i input.webm -c:v libx264 -pix_fmt yuv420p output.mp4

# 提取音频
ffmpeg -y -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
ffmpeg -y -i video.mp4 -vn -acodec pcm_s16le audio.wav
```

### 6. 视频裁剪与缩放

```bash
# 裁剪视频（从(100,50)开始，裁800x600）
ffmpeg -y -i input.mp4 \
  -vf "crop=800:600:100:50" \
  cropped.mp4

# 横版转竖版（两侧加黑边）
ffmpeg -y -i horizontal.mp4 \
  -vf "pad=ih*9/16:ih:(ow-iw)/2:0:black" \
  vertical.mp4

# 竖版转横版（上下加黑边）
ffmpeg -y -i vertical.mp4 \
  -vf "pad=iw:iw*16/9:(ow-iw)/2:(oh-ih)/2:black" \
  horizontal.mp4

# 缩放到720P
ffmpeg -y -i input.mp4 \
  -vf "scale=-2:720" \
  scaled_720p.mp4
```

### 7. 片头片尾合成

```bash
# 方案：先合并片头+正片，再合并片尾
# Step 1: 片头 + 正片
ffmpeg -y -f concat -safe 0 -i part1.txt -c copy temp.mp4

# Step 2: temp + 片尾
ffmpeg -y -f concat -safe 0 -i part2.txt -c copy final.mp4
```

### 8. 压缩与优化

```bash
# 低质量压缩（文件体积小）
ffmpeg -y -i input.mp4 -c:v libx264 -crf 28 -preset fast small.mp4

# 高质量压缩（文件小但画质好）
ffmpeg -y -i input.mp4 -c:v libx264 -crf 22 -preset slow high_quality.mp4

# 仅压缩音频
ffmpeg -y -i input.mp4 -c:a aac -b:a 128k output.mp4
```

---

## Python 自动化脚本

```python
import subprocess
import os
from pathlib import Path

class VideoPipeline:
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
    
    def images_to_video(self, image_pattern, audio_file, output, fps=1, 
                        scale_w=1920, scale_h=1080):
        """图片序列 + 音频 → 视频"""
        # 构造scale滤镜（自动填充黑边）
        scale_filter = (
            f"scale={scale_w}:{scale_h}:"
            "force_original_aspect_ratio=decrease,"
            f"pad={scale_w}:{scale_h}:(ow-iw)/2:(oh-ih)/2:black"
        )
        
        cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-pattern_type', 'glob', '-i', image_pattern,
            '-i', str(audio_file),
            '-vf', scale_filter,
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-shortest',
            str(output)
        ]
        subprocess.run(cmd, check=True, cwd=self.project_dir)
        print(f"✅ 视频生成完成: {output}")
    
    def merge_videos(self, clip_list, output):
        """多个视频片段合并"""
        with open(self.project_dir / 'filelist.txt', 'w') as f:
            for clip in clip_list:
                f.write(f"file '{clip}'\n")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0',
            '-i', str(self.project_dir / 'filelist.txt'),
            '-c', 'copy',
            str(output)
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ 合并完成: {output}")
    
    def add_subtitles(self, video_file, srt_file, output):
        """添加字幕"""
        cmd = [
            'ffmpeg', '-y', '-i', str(video_file),
            '-vf', f'subtitles={srt_file}',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            str(output)
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ 字幕添加完成: {output}")
    
    def mix_audio(self, video_file, voice_file, bgm_file, output, 
                  voice_vol=1.0, bgm_vol=0.3):
        """混音：视频 + 人声 + BGM"""
        cmd = [
            'ffmpeg', '-y', '-i', str(video_file),
            '-i', str(voice_file), '-i', str(bgm_file),
            '-filter_complex',
            f'[1:a]volume={voice_vol}[voice];'
            f'[2:a]volume={bgm_vol}[bgm];'
            '[voice][bgm]amix=inputs=2:duration=longest[aout]',
            '-map', '0:v', '-map', '[aout]',
            '-c:v', 'copy',
            str(output)
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ 混音完成: {output}")

# 使用示例
pipeline = VideoPipeline('/workspace/video_project')

# 1. 图片序列 + 语音 → 视频
pipeline.images_to_video(
    image_pattern='slides/*.png',
    audio_file='voiceover.wav',
    output='step1_video.mp4',
    fps=0.5  # 每张图停留2秒
)

# 2. 多个片段合并
pipeline.merge_videos(
    clip_list=['intro.mp4', 'step1_video.mp4', 'outro.mp4'],
    output='merged.mp4'
)

# 3. 添加字幕
pipeline.add_subtitles(
    video_file='merged.mp4',
    srt_file='subtitle.srt',
    output='with_subtitle.mp4'
)

# 4. 混音（人声+BGM）
pipeline.mix_audio(
    video_file='with_subtitle.mp4',
    voice_file='voiceover.wav',
    bgm_file='bgm.mp3',
    output='final_output.mp4',
    voice_vol=1.0,
    bgm_vol=0.25
)
```

---

## AI视频管线集成方案

```
┌──────────────────────────────────────────────────────┐
│                  FFmpeg 自动化管线                     │
├──────────────────────────────────────────────────────┤
│                                                       │
│  文案脚本 ──→ Gamma生成PPT ──→ 导出PNG序列            │
│      │                                            │   │
│      ▼                                            ▼   │
│  ElevenLabs ──→ 语音克隆 ──→ voiceover.wav         │
│      │                                            │   │
│      ▼                                            ▼   │
│  Mureka V8 ──→ BGM生成 ──→ bgm.mp3                  │
│      │                                            │   │
│      └──────────────┬───────────────────────────┘   │
│                     ▼                                 │
│           FFmpeg 一键合成                             │
│           图片序列 + 人声 + BGM                        │
│                     ▼                                 │
│              final_video.mp4                          │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## 常见错误处理

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `No such file` | 文件路径错误 | 使用绝对路径或检查文件名 |
| `Invalid data found` | 文件格式不支持 | 加 `-c:v copy` 直接复制流 |
| `Output size too small` | 分辨率为奇数 | 使用 `-2` 保持偶数宽高 |
| `Duration limit` | 音视频时长不匹配 | 用 `-shortest` 或 `-loop 1` |
| `Directory not empty` | 覆盖文件权限 | 加 `-y` 或检查权限 |
