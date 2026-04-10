# 视频解析方法总结索引

> 最近更新：2026-04-10 第十周更新（上午+下午场）
> 新增：AutoGaze/CurveStream/UFVideo（CVPR 2026）、AgentVista/MovieTeller（AAAI 2026）、VideoRAG/Vimo（KDD 2026）
> 下午新增：视频解析推荐系统应用专题、Snipd播客工具解析、视频标签自动化Pipeline教程
> 维护Agent：视频解析方法总结Agent

---

## 方法总览

| 方法 | 核心工具 | 适用视频类型 | 难度 | 核心能力 |
|------|----------|-------------|------|----------|
| **AI视频直接理解** | videos_understand | 任意视频 | ⭐ | 多模态语义理解+画面分析 |
| **Gemini 2.5 Pro** | Gemini API | 长视频/行业分享 | ⭐⭐ | VideoMME 85.2%超越人类，原生多模态 |
| **Gemini 2.5 Flash** | Gemini API | 中长视频/批量处理 | ⭐⭐ | 性价比最优，支持~6h |
| **Claude 3.7 Sonnet Extended** | Anthropic API | 编程教程/代码演示 | ⭐⭐⭐ | 超长思维链，深度推理 |
| **WayinVideo AI Clipping** | WayinVideo API | 多类型视频 | ⭐ | AI剪辑+时刻搜索+摘要+转录 |
| **VideoARM编排架构** | 子Agent+记忆文件 | 复杂视觉QA | ⭐⭐⭐ | 迭代探索+置信度输出 |
| **video-vision Skill** | FFmpeg + Vision AI | GUI操作/PPT/无字幕 | ⭐⭐ | 可控帧提取+视觉理解 |
| **video-analyzer Skill** | yt-dlp + whisper-cpp | 无字幕视频/播客 | ⭐⭐ | 零成本本地转录 |
| **AI音频理解** | audios_understand | 播客/访谈 | ⭐ | 语音转文字+内容分析 |
| **Whisper音频转录** | whisper / openai-whisper-api | 有声视频 | ⭐⭐ | 高精度语音转文字 |
| **summarize快速摘要** | summarize CLI | 有字幕/URL视频 | ⭐ | 快速获取摘要 |
| **FFmpeg帧提取+OCR** | ffmpeg + images_understand | 代码演示/GUI操作 | ⭐⭐ | 提取画面中的文字/代码 |
| **BibiGPT深度总结** | BibiGPT / BiliNote | B站/多平台 | ⭐ | 专业视频总结工具 |
| **AutoClip高光提取** | AutoClip + FFmpeg + LLM | 短视频/自媒体/高光剪辑 | ⭐⭐ | YouTube+B站自动高光切片 |
| **DeepSeek VL本地分析** | FFmpeg + DeepSeek-VL2 + Ollama | 隐私敏感/离线/批量处理 | ⭐⭐⭐ | 100%本地，零API成本 |
| **VideoSeek AI总结** | VideoSeek Cloud API | 多平台快速摘要 | ⭐ | YouTube/B站/抖音/小红书+思维导图 |
| **n8n自动化工作流** | n8n + YouTube API + LLM | 批量处理/定时监控 | ⭐⭐⭐ | 全自动视频→结构化笔记 |
| **Video Summary Skill** | 多平台统一入口 | B站/小红书/抖音/YouTube | ⭐ | 多平台快速摘要 |
| **AutoGaze** | AutoGaze + ViT/MLLM | 超长4K/高清视频 | ⭐⭐ | Token压缩4x-100x，加速19x（CVPR 2026）|
| **CurveStream** | CurveStream + MLLM | 实时流/监控/直播 | ⭐⭐ | 无训练流式理解，曲率感知内存管理（CVPR 2026）|
| **VideoRAG / Vimo** | HKUDS VideoRAG | 超长视频（100h+） | ⭐⭐⭐ | 知识图谱+多模态RAG，单卡处理数百小时（KDD 2026）|
| **UFVideo** | UFVideo 统一框架 | 多任务视频理解 | ⭐⭐ | 4类任务统一（QA+分割+引用+定位，CVPR 2026）|
| **Snipd** | Snipd APP | 播客/YouTube视频 | ⭐⭐ | AI精华捕捉+智能问答+YouTube导入，适合技术演讲快速摄入 |
| **视频标签Pipeline** | yt-dlp+Whisper+FFmpeg+VL+FAISS | 推荐系统视频特征 | ⭐⭐⭐ | 完整Python代码，从视频到推荐系统标签/向量入库 |

---

## 快速选型指南

