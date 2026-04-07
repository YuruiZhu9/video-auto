# 开源项目演示类 — video-analyzer 工具

> 🤖 更新：2026-03-31 | 来源：知乎专栏 + GitHub
> 维护状态：🆕 新增

---

## 核心工具/API

| 工具 | 功能描述 |
|------|----------|
| **Llama3.2 Vision（11B）** | 关键帧视觉分析，生成自然语言帧描述，考虑前后帧上下文保持连贯性 |
| **OpenAI Whisper** | 音频转录，处理低质量音频，确保转录准确性 |
| **OpenCV** | 视频关键帧提取（智能场景检测） |
| **Ollama** | 本地 LLM 推理运行时（默认），无需 API 密钥 |
| **OpenRouter** | 可选云端 LLM 扩展，提升处理速度和扩展性 |

---

## 步骤流程

```
第1步：安装依赖
  git clone https://github.com/byjlw/video-analyzer.git
  cd video-analyzer
  python3 -m venv .venv && source .venv/bin/activate
  pip install .
  # 安装 FFmpeg（Ubuntu/macOS/Windows）

第2步：关键帧提取（OpenCV）
  · 自动检测场景变化，提取关键帧
  · 保留视频中视觉信息最丰富的时刻
  · 输出帧序列

第3步：音频转录（Whisper）
  · 提取视频音频流
  · Whisper 模型转录为文字
  · 处理低质量音频降噪

第4步：帧分析（Llama Vision）
  · 对每个关键帧进行视觉分析
  · 结合前一帧上下文，保持内容连贯性
  · 生成自然语言帧描述

第5步：结果整合
  · 按时间顺序组合帧分析结果
  · 整合音频转录内容
  · 以首帧设定场景背景
  · 输出完整视频描述报告
```

---

## 适用场景

- **内容审核**：自动分析视频内容，识别违规片段
- **视频管理与检索**：生成元数据和描述，便于搜索管理
- **教育培训**：分析教学视频，提取关键知识点时间戳
- **安全监控**：异常行为识别（配合专用微调模型）
- **媒体娱乐**：广告分析、内容分类、用户行为挖掘
- **视频切片制作**：提取高光帧 + 对应解说词，一键生成切片文案

---

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| **无 GPU 速度慢** | 使用 Ollama 时默认消耗大量内存，7B 模型建议 16GB+ RAM；或切换 OpenRouter 云端 API |
| **长视频内存溢出** | 分段处理视频（FFmpeg split），每段单独分析后合并 |
| **音频质量差转录不准** | 手动用 FFmpeg 预处理音频：`ffmpeg -i video.mp4 -af denoise=adaptive output.mp4` |
| **Whisper 模型选择** | 默认 whisper-1；中文视频建议用 `whisper-1` + `--language zh` 指定中文 |
| **关键帧提取过多** | 调低 OpenCV 场景变化阈值，或手动指定帧间隔 |

---

## OpenClaw 集成方式

```bash
# OpenClaw 中使用 FFmpeg 提取帧 → 结合 videos_understand
# 与 video-analyzer 思路相同，但使用 OpenClaw 内置工具

# 步骤1：FFmpeg 提取关键帧（每隔 N 秒或场景变化时）
ffmpeg -i input.mp4 -vf "select='eq(pict_type,I-frame)',fps=1/10" frames_%03d.jpg

# 步骤2：批量发送给 videos_understand 分析
# （使用 OpenClaw 的 videos_understand 工具，替代本地 Llama Vision）

# 步骤3：audios_understand 替代 Whisper 转录音频
```

---

## 参考链接

- GitHub：https://github.com/byjlw/video-analyzer
- Ollama：https://ollama.ai
- OpenRouter：https://openrouter.ai
