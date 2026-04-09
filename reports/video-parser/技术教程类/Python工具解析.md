# 技术教程类 - Python 视频解析工具

> 适合对象：需要深度定制、批量处理、本地部署的技术人员

---

## 工具一：video-analyzer（综合视频分析）

### 核心工具/API
- **GitHub**：`https://github.com/byjlw/video-analyzer`
- **Python** + FFmpeg + Whisper + Vision LLM（Ollama / OpenAI）
- **依赖**：PyAV、Pillow、Whisper、FFmpeg

### 步骤流程
```
1. 安装：git clone https://github.com/byjlw/video-analyzer.git
2. 创建虚拟环境：python3 -m venv .venv && source .venv/bin/activate
3. 安装依赖：pip install -e .
4. 确认 FFmpeg 已安装（系统级依赖）
5. 运行分析：
   video-analyzer path/to/video.mp4
6. 带参数运行（控制采样率和时长）：
   video-analyzer video.mp4 --frames-per-minute 15 --duration 60
```

### 完整处理流程（三步走）
```
Step 1 - 帧提取
  └─ 按设定采样率从视频提取关键帧（如每分钟15帧）
  └─ 对每帧调用 Vision LLM 分析，记录时间戳+分析结果

Step 2 - 音频转录
  └─ 分离音频轨道 → Whisper 模型转录
  └─ 将转录文本与视频帧信息对齐

Step 3 - 生成描述
  └─ 汇总所有帧分析 + 音频转录 → AI 生成连贯的视频描述
  └─ 输出 analysis.json（结构化，含帧标注和文字稿）
```

### 适用场景
- 需要"帧分析 + 字幕"双轨输出的完整视频解析
- 完全本地运行，无 API 费用
- 支持 Ollama 自托管 Vision 模型（如 LLaVA）

### 避坑指南
- ⚠️ 首次运行 Whisper 下载模型较大（medium ≈ 1.5GB，large ≈ 3GB）
- ⚠️ frames-per-minute 设太高会产生大量帧，建议 5-15 帧/分钟
- ⚠️ `--duration` 参数限制分析的视频时长，适合长视频预览
- ⚠️ 配置文件中可选择 Whisper 模型大小：tiny / base / small / medium / large

---

## 工具二：video-frames-skill（ClawHub 安装 · 批量帧提取）

### 核心工具/API
- **GitHub**：`https://github.com/indulgeback/video-frame-extractor`
- **ClawHub**：`clawhub install video-frames-skill`
- **依赖**：PyAV、tqdm、Pillow
- **平台**：Windows / macOS / Linux

### 步骤流程
```
安装方式1（推荐）：
  clawhub install video-frames-skill
  （需要 npm i -g clawhub）

安装方式2（手动）：
  git clone https://github.com/indulgeback/video-frame-extractor.git ~/.video-frame-extractor
  cd ~/.video-frame-extractor
  python3 -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  ln -sf ~/.video-frame-extractor/frame-extractor.py ~/.local/bin/frame-extractor
```

### 常用命令速查
```bash
# 单帧提取（按帧号）
frame-extractor single -i video.mp4 -f 100 -o frame100.jpg

# 单帧提取（按时间点，秒）
frame-extractor single -i video.mp4 -t 3.5 -o frame_at_3_5s.jpg

# 批量提取（每隔5帧取一帧，范围10-50）
frame-extractor batch -i video.mp4 -o frames -s 10 -e 50 -d 5

# 间隔采样（每2秒取一帧）
frame-extractor sample -i video.mp4 -o samples -t 2

# 目录批量（提取目录下所有视频的首帧）
frame-extractor dirfirst -i videos_dir -o output_dir -r

# 视频压缩（H.264重编码）
frame-extractor vcompress -i input.mp4 -o output.mp4 -q 50 -p slow
```

### 适用场景
- 快速为视频库生成缩略图目录
- 提取关键帧用于后续 AI 视觉分析
- 视频质量压缩和格式转换

### 避坑指南
- ⚠️ 质量参数 `-q` 建议 50（平衡体积和质量），设为 100 为近无损
- ⚠️ 编码预设 `-p slower` 速度最慢但质量最高，适合最终存档
- ⚠️ 批量压缩时加 `-w` 参数指定线程数提速

---

## 工具三：PyAV（底层视频处理）

### 核心工具/API
- **官网**：`https://pyav.org/`
- **Python 库**：PyAV（FFmpeg 的 Python 绑定）
- **说明**：底层视频帧控制，适合精确到帧的开发场景

### 步骤流程
```python
import av

# 打开视频
container = av.open("video.mp4")

# 获取视频流
video_stream = container.streams.video[0]

# 按时间seek到指定位置
container.seek(10000)  # 微秒

# 读取帧
for frame in container.decode(video=0):
    # 处理每帧（PIL Image 或 NumPy 数组）
    img = frame.to_image()
    print(f"帧: {frame.index}, 时间: {frame.pts}")
```

### 适用场景
- 需要精确控制帧提取逻辑的开发场景
- 结合 OpenCV / NumPy 做自定义视频分析
- 构建专业视频处理流水线

### 避坑指南
- ⚠️ PyAV 时间单位是微秒，计算时需注意换算
- ⚠️ 必须手动管理资源（with 或 close()），避免内存泄漏
- ⚠️ 某些编码格式需要先安装对应 FFmpeg 解码器

---

## 方法对比

| 工具 | 上手难度 | 批量处理 | 帧提取 | 字幕转录 | 总结生成 |
|------|---------|---------|--------|---------|---------|
| video-analyzer | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| video-frames-skill | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ❌ |
| PyAV | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 需配合Whisper | 需配合LLM |

---

## 参考链接
- video-analyzer GitHub：https://github.com/byjlw/video-analyzer
- video-frames-skill GitHub：https://github.com/indulgeback/video-frame-extractor
- video-frames-skill ClawHub：https://clawhub.ai/indulgeback/video-frames-skill
- PyAV 官方文档：https://pyav.org/docs/stable/