```
我需要做什么？
├─ 快速知道视频说了什么 → summarize + videos_understand
├─ 长视频/复杂多模态理解（1h+）→ Gemini 2.5 Pro（低分辨率模式）
├─ 高性价比批量处理 → Gemini 2.5 Flash
├─ 编程教程/代码理解 → Claude 3.7 Sonnet Extended Thinking
├─ 提取短视频高光剪辑 → WayinVideo AI Clipping
├─ 精确时刻检索 → WayinVideo Find Moments / Gemini 2.5 Pro
├─ 复杂视觉问答+需要置信度 → VideoARM 子Agent编排
├─ 需要完整文字稿 → video-analyzer Skill（零成本）/ whisper API
├─ 理解视频画面内容 → video-vision Skill（FFmpeg帧+Vision AI）
├─ 截取代码/文字画面 → FFmpeg帧提取 → images_understand OCR
├─ 视频附带字幕/文稿 → yt-dlp --write-auto-sub / summarize
├─ 多平台（B站/抖音/小红书）快速摘要 → Video Summary Skill / VideoSeek AI
├─ 自媒体/短视频高光剪辑 → AutoClip（开源免费）/ WayinVideo
├─ 本地离线分析（隐私敏感）→ DeepSeek VL2 + FFmpeg（零成本）
└─ 搜索视频中某个内容点 → Gemini Embedding 2 多模态RAG
├─ 播客/技术演讲快速摄入精华 → Snipd（最佳体验）/ BibiGPT
├─ 构建推荐系统视频特征 → 视频标签自动化Pipeline（通用方法类/视频解析推荐系统应用专题）
└─ 超长视频+知识库检索 → VideoRAG/Vimo（KDD 2026，100h+支持）
```

---

## 视频类型 × 推荐方案矩阵

| 视频类型 | 推荐方案 | 解析重点 |
|----------|----------|----------|
| 技术教程（编程/工具/GUI） | Claude 3.7 Extended / video-vision Skill | 步骤拆解、代码片段、命令清单 |
| 技术教程（有字幕/演讲型） | yt-dlp + Whisper + videos_understand | 步骤拆解、语音逐字稿 |
| 行业分享/演讲（普通 <20min） | videos_understand / Gemini 2.5 Flash | 观点、数据、案例、趋势 |
| 行业分享/演讲（长 >1h） | Gemini 2.5 Pro（低分辨率模式） | 观点、趋势、多模态联合 |
| 开源项目演示 | video-vision Skill + GitHub README | 功能演示、操作步骤、项目架构 |
| 播客/访谈 | video-analyzer Skill（零成本） | 对话内容、关键引述、结论 |
| B站/YouTube视频 | yt-dlp + BibiGPT / Video Summary Skill | 平台原生解析+AI增强 |
| 短视频高光剪辑 | WayinVideo AI Clipping | 片段+标题+标签+下载链接 |

---

## 基准数据（2026年4月版）

| 模型/方法 | VideoMME 准确率 | 长视频支持 | 多模态原生 |
|---------|--------------|---------|---------|
| Gemini 2.5 Pro | 85.2% 🔥 超越人类 | ✅ ~6小时 | ✅ |
| 人类水平 | 84.3% | ✅ | ✅ |
| Claude 3.7 Sonnet (Extended) | ~60-70% | ✅（分段） | 部分 |
| Gemini 2.5 Flash | ~70-75% | ✅ | ✅ |
| GPT-4.1 (直接) | ~42% | 有限 | ❌ |
| GPT-4o (直接) | 36.6% | 有限 | ✅ |
| 关键帧选择 (FOCUS) | +11.9%提升 | ✅ | ✅ |

---

## 目录结构

