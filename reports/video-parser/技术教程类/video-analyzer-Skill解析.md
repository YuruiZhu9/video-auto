# video-analyzer Skill — yt-dlp + whisper-cpp 本地视频分析

## 核心工具/API

| 工具 | 功能描述 |
|------|---------|
| **yt-dlp** | 优先快速路径：从 YouTube/X(Twitter)/TikTok 提取已有字幕 |
| **whisper-cpp** | 本地 Whisper（CPU 运行）：无 API 费用，保护隐私，适合无字幕视频 |
| **OpenAI Whisper API** | 云端转录备选：速度快，质量高，按 Token 计费 |
| **Python + analyze_video.py** | Skill 入口脚本，统一调度下载→转录→分析全流程 |
| **多平台支持** | YouTube、X/Twitter（视频推文）、TikTok |

---

## 步骤流程

### 标准处理流程（fast path: 有字幕）

```
用户输入：YouTube 视频 URL
       ↓
① yt-dlp --write-auto-sub --sub-lang zh-Hans,en
   尝试下载已有字幕（SRT/VTT/ass）
       ↓（有字幕？）
  ✅ 字幕文件已提取
       ↓
② analyze_video.py --action transcript → 输出 .txt 时间戳转录
       ↓
③ LLM 格式化：TL;DR + 关键时间点 + 可操作要点
```

### Fallback 流程（无字幕视频）

```
字幕提取失败
       ↓
① yt-dlp -f bestaudio 下载最高质量音频流
       ↓
② whisper-cpp 本地推理（无需网络）
   # medium 模型，CPU 运行，约 1-2 分钟/10分钟视频
       ↓
③ 输出 .txt 时间戳转录
       ↓
④ LLM 格式化：TL;DR + 关键时间点 + 可操作要点
```

### 命令行调用示例

```bash
# 安装 Skill
clawhub install minilozio/video-analyzer-skill
# 或 npx clawhub@latest install minilozio/video-analyzer-skill

# 运行分析
python analyze_video.py --action transcript \
  --url "https://youtube.com/watch?v=abc123"

# 指定输出格式
python analyze_video.py --action summarize \
  --url "https://youtube.com/watch?v=abc123" \
  --language zh
```

---

## 适用场景

- **无字幕的 YouTube 视频**：whisper-cpp 本地推理，无需 API key
- **隐私敏感内容**：所有处理在本地完成，数据不离开设备
- **成本敏感场景**：零 API 费用处理大量视频
- **X/Twitter 视频推文**：普通工具难以下载，yt-dlp 专项支持
- **TikTok 视频下载**：需要保存 MP4 到本地时

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| whisper-cpp 太慢 | 使用了 `large` 模型 | 推荐 `medium`（准确率与速度最佳平衡） |
| 字幕下载失败 | 视频无字幕或地区限制 | 自动切换 whisper-cpp 本地转录 |
| X/Twitter 下载失败 | 账号水印/登录限制 | 使用 Cookie 或 Playwright 回退 |
| 中文识别为繁体 | Whisper 训练语料偏向台语 | 使用 `--language Chinese` + medium 模型 |
| ffmpeg 报错 | 未安装或路径问题 | `apt install ffmpeg` / `brew install ffmpeg` |
| whisper-cpp 内存不足 | 模型过大（large=10GB VRAM） | 切换 `small` 模型（2GB VRAM） |

---

## Whisper 模型选择参考

| 模型 | 参数量 | 多语言 | 显存需求 | 相对速度 | 推荐场景 |
|------|--------|--------|---------|---------|---------|
| tiny | 39M | ✅ | ~1GB | ~10x | 快速测试 |
| base | 74M | ✅ | ~1GB | ~7x | 英文优先 |
| **small** | 244M | ✅ | ~2GB | ~4x | **推荐日常使用** |
| **medium** | 769M | ✅ | ~5GB | ~2x | **推荐精度场景** |
| large | 1550M | ✅ | ~10GB | 1x | 最高精度需求 |
| turbo | 809M | ✅ | ~6GB | ~8x | 速度优先 |

---

## 两套方案对比

| 维度 | 本地 whisper-cpp | OpenAI Whisper API |
|------|-----------------|-------------------|
| **费用** | 零成本 | 按 Token 计费 |
| **隐私** | 完全本地 | 数据发送 OpenAI |
| **速度** | 依赖 CPU/GPU | 快（GPU 加速） |
| **安装** | 需编译/配置 | pip install 即用 |
| **准确性** | 中等（medium 足够） | 高（large 模型） |
| **适用** | 大量视频、无网络 | 偶尔使用、高精度需求 |

---

## 参考链接

- Skill 下载: https://clawskills.sh/skills/minilozio-video-analyzer-skill
- GitHub: https://github.com/openclaw/skills/tree/main/skills/minilozio/video-analyzer-skill
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- whisper-cpp: https://github.com/ggerganov/whisper.cpp
- OpenAI Whisper: https://github.com/openai/whisper
