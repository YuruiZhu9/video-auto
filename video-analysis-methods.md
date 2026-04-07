# 视频解析方法总结

> 🤖 维护：视频解析方法总结 Agent  
> 📅 更新时间：2026-03-27  
> 📂 源目录：`/workspace/reports/video-parser/`（技术前沿分析师输出）  
> 📍 输出路径：`/workspace/video-analysis-methods.md`

---

## 一、核心工具能力地图

| 工具 | 类型 | 语音转文字 | 帧提取 | 多模态理解 | 字幕提取 | 本地/URL/YouTube |
|------|------|:--------:|:------:|:---------:|:--------:|:--------------:|
| **summarize** | Skill/CLI | ✅ | ❌ | ✅ | ✅ | URL + YouTube + 本地 |
| **videos_understand** | 内置工具 | ✅ | ✅ | ✅ | ✅ | URL + 本地 |
| **audios_understand** | 内置工具 | ✅ | ❌ | ✅ | ✅ | URL + 本地 |
| **FFmpeg / video-frames** | CLI | ❌ | ✅ | ❌ | ❌ | 仅本地 |
| **Whisper（API版）** | Skill/API | ✅ | ❌ | ❌ | ✅ | 仅本地 |
| **Whisper（本地CLI版）** | Skill/CLI | ✅ | ❌ | ❌ | ✅ | 仅本地 |
| **yt-dlp** | CLI | ❌ | ❌ | ❌ | ✅（字幕下载） | YouTube + B站等 |
| **BibiGPT** | 第三方工具 | ✅ | ✅ | ✅ | ✅ | B站/YouTube等 |
| **TLDW** | 第三方工具 | ✅ | ✅ | ✅ | ✅ | YouTube为主 |

---

## 二、视频类型 × 推荐方案矩阵

### 2.1 🧑‍💻 技术教程类

**推荐组合**：`summarize`（快速摘要）+ `FFmpeg`（帧提取）+ `videos_understand`（深度理解）+ `Whisper`（无字幕转录）

**解析重点**：步骤拆解、代码片段、工具命令、知识点清单、参考资源链接

**最佳实践流程**：
```
YouTube/URL → summarize --extract-only → 获取字幕文本
     ↓
Whisper 转录（无字幕时）→ 增强文字稿
     ↓
FFmpeg 关键帧提取 → images_understand OCR 代码
     ↓
videos_understand → 结构化笔记输出
```

**避坑指南**：
- 视频中代码一闪而过？→ 放大帧图 `scale=3840` 后 OCR
- 无字幕口音重？→ medium 模型 + prompt 提示上下文

---

### 2.2 🎤 行业分享类

**推荐组合**：`summarize`（快速摘要）+ `videos_understand`（观点分析）+ `FFmpeg`（PPT帧提取）+ `Whisper`（完整文字稿）

**解析重点**：核心观点、数据引用、案例、行业趋势判断、演讲者建议

**最佳实践流程**：
```
YouTube URL → summarize --length long → 演讲摘要
     ↓
FFmpeg 提取 PPT 帧（每30秒一帧）
     ↓
images_understand 批量分析 PPT 内容
     ↓
videos_understand 综合理解 → 结构化洞察报告
```

**避坑指南**：
- 图表数据难以精确还原 → 配合字幕中的数据播报交叉验证
- 长视频（>60分钟）→ 按段落（每10分钟）分段分析

**适用场景**：
- ✅ Conference 演讲（SIGIR、RecSys、CVPR 等顶会分享）
- ✅ 公司发布会（产品发布、战略分享）
- ✅ 行业洞察报告（券商研报解读、投资人分享）
- ✅ 播客/访谈节目（多嘉宾对话结构化）
- ✅ 政策解读视频（监管动态、政策影响分析）

---

### 2.3 🛠️ 开源项目演示类

**推荐组合**：`videos_understand`（项目定位）+ `FFmpeg`（界面截图）+ `images_understand`（代码OCR）+ `Whisper`（步骤旁白）

**解析重点**：项目背景、技术栈、核心功能模块、代码示例、GitHub链接、运行效果

**最佳实践流程**：
```
视频 URL → videos_understand → 项目整体理解
     ↓
FFmpeg 提取关键帧（每15秒）+ 慢速处理易错过内容
     ↓
images_understand OCR 代码 + 链接
     ↓
Whisper 转录演示旁白 → 还原操作步骤
     ↓
结构化输出：项目卡片 + 代码块 + 快速上手命令
```

**避坑指南**：
- GitHub 链接一闪而过？→ 定位链接展示时段逐帧放大提取
- 命令执行太快？→ 慢速处理 `setpts=2*PTS`

---

## 三、逐工具详解

### 3.1 summarize（Skill）

