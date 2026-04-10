# 通用工具 - DeepSeek VL + FFmpeg 本地视频分析

> 更新时间：2026-04-10
> 技术参考：https://www.cnblogs.com/greywen/p/18727124
> 模型来源：https://github.com/deepseek-ai/DeepSeek-VL2

---

## 核心工具/API

| 工具 | 类型 | 说明 |
|------|------|------|
| **FFmpeg** | 命令行工具 | 视频帧提取、音频分离、视频切片 |
| **DeepSeek-VL2** | 开源多模态模型 | MoE视觉语言模型，支持图像/视频帧分析 |
| **Ollama** | 本地模型运行平台 | 简化 DeepSeek VL 本地部署 |
| **TypeScript / Python** | 胶水语言 | 串联 FFmpeg + DeepSeek VL 的脚本层 |
| **流式输出（Stream）** | 技术特性 | 实时输出分析结果，无需等待完整处理 |

---

## 步骤流程

### 第一步：安装环境依赖

```bash
# 1. 安装 FFmpeg（必须）
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows：下载 ffmpeg.exe 并加入 PATH
# https://ffmpeg.org/download.html

# 2. 安装 Ollama（用于运行 DeepSeek VL）
curl -fsSL https://ollama.com/install.sh | sh

# 3. 拉取 DeepSeek VL 模型（根据显存选择）
ollama pull deepseek-vl2:3b   # 3B 参数，~4GB 显存（推荐新手）
ollama pull deepseek-vl2:7b  # 7B 参数，~8GB 显存
ollama pull deepseek-vl2:16b # 16B 参数，~16GB 显存

# 4. 验证安装
ollama list
ffmpeg -version
```

### 第二步：提取视频关键帧

```bash
# 方式 A：固定间隔提取（适合变化均匀的视频）
ffmpeg -i input_video.mp4 \
  -vf "fps=1/10,scale=1280:720" \
  -q:v 2 \
  frames/frame_%04d.jpg

# 方式 B：场景检测提取（只在画面变化大时提取）
ffmpeg -i input_video.mp4 \
  -vf "select='gt(scene,0.3)',scale=1280:720" \
  -vsync vfr \
  -q:v 2 \
  frames/frame_%04d.jpg

# 方式 C：指定时间点提取
ffmpeg -i input_video.mp4 \
  -ss 00:01:30 -vframes 1 \
  -q:v 2 \
  frame_1min30s.jpg

# 提取音频（供后续分析）
ffmpeg -i input_video.mp4 -vn -acodec pcm_s16le audio.wav
```

### 第三步：使用 DeepSeek VL 分析关键帧

**通过 Ollama API（推荐）：**

```bash
# 单帧分析
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-vl2:3b",
    "prompt": "请描述这张图片中的内容，如果是技术操作视频，请列出具体步骤",
    "images": ["frames/frame_0001.jpg"]
  }'

# 批量多帧联合分析（将多帧 Base64 拼接）
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-vl2:3b",
    "prompt": "请按时间顺序分析这段视频的关键内容，列出每个关键时刻发生的事",
    "images": [
      "frames/frame_0001.jpg",
      "frames/frame_0002.jpg",
      "frames/frame_0003.jpg"
    ]
  }'
```

**Python 脚本示例（批量处理）：**

```python
import subprocess
import base64
import json
import os

def extract_frames(video_path, output_dir, interval=10):
    """每interval秒提取一帧"""
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps=1/{interval},scale=1280:720",
        "-q:v", "2",
        f"{output_dir}/frame_%04d.jpg"
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return sorted(os.listdir(output_dir))

def analyze_frame(image_path, ollama_url="http://localhost:11434"):
    """调用 DeepSeek VL 分析单帧"""
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": "deepseek-vl2:3b",
        "prompt": "详细描述这张图中的内容，如果是操作步骤请逐条列出",
        "images": [img_b64],
        "stream": False
    }

    import requests
    resp = requests.post(f"{ollama_url}/api/generate", json=payload)
    return resp.json().get("response", "")

def full_pipeline(video_path):
    """完整流程：帧提取 + 逐帧分析"""
    frames = extract_frames(video_path, "/tmp/video_frames", interval=15)
    results = []
    for i, frame in enumerate(frames):
        print(f"分析第 {i+1}/{len(frames)} 帧: {frame}")
        desc = analyze_frame(f"/tmp/video_frames/{frame}")
        results.append({"frame": frame, "description": desc})
    return results
```

**TypeScript 脚本示例（流式输出）：**

