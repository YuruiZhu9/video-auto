# DeepParseX — 多模态文档解析平台（含视频支持）

> 🤖 维护：视频解析方法总结Agent  
> 📅 新增日期：2026-03-29  
> 🔗 来源：GitHub / Gitee

---

## 核心工具/API

- **DeepParseX**：多模态文档解析与知识管理平台
- **支持格式**：PDF、Word、Excel、PPT、图片、视频、音频
- **RAG能力**：检索增强生成，知识库构建
- **Python SDK**：pip install 即可使用
- **API接口**：REST API，支持本地部署

---

## 核心能力

### 支持的文件类型

| 类型 | 解析内容 | 输出格式 |
|------|----------|----------|
| 视频 (.mp4/.avi/.mov) | 关键帧提取 + 语音转文字 + 场景描述 | JSON/Markdown |
| 音频 (.mp3/.wav/.m4a) | 语音转文字 + 说话人分离 | SRT/JSON/TXT |
| 图片 (.jpg/.png/.webp) | OCR文字识别 + 图像描述 | JSON/Markdown |
| 文档 (PDF/DOCX/PPT) | 结构化提取 + 表格解析 | JSON/Markdown |
| 网页 | 完整内容提取 + 元数据 | Markdown/HTML |

---

## 步骤流程

### 安装与基础使用

```bash
pip install deepparsex

# 或 Docker 部署
docker run -p 8000:8000 deepparsex/parser
```

### Python使用示例

```python
from deepparsex import Parser

parser = Parser(
    api_key="your-api-key",  # 或本地部署时留空
    base_url="http://localhost:8000"
)

# 解析视频文件
result = parser.parse(
    file_path="/path/to/video.mp4",
    extract_audio=True,      # 提取语音转文字
    extract_frames=True,     # 提取关键帧
    frame_interval=30,       # 每30秒一帧
    ocr=True,               # OCR识别帧内文字
    language="zh"
)

print(result.structured_output)  # 结构化JSON
print(result.audio_transcript)   # 语音文字稿
print(result.key_frames)         # 关键帧列表
```

### API调用

```bash
curl -X POST "http://localhost:8000/api/v1/parse" \
  -H "Authorization: Bearer your-token" \
  -F "file=@video.mp4" \
  -F "options={\"extract_audio\":true,\"extract_frames\":true,\"language\":\"zh\"}"
```

---

## 适用场景

- **技术视频深度解析**：视频 → 字幕 + 关键帧 + 结构化内容，一站式完成
- **知识库构建**：将视频教程批量转为可检索知识库（RAG场景）
- **企业文档处理**：视频会议录像、演示视频统一归档解析
- **多模态数据管道**：视频+音频+文档统一处理的完整pipeline

---

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| 视频解析速度慢 | 使用`frame_interval`降低帧采样频率 |
| 长视频OOM | 分段处理：每段≤10分钟 |
| 音频无字幕识别不准 | 确保音频质量；使用large模型 |
| 本地部署GPU要求 | 需要NVIDIA GPU + CUDA支持 |

---

## 参考链接

- GitHub：https://github.com/Arterning/DeepParseX
- Gitee：https://gitee.com/zhouwenke/DeepParseX
