# 技术教程类 - Python 视频处理工具

## 核心工具/API

- **MoviePy**: Python视频编辑库，适合剪辑、拼接、添加文字
- **OpenCV**: 计算机视觉库，适合帧级处理、目标检测
- **Pillow (PIL)**: 图片处理，可用于视频帧的处理

## 步骤流程

### MoviePy 基本用法

1. **安装**
   ```bash
   pip install moviepy
   ```

2. **提取视频片段**
   ```python
   from moviepy.editor import VideoFileClip
   
   clip = VideoFileClip("input.mp4")
   # 提取0-10秒片段
   subclip = clip.subclip(0, 10)
   subclip.write_videofile("output.mp4")
   ```

3. **提取音频**
   ```python
   clip = VideoFileClip("input.mp4")
   clip.audio.write_audiofile("output.mp3")
   ```

4. **添加文字水印**
   ```python
   from moviepy.editor import TextClip
   
   txt_clip = TextClip("Hello World", fontsize=70, color='white')
   txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(10)
   final_clip = CompositeVideoClip([video_clip, txt_clip])
   ```

### OpenCV 基本用法

1. **安装**
   ```bash
   pip install opencv-python
   ```

2. **读取视频并提取帧**
   ```python
   import cv2
   
   cap = cv2.VideoCapture('video.mp4')
   frame_count = 0
   while cap.isOpened():
       ret, frame = cap.read()
       if not ret:
           break
       # 每30帧保存一帧
       if frame_count % 30 == 0:
           cv2.imwrite(f'frame_{frame_count}.jpg', frame)
       frame_count += 1
   cap.release()
   ```

3. **视频关键帧检测**
   ```python
   import cv2
   
   def extract_keyframes(video_path, output_dir):
       cap = cv2.VideoCapture(video_path)
       prev_frame = None
       frame_idx = 0
       keyframe_idx = 0
       
       while cap.isOpened():
           ret, frame = cap.read()
           if not ret:
               break
           
           if prev_frame is not None:
               # 计算帧差
               diff = cv2.absdiff(prev_frame, frame)
               if diff.mean() > 30:  # 阈值
                   cv2.imwrite(f'{output_dir}/keyframe_{keyframe_idx}.jpg', frame)
                   keyframe_idx += 1
           
           prev_frame = frame
           frame_idx += 1
       
       cap.release()
   ```

## 适用场景

- 批量处理教学视频（提取片段、加字幕）
- 自动化视频剪辑工作流
- 视频内容分析（关键帧提取）
- 技术教程视频后期处理

## 避坑指南

- **问题**: MoviePy 处理大视频内存溢出
  - **解决**: 使用 `clip.flush()` 及时释放内存，或分段处理

- **问题**: OpenCV 无法读取某些格式
  - **解决**: 先用 ffmpeg 转换为 mp4 格式

- **问题**: 中文字体显示为方块
  - **解决**: 指定中文字体路径，如 `font='simhei.ttf'`

- **问题**: 处理速度慢
  - **解决**: 使用多线程/多进程，或使用GPU加速版本

## 进阶技巧

### FFmpeg + Python 结合

```python
import subprocess

# 使用ffmpeg提取音频
subprocess.run([
    'ffmpeg', '-i', 'input.mp4',
    '-vn', '-acodec', 'libmp3lame', 'output.mp3'
])
```

### 视频信息查看

```python
import cv2

cap = cv2.VideoCapture('video.mp4')
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print(f"Frame count: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
print(f"Duration: {cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)}")
print(f"Resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
```

## 参考链接

- [MoviePy官方文档](https://zulko.github.io/moviepy/)
- [MoviePy中文手册](https://moviepy-cn.readthedocs.io/)
- [OpenCV Python教程](https://docs.opencv.org/)
