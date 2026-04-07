# 开源项目演示类 — Video-Analyzer 解析

> GitHub: https://github.com/byjlw/video-analyzer

## 核心工具/API

| 组件 | 技术 | 说明 |
|------|------|------|
| **FFmpeg** | 视频处理 | 帧提取、音视频分离 |
| **OpenCV** | 计算机视觉 | 关键帧检测 |
| **Whisper**（OpenAI） | 语音识别 | 音频转录，支持多语言 |
| **Llama 3.2 Vision**（或兼容VLM） | 视觉理解 | 分析关键帧画面 |
| **OpenRouter API**（可选） | LLM接口 | 兼容OpenAI格式的视觉模型API |

---

## 步骤流程

### 一、安装部署

```bash
# 1. 克隆仓库
git clone https://github.com/byjlw/video-analyzer.git
cd video-analyzer

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install .

# 4. 安装FFmpeg
sudo apt-get update && sudo apt-get install -y ffmpeg

# 5. 配置API密钥（可选）
export OPENAI_API_KEY="your-key"
```

### 二、命令行使用

```bash
# 基本用法
video-analyzer path/to/video.mp4

# 使用OpenRouter API
video-analyzer video.mp4 \
    --client openai_api \
    --api-key your-openrouter-key \
    --api-url https://openrouter.ai/api/v1 \
    --model llama3.2-vision \
    --frames-per-minute 15 \
    --whisper-model medium
```

### 三、Python API

```python
from video_analyzer.analyzer import VideoAnalyzer
from video_analyzer.clients.llm_client import LLMClient
from video_analyzer.prompt import PromptLoader

client = LLMClient(api_key="your-key", api_url="https://openrouter.ai/api/v1")
prompt_loader = PromptLoader()
analyzer = VideoAnalyzer(client, "llama3.2-vision", prompt_loader)

frame_analyses = analyzer.analyze_video("path/to/video.mp4")
video_description = analyzer.reconstruct_video(frame_analyses)
print(video_description)
```

---

## 适用场景

- 技术教程视频自动化结构化摘要
- 开源项目README配套视频演示解析
- 产品发布会Demo内容提取
- 本地部署保护数据隐私

---

## 避坑指南

- **FFmpeg必须安装**：最常见失败原因，验证：`ffmpeg -version`
- **Whisper模型**：中文必须用 medium 及以上，准确率差距约15-20%
- **API费用**：OpenRouter按token计费；可选本地GPU模式
- **长视频内存**：medium模型处理1小时视频约需6GB内存，用 --duration 限制
- **输出格式**：目前输出文本描述，需自行转换JSON/Markdown

---

## 参考链接

- Video-Analyzer GitHub：https://github.com/byjlw/video-analyzer
- OpenRouter：https://openrouter.ai
- Whisper：https://github.com/openai/whisper
