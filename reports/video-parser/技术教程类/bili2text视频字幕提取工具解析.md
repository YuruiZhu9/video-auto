# 技术教程类 - bili2text 视频字幕提取工具解析

## 核心工具/API

- **bili2text**：开源工具，将视频（Bilibili、YouTube 等）转换为文本
- **yt-dlp**：视频下载，支持 B站、YouTube 等 1000+ 平台
- **FFmpeg**：音频提取和分割
- **Whisper**：开源 ASR 模型（支持 Whisper / WhisperX），将音频转为文字

## 步骤流程

1. **下载视频**
   - 使用 yt-dlp 自动下载视频（支持 B站BV号/YouTube URL）
   - 解析视频元数据（标题、时长、弹幕等）

2. **音频提取**
   - 使用 FFmpeg 从视频中提取音频流
   - 自动格式转换（MP3/AAC/OGG）

3. **音频分割**
   - 按时间或大小分割长音频
   - 避免 Whisper 单次处理的上下文限制

4. **Whisper 转录**
   - 调用 Whisper API 或本地模型进行语音识别
   - 支持中文、英语、日语等多语言
   - 输出带时间戳的文本（可选 SRT 格式）

5. **文本整理**
   - 合并分割片段
   - 清理无意义片段（静音、广告等）
   - 输出结构化文本文件

## 适用场景

- **B站视频转文字稿**：将 UP 主视频内容转为可编辑文字
- **YouTube 视频字幕获取**：绕过 YouTube 字幕下载限制
- **长视频语音内容提取**：适用于 1 小时以上的讲座、播客
- **无字幕视频内容数字化**：为无字幕视频生成文字版本
- **训练数据准备**：为微调模型准备视频-文本配对数据

## 避坑指南

- **Whisper 模型选择**：Whisper large-v3 准确率最高但速度慢；medium 性价比好；small 适合快速测试
- **音频质量影响显著**：背景音乐嘈杂或多人说话的视频，转录准确率会大幅下降
- **B站下载限制**：部分视频有地区限制或登录要求，可能需要 Cookie 认证
- **WhisperX 时间轴对齐**：WhisperX 提供更精确的时间戳，但安装依赖较多（phonemizer 等）
- **长视频分割策略**：分割太短会丢失上下文，建议按自然段落（5-15分钟）分割
- **中英混合内容**：需注意 Whisper 对中文音译词的处理，必要时补充 prompt

## 代码示例

```bash
# 克隆项目
git clone https://github.com/beingaigital/bili2text
cd bili2text

# 安装依赖
pip install -r requirements.txt

# 使用 B站视频 BV 号提取
python bili2text.py --bv BV1xx411c7XZ --output ./output

# 使用 YouTube URL 提取
python bili2text.py --url "https://www.youtube.com/watch?v=XXX" --model large

# 指定语言 + 输出 SRT
python bili2text.py --url "视频URL" --language zh --format srt
```

## 核心洞察

1. **全链路开源**：从下载→提取→转录→整理，全部使用开源工具，不依赖商业 API
2. **B站专精**：针对 B站有特殊处理（BV号解析、弹幕获取、封面提取等）
3. **Whisper 本地运行**：无需 OpenAI API key，纯本地计算（适合隐私敏感场景）
4. **可扩展性强**：代码结构清晰，可根据需求修改各环节（如换用 Faster-Whisper 加速）

## 参考链接

- GitHub：https://github.com/beingaigital/bili2text
