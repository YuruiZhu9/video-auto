# FFmpeg 常用命令速查

> AI视频制作流程配套工具 | 适用场景：剪映处理不了时的自动化合成

---

## 一、基础信息查看

```bash
# 查看视频信息
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4

# 查看视频时长
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4

# 提取音频
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# 截图（每10秒一帧）
ffmpeg -i video.mp4 -vf "fps=0.1" image_%03d.png
```

---

## 二、视频拼接与裁剪

```bash
# 拼接多个视频（需先创建 filelist.txt）
# filelist.txt 内容：
# file 'clip1.mp4'
# file 'clip2.mp4'
# file 'clip3.mp4'
ffmpeg -f concat -safe 0 -i filelist.txt -c copy merged.mp4

# 裁剪片段（从第5秒开始，截取10秒）
ffmpeg -i input.mp4 -ss 00:00:05 -t 00:00:10 -c copy clip.mp4

# 从开头裁剪到指定时长
ffmpeg -i input.mp4 -t 00:01:00 -c copy short.mp4

# 裁剪指定区域（左边偏移x，上边偏移y，宽w，高h）
ffmpeg -i input.mp4 -vf "crop=w:h:x:y" output.mp4
```

---

## 三、音频处理

```bash
# 视频添加音频
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4

# 调整音频音量（2倍）
ffmpeg -i audio.mp3 -af "volume=2.0" louder.mp3

# 音频淡入淡出（淡入1秒，淡出2秒）
ffmpeg -i audio.mp3 -af "afade=t=in:ss=0:d=1,afade=t=out:st=28:d=2" fade.mp3

# 混音（视频原声60% + 背景音乐40%）
ffmpeg -i video.mp4 -i bgm.mp3 -filter_complex "[0:a]volume=0.6[a1];[1:a]volume=0.4[a2];[a1][a2]amix=inputs=2:duration=first[aout]" -map 0:v -map "[aout]" -c:v copy output.mp4

# 提取特定时间点的音频片段
ffmpeg -i input.mp4 -ss 00:00:30 -t 00:00:10 -vn -acodec copy audio_clip.aac
```

---

## 四、字幕处理

```bash
# 硬字幕（烧录进视频）
ffmpeg -i video.mp4 -vf subtitles=subtitle.srt output.mp4

# 软字幕（可开关）
ffmpeg -i video.mp4 -i subtitle.srt -c copy -c:s mov_text output.mp4

# ASS字幕样式
ffmpeg -i video.mp4 -vf "ass=subtitle.ass" output.mp4

# 调整字幕延迟（正数=延迟，负数=提前，单位毫秒）
ffmpeg -i input.mp4 -itsoffset 2.5 -i input.mp4 -map 0:v -map 1:a -c copy output.mp4
```

---

## 五、格式转换与压缩

```bash
# 转换为H.264编码（兼容性最好）
ffmpeg -i input.avi -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4

# 压缩到指定码率（5Mbps视频 + 192k音频）
ffmpeg -i input.mp4 -vcodec h264 -b:v 5000k -acodec aac -b:a 192k output.mp4

# 压缩到1GB以内
ffmpeg -i input.mp4 -fs 1000M -c:v libx264 -crf 28 output.mp4

# 转换为WebM格式（适合网页嵌入）
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 output.webm

# 转换为GIF
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" -loop 0 output.gif
```

---

## 六、分辨率与画面调整

```bash
# 调整分辨率
ffmpeg -i input.mp4 -vf "scale=1920:1080" output.mp4

# 竖屏转横屏（两边加黑边）
ffmpeg -i vertical.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.mp4

# 横屏转竖屏（中间裁剪）
ffmpeg -i horizontal.mp4 -vf "crop=1080:1920:(iw-1080)/2:(ih-1920)/2" output.mp4

# 视频加速/减速（2倍速）
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -af "atempo=2.0" output.mp4

# 视频倒放
ffmpeg -i input.mp4 -vf "reverse" -af "areverse" reversed.mp4

# 顺时针旋转90度
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4
```

---

## 七、视频质量与滤镜

```bash
# 提高清晰度（轻度）
ffmpeg -i input.mp4 -vf "unsharp=5:5:1.0:5:5:0.0" output.mp4

# 降噪
ffmpeg -i input.mp4 -vf "hqdn3d=4:3:6:4.5" denoised.mp4

# 添加水印
ffmpeg -i input.mp4 -i watermark.png -filter_complex "overlay=W-w-10:H-h-10" output.mp4

# 文字水印
ffmpeg -i input.mp4 -vf "drawtext=text='@你的账号':fontcolor=white:fontsize=24:x=10:y=H-th-10:shadow=1" output.mp4

# 调整亮度/对比度
ffmpeg -i input.mp4 -vf "eq=brightness=0.1:contrast=1.2" output.mp4

# 色彩增强
ffmpeg -i input.mp4 -vf "curves=vintage" vintage.mp4
```

---

## 八、AI视频批处理脚本

```bash
#!/bin/bash
# 批量拼接：把同一文件夹下所有mp4按文件名顺序拼接

mkdir -p output

for file in *.mp4; do
    echo "file '$file'" >> output/filelist.txt
done

ffmpeg -f concat -safe 0 -i output/filelist.txt -c copy output/merged.mp4

echo "完成！输出: output/merged.mp4"
```

```bash
#!/bin/bash
# 批量压缩：压缩当前目录下所有mp4到指定大小

for file in *.mp4; do
    ffmpeg -i "$file" -vcodec h264 -crf 28 -c:a aac -b:a 128k "compressed_$file"
done

echo "批量压缩完成！"
```

---

## 九、常用参数速查表

| 参数 | 含义 | 示例 |
|------|------|------|
| `-i` | 输入文件 | `-i input.mp4` |
| `-c:v` | 视频编码器 | `-c:v libx264` |
| `-c:a` | 音频编码器 | `-c:a aac` |
| `-crf` | 质量（越小越好，18-28常用）| `-crf 23` |
| `-b:v` | 视频码率 | `-b:v 5000k` |
| `-b:a` | 音频码率 | `-b:a 192k` |
| `-ss` | 开始时间 | `-ss 00:00:05` |
| `-t` | 持续时间 | `-t 00:00:30` |
| `-vf` | 视频滤镜 | `-vf "scale=1920:1080"` |
| `-af` | 音频滤镜 | `-af "volume=2.0"` |
| `-map` | 指定流 | `-map 0:v -map 1:a` |
| `-y` | 自动覆盖输出 | （不加会询问是否覆盖）|

---

> 🤖 由 AI协作视频制作Agent 生成