```typescript
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

// 1. 用 FFmpeg 提取帧
const outputDir = '/tmp/video_frames';
fs.mkdirSync(outputDir, { recursive: true });
execSync(
  `ffmpeg -i input.mp4 -vf "fps=1/20,scale=1280:720" -q:v 2 ${outputDir}/frame_%04d.jpg`,
  { stdio: 'inherit' }
);

// 2. 逐帧调用 Ollama DeepSeek VL
const frames = fs.readdirSync(outputDir).sort();
for (const frame of frames) {
  const result = execSync(
    `curl -s -X POST http://localhost:11434/api/generate \
      -H "Content-Type: application/json" \
      -d '{"model":"deepseek-vl2:3b","prompt":"描述这张图","images":["${Buffer.from(fs.readFileSync(path.join(outputDir, frame))).toString('base64')}"]}'`,
    { encoding: 'utf8' }
  );
  const parsed = JSON.parse(result);
  console.log(`[${frame}]: ${parsed.response}`);
}
```

### 第四步：音频联合分析（可选）

```bash
# Whisper 提取字幕
whisper audio.wav --model medium --language Chinese --output_format srt

# 将字幕与帧分析合并
# 用 LLM 做最后汇总
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-vl2:3b",
    "prompt": "结合以下字幕和画面描述，生成完整的视频内容摘要：\n\n字幕：\n{字幕内容}\n\n画面描述：\n{帧分析结果}\n\n请按【主题】【关键步骤】【核心结论】三部分输出"
  }'
```

---

## 适用场景

- **本地隐私敏感视频**：医疗、法务、内部培训等不能上传云端的视频
- **大批量视频结构化**：需要定期处理大量本地视频（如监控录像、课程录像）
- **离线环境**：没有网络的工作站、服务器
- **技术教程视频**：提取 GUI 操作步骤、代码演示、命令执行过程
- **开源项目演示**：分析操作截图，生成 README 文档

---

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| 显存不足（OOM） | 使用 deepseek-vl2:3b 小模型，或降低图像分辨率 |
| 帧太多处理太慢 | 先用场景检测 `fps=1/30`，或按镜头切分视频 |
| 帧提取时间戳不准 | 记录每帧对应的原始视频时间戳，便于对齐字幕 |
| DeepSeek VL 中文理解弱 | 切换为支持中文的 VL 模型（如 Qwen-VL、GLM-4V） |
| Ollama 版本不兼容 | 升级 Ollama：`brew upgrade ollama` |
| FFmpeg 提取图片颜色异常 | 添加 `-pix_fmt yuv420p` 参数统一色彩空间 |
| 模型幻觉/乱说 | 多次采样 + Prompt 约束，要求只描述看到的，不猜测 |

---

## 技术架构总览

```
┌─────────────────────────────────────────────────────────┐
│              DeepSeek VL + FFmpeg 视频分析架构           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  原始视频文件（MP4/AVI/MOV...）                          │
│       │                                                  │
│       ▼                                                  │
│  ┌────────────┐     ┌─────────────┐                      │
│  │   FFmpeg   │────▶│  关键帧图片  │  (JPEG/PNG)        │
│  │  帧提取器   │     └─────────────┘                      │
│  └────────────┘            │                              │
│       │                   │                              │
│       ▼                   ▼                              │
│  ┌────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │  FFmpeg    │     │ DeepSeek-VL2│     │  分析结果    │  │
│  │  音频提取   │     │ (Ollama)   │────▶│  (结构化文本) │  │
│  └────────────┘     └─────────────┘     └─────────────┘  │
│       │                   │                              │
│       ▼                   │                              │
│  ┌────────────┐           │                              │
│  │  Whisper   │───────────┘                              │
│  │  ASR转录   │                                          │
│  └────────────┘                                           │
│       │                                                  │
│       ▼                                                  │
│  ┌────────────┐                                          │
│  │  LLM 汇总   │ ────────────────────────────────────▶ 最终报告 │
│  └────────────┘                                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 优缺点总结

**优点：**
- ✅ 100% 本地运行，数据不上云，隐私安全
- ✅ 零 API 成本，Ollama + 开源模型免费使用
- ✅ 可深度定制：修改 Prompt、添加后处理逻辑
- ✅ 支持流式输出，实时看到分析进度
- ✅ 与 Whisper 联合：音视频双模态分析

**缺点：**
- ❌ 需要足够显存（至少 4GB，推荐 8GB+）
- ❌ 设置复杂，非技术用户门槛高
- ❌ 处理速度较慢（本地推理 vs 云端 API）
- ❌ DeepSeek VL 对中文 OCR、表格识别能力弱于商用模型
- ❌ 帧提取策略需要人工调优（间隔/场景检测参数）

---

## 参考链接

- 技术博客（博客园）：https://www.cnblogs.com/greywen/p/18727124
- 稀土掘金同文：https://juejin.cn/post/7473423771201470498
- DeepSeek-VL2 GitHub：https://github.com/deepseek-ai/DeepSeek-VL2
- Ollama 官网：https://ollama.com
- FFmpeg 官方文档：https://ffmpeg.org/documentation.html
- Whisper 本地转录：pip install openai-whisper