- **首页**：https://summarize.sh
- **支持**：YouTube 自动字幕提取 + AI 摘要
- **常用参数**：
  - `--extract-only`：获取纯字幕文本
  - `--length long`：获取详细摘要
  - `--youtube auto`：自动识别YouTube字幕
- **默认模型**：google/gemini-3-flash-preview
- **适用场景**：有字幕的 YouTube/B站 视频快速摘要

### 3.2 videos_understand

- **支持**：本地文件 + URL（含 YouTube）
- **最大并发**：同时分析 10 个视频
- **核心能力**：多模态理解（画面+音频+字幕联合分析）
- **Prompt 设计关键**：结构化输出要求决定输出质量
- **适用场景**：任意类型视频的深度理解

### 3.3 audios_understand

- **支持**：本地音频 + URL
- **最大并发**：同时分析 10 个音频
- **适用场景**：直接分析视频音频轨道；播客/无画面视频

### 3.4 FFmpeg 帧提取

| 命令 | 功能 |
|------|------|
| `ffmpeg -i video.mp4 -vf "fps=1/30,scale=1280:-1" frame_%04d.jpg` | 每30秒均匀提取一帧 |
| `ffmpeg -ss 00:05:30 -i video.mp4 -vframes 1 frame.jpg` | 提取指定时间戳单帧 |
| `ffmpeg -i video.mp4 -vf "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr frames_%04d.jpg` | I帧场景检测提取 |
| `ffmpeg -i video.mp4 -i video.mp4 -filter_complex "[0:v][1:v]hstack=inputs=2" output.jpg` | 缩略图拼图 |
| `ffmpeg -i video.mp4 -i video.mp4 -filter_complex "[0:v][1:v]vstack=inputs=2" output.jpg` | 垂直拼图 |
| `ffmpeg -i video.mp4 -vf "scale=3840:-1" big_frame.jpg` | 高分辨率放大（OCR用） |
| `ffmpeg -i video.mp4 -vf "setpts=2*PTS" slow.mp4` | 慢速处理快内容 |

**音频提取**：
```bash
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav -y
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3 -y
```

### 3.5 Whisper 系列

| 版本 | API需求 | 费用 | 推荐模型 |
|------|---------|------|---------|
| **API 版**（openai-whisper-api） | OPENAI_API_KEY | 按调用量付费 | whisper-1 |
| **本地 CLI 版** | 无需 API Key | 完全免费 | medium / large-v3 |

**推荐本地 CLI 用法**：
```bash
# 转录为JSON（带段落时间戳）
whisper audio.wav --model medium --language zh \
  --output_format json --output_dir ./transcripts

# 词级时间戳（适合RAG）
whisper audio.wav --model large-v3 --word_timestamps True

# 使用 faster-whisper（GPU加速，速度更快）
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", compute_type="int8")
```

### 3.6 yt-dlp

```bash
# 下载视频（含字幕）
yt-dlp --write-subs --write-auto-subs \
  --sub-lang zh-Hans,zh-Hant,en \
  -o "%(title)s.%(ext)s" "https://youtu.be/xxxx"

# 下载最佳画质
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  -o "%(title)s.%(ext)s" "https://youtu.be/xxxx"
```

### 3.7 第三方工具

**BibiGPT**：
- 专注 B站/YouTube 的 AI 视频总结工具
- 支持一键生成章节摘要、关键要点
- 适合快速了解视频核心内容

**TLDW**：
- 专注长视频的结构化输出
- 支持多种输出格式（SRT/MD/JSON）

---

## 四、进阶方案：视频 RAG 语义搜索

> 将视频内容转化为可语义检索的知识库，适合大量视频学习、代码定位、知识问答。

### 4.1 整体架构

```
视频文件/URL
    ↓ 下载（yt-dlp）
音频提取（FFmpeg）
    ↓ 转录（Whisper）→ 带时间戳的文字稿
语义分块（LLM）→ 按主题/章节切分
    ↓ 向量化（Embedding）
向量数据库（ChromaDB / Milvus / Qdrant）
    ↓ 语义检索
用户Query → Top-K 相关片段 → 时间戳定位
```

### 4.2 工具栈

| 工具 | 用途 | 成本 | 部署 |
|------|------|------|------|
| Whisper | 音频转文字 | 本地免费 / API付费 | 本地 / 云 |
| faster-whisper | 快速转录 | 本地免费 | GPU加速 |
| ChromaDB | 向量存储 | 本地免费 | 轻量 |
| Milvus | 生产向量库 | 开源免费 | 需要服务器 |
| Qdrant | 向量检索 | 开源免费 | Docker |
| OpenAI Embedding | 向量化 | 按Token计费 | 云API |
| ZhipuAI Embedding | 中文向量化 | 低成本 | 云API |

### 4.3 多模态 RAG（帧 + 字幕联合索引）