```
video-parser/
├── INDEX.md                                    # ⭐ 本文件（总索引）
├── 视频解析方法总结.md                          # 第四周更新主报告
├── 执行报告-2026-04-06.md                      # 本次执行报告
│
├── 技术教程类/
│   ├── OpenClaw-Skill解析.md
│   ├── OpenClaw-video-vision技能解析.md         # 🆕 第四周
│   ├── video-analyzer-Skill解析.md              # 🆕 第四周
│   ├── WayinVideo-AI-Clipping-Skill解析.md      # 🆕 第五周
│   ├── VideoARM-Video-Reader-Skill解析.md       # 🆕 第五周
│   ├── Video-Summary-Skill多平台视频摘要解析.md  # 🆕 第五周
│   ├── FFmpeg-帧提取解析.md
│   ├── Whisper转录方法.md
│   ├── yt-dlp-Whisper转录方案.md
│   ├── 视频结构化解析Prompt工程进阶.md
│   └── 外部工具解析.md
│
├── 行业分享类/
│   ├── videos_understand通用解析.md
│   ├── ICLR-2026-视频理解前沿方法.md
│   ├── Qwen3-VL视频理解能力对比与应用.md
│   ├── BibiGPT-BiliNote解析.md
│   ├── 豆包视频理解解析.md
│   ├── AgentVista-多模态智能体视频评测基准解析.md  # 🆕 第十周·上午
│   ├── MovieTeller-电影视频结构化摘要生成解析.md    # 🆕 第十周·上午
│   └── Snipd-AI播客精华提取工具解析.md             # 🆕 第十周·下午
│
├── 开源项目演示类/
│   ├── FFmpeg命令行.md
│   ├── Whisper系列音频转录解析.md
│   ├── 帧提取+图像识别解析.md
│   └── GitHub-README提取方案.md
│
└── 通用工具/
    ├── yt-dlp-视频下载解析.md
    ├── n8n-YouTube视频自动化解析工作流.md
    ├── Whisper-Mate音视频转录关键帧检测.md
    ├── 多模态RAG视频语义检索全链路方案.md
    ├── GPT-4.1-mini视频理解解析.md
    ├── Video-Learn-Skill解析.md                 # 🆕 第四周
    ├── Gemini-2.5-视频理解解析.md                # 🆕 第四周
    ├── 大模型视频理解能力横向对比2026.md         # 🆕 第五周
    └── 智源Emu3-统一多模态视频理解解析.md         # 🆕 第六周

└── 通用方法类/
    ├── 视频RAG语义搜索方案.md                    # 🆕 第三周
    ├── 视频解析Agent工作流编排.md                 # 🆕 第六周
    ├── 视频解析推荐系统应用专题.md                # 🆕 第十周·下午
    └── 视频标签自动化生成Pipeline教程.md         # 🆕 第十周·下午
```

---

## 更新日志

### 2026-04-10 第七周新增（补充）
- **通用工具/NVIDIA-AI-Blueprint视频搜索与总结解析.md** — 企业级视频搜索+总结，VILA+Llama Nemotron+Nemo Retriever RAG，NVIDIA Metropolis平台，PB级视频亚秒检索
- **通用工具/Time-R1视频时序定位模型解析.md** — 强化学习后训练视频时序定位，仅2.5K数据刷新SOTA，支持自然语言查询定位视频片段
- **通用工具/Uni-MoE统一多模态MoE模型视频理解解析.md** — MoE架构统一多模态LLM，稀疏激活高效处理视频+语音+文本，企业多模态知识库首选

### 2026-04-10 第七周新增
- **技术教程类/VideoSeek-AI多平台视频总结解析.md** — 多平台（YouTube/B站/抖音/小红书）视频总结+思维导图，内置浏览器插件
- **通用工具/AutoClip-AI视频剪辑高光提取解析.md** — 开源AI视频高光切片，Docker一键部署，支持YouTube+B站双平台
- **通用工具/DeepSeek-VL2-FFmpeg本地视频分析解析.md** — 100%本地运行，FFmpeg帧提取+DeepSeek VL2视觉分析，零API成本

### 2026-04-06 第六周新增
- **通用工具/智源Emu3-统一多模态视频理解解析.md** — BAAI Nature 2025正刊，next-token统一图像+视频+文本，国产可本地部署
- **通用方法类/视频解析Agent工作流编排.md** — 四大编排模式（串行/并行/路由/迭代），LlamaIndex/LangChain/OpenClaw SubAgent完整代码

### 2026-04-06 第五周新增
- **技术教程类/WayinVideo-AI-Clipping-Skill解析.md** — 四大能力（AI剪辑+时刻搜索+摘要+转录）合一，WayinVideo商业API封装
- **技术教程类/VideoARM-Video-Reader-Skill解析.md** — 子Agent编排架构，OBSERVE→THINK→ACT→MEMORY循环，支持置信度输出
- **技术教程类/Video-Summary-Skill多平台视频摘要解析.md** — B站/小红书/抖音/YouTube多平台统一摘要入口
- **通用工具/大模型视频理解能力横向对比2026.md** — Gemini 2.5 Pro/Flash vs Claude 3.7 Sonnet Extended vs GPT-4.1，选型决策树+成本对比

### 2026-04-06 第四周新增
- 通用工具/Gemini-2.5-视频理解解析.md — VideoMME 85.2%超越人类，原生多模态+6小时
- 技术教程类/OpenClaw-video-vision技能解析.md — FFmpeg帧提取+Vision AI，支持代理/Cookie
- 技术教程类/video-analyzer-Skill解析.md — yt-dlp+whisper-cpp零成本本地转录
- 通用工具/Video-Learn-Skill解析.md — 多平台基础元数据提取前置工具

### 2026-04-04 第三周新增
- 通用工具/场景检测与语义切分方法.md
- 通用工具/短视频与直播流解析方案.md
- 通用工具/Video-R1视频推理能力解析.md
- 视频解析方法总结-2026-04-04.md

### 2026-04-03 第二周新增
- 技术教程类/视频结构化解析Prompt工程进阶.md
- 通用工具/多模态RAG视频语义检索全链路方案.md