```python
# 1. 字幕块索引 → collection: "transcripts"
# 2. 关键帧描述索引 → collection: "keyframes"
# 3. 联合检索时交叉验证，提升准确率
```

### 4.4 避坑指南

| 坑 | 解决方案 |
|----|---------|
| Whisper 中文识别率低 | large-v3 模型 + 中文 prompt；或使用 faster-whisper |
| 长视频转录 OOM | 分段转录后合并：`ffmpeg -f segment -segment_time 600` |
| 向量检索结果不相关 | 使用中文优化 Embedding（M3E / ZhipuAI embedding） |
| ChromaDB 数据丢失 | 配置持久化 + 定期备份 |

---

## 五、OpenClaw 自动化脚本

### 5.1 快速解析流水线

```python
# === OpenClaw Agent 自动化 ===
video_url = user_input

# Step 1: 快速摘要
summary = exec(f"summarize '{video_url}' --youtube auto --length long")

# Step 2: 深度理解
result = videos_understand(videos_info=[{
    "url": video_url,
    "prompt": "提取：1. 核心知识点 2. 关键时间戳 3. 代码/命令 4. 参考资源"
}])

# Step 3: 返回结构化结果
return f"✅ 摘要：{summary}\n\n📋 深度分析：{result}"
```

### 5.2 完整解析流水线（本地视频）

```python
# Step 1: 下载（如需要）
exec(f"yt-dlp --write-subs -o 'input/%(title)s.%(ext)s' '{video_url}'")

# Step 2: 提取音频
exec("ffmpeg -i input.mp4 -vn -acodec libmp3lame audio.mp3")

# Step 3: Whisper 转录
transcript = exec("whisper audio.mp3 --model medium --language zh")

# Step 4: 结构化分析
analysis = videos_understand(videos_info=[{
    "file": "input.mp4",
    "prompt": "提取关键步骤、知识点、时间戳"
}])

# Step 5: 返回结果
return f"✅ 视频已解析！\n摘要：{analysis.content[:500]}"
```

---

## 六、快速选型指南

| 需求 | 推荐方案 |
|------|---------|
| 需要提取视频**说了什么**（文字稿） | Whisper 转写 → Summarize 摘要 |
| 需要理解视频**里发生了什么**（画面内容） | `videos_understand` |
| 需要截取**关键帧**做深度分析 | `FFmpeg` 抽帧 → `images_understand` |
| 视频**附带字幕/文稿** | `summarize --extract-only` 直接提取 → LLM 结构化 |
| **代码演示类**视频 | 帧提取 + OCR / 图像识别，提取代码片段 |
| **大量视频**的语义检索 | Whisper + ChromaDB RAG 方案 |
| **B站/YouTube**快速摘要 | BibiGPT / summarize |
| **无字幕**演讲视频 | Whisper (medium/large) + 字幕后处理 |

---

## 七、知识库文件索引

```
/workspace/reports/video-parser/
├── README.md                        ← 工具能力总览 & 索引
├── INDEX.md                        ← 快速选型指南
├── 视频解析方法总结.md              ← 本报告（完整总结）
├── 技术教程类/
│   ├── summarize工具解析.md         # YouTube/URL视频快速摘要
│   ├── FFmpeg-帧提取解析.md         # 帧提取命令详解
│   ├── Whisper转录解析.md           # 音频转文字全方案
│   ├── videos_understand解析.md     # AI多模态视频理解
│   └── 视频RAG语义搜索方案.md        # 向量数据库+视频知识库
├── 行业分享类/
│   ├── 行业分享综合解析.md           # 演讲/Conference视频分析
│   ├── videos_understand通用解析.md # AI直接理解
│   └── 大模型直接理解法.md           # 多模态大模型应用
├── 开源项目演示类/
│   ├── 帧提取+图像识别解析.md        # FFmpeg+OCR方案
│   ├── 字幕+结构化解析.md            # 字幕提取+LLM结构化
│   └── 开源项目演示解析.md           # GitHub+视频联合分析
└── 通用工具/
    ├── yt-dlp视频下载解析.md         # 多平台视频下载
    └── OpenClaw-audios_understand解析.md
```

---

## 八、持续迭代计划

- [ ] 补充：BibiGPT / TLDW 等第三方工具评测
- [ ] 补充：豆包/腾讯等国产模型视频理解 API 对比
- [ ] 补充：本地视频文件中文档类（DASH/HLS流）解析方案
- [ ] 补充：B站视频解析（av/BV号）专项方案
- [ ] 补充：抖音/快手短视频解析方案
- [ ] 补充：多语言视频翻译+解析方案
- [ ] 补充：实时流媒体解析方案
- [ ] 定期更新：每轮 cron 自动刷新本报告

---

*本报告由视频解析方法总结 Agent 自动生成 · 2026-03-27*  
*源数据来源：/workspace/reports/video-parser/（技术前沿分析师输出目录）*
