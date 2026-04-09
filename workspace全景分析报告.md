---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 71de58f45f61707f09ef702e99c0249b
    PropagateID: 71de58f45f61707f09ef702e99c0249b
    ReservedCode1: 3045022100e0138d9a086d0b27276452c9a0c1c2fe08238f9b82c09b1b240c5f48ba146b9f02207bbd478b1068ff8dd512d6e8ea7bbd99191ec20951bd987157cdffe576b4c88c
    ReservedCode2: 30460221009c439616919d678a6104dddfd8807117fcad1484d26eed29d94ac10f6993b43d022100dece1900064b3df5dd97c78c2376bc27a370334b59fc91681043a841b649c34d
---

# Workspace 全景分析报告

> 🤖 由小M 整理 | 最后更新：2026-04-09
> 本文件为 Workspace 全局地图，同时作为 GitHub 仓库 README 使用。

---

## 📁 目录结构

```
/workspace/
├── AGENTS.md              # Workspace 宪法（必读）
├── SOUL.md                # 小M 人格定义
├── USER.md                # 用户信息与偏好
├── IDENTITY.md            # 小M 身份卡
├── MEMORY.md              # 小M 长期记忆
├── HEARTBEAT.md           # 心跳任务配置
├── TOOLS.md               # 工具配置（API/模型/技能索引）
├── README.md              # 本文件
│
├── agents/                # Agent 角色定义 & 任务提示词
│   ├── info-fetcher-prompt.md          # 信息抓取助手
│   ├── tech-analyst-prompt.md           # 技术前沿分析师
│   ├── business-analyst-prompt.md      # 商业需求洞察分析师
│   ├── voice-cloning-prompt.md         # 语音克隆方案分析 Agent
│   ├── ai-music-biz-prompt.md           # AI+音乐商机探索 Agent
│   ├── ai-guitar-tab-dev-task-prompt.md # AI 吉他扒谱开发 Agent
│   ├── video-workflow-prompt.md         # AI 协作视频制作 Agent
│   ├── video-auto/                      # 独立视频自动流水线
│   │   ├── AGENTS.md
│   │   ├── input/  · topic.txt / material.md（待处理任务）
│   │   ├── video/  · slides/  · content/
│   │   └── logs/
│   ├── voice-cloning/                   # 语音克隆独立 Agent
│   ├── ai-coding-helper-prompt.md       # AI Coding 助手
│   ├── self-maintenance-prompt.md       # Agent 自我维护
│   ├── llm-tracker-prompt.md            # 开源大模型技术追踪
│   ├── tech-sync-center-prompt.md       # 跨 Agent 新技术同步中心
│   ├── openclaw-prompt.md               # OpenClaw 配置专家
│   ├── oc-cross-device-prompt.md        # 跨设备控制 OpenClaw 方案
│   ├── jd-analyst-prompt.md             # 招聘 JD 分析
│   ├── book-recommender-prompt.md      # 豆瓣书籍推荐
│   ├── stock-beginner-prompt.md        # 股市趋势分析
│   ├── human-value-analyst-prompt.md    # 人类价值市场分析师
│   ├── leetcode-prompt.md               # LeetCode 刷题助手
│   ├── llamafactory-papers-prompt.md   # LlamaFactory 论文资源
│   ├── xiaohongshu-agent-prompt.md     # 小红书内容运营
│   ├── video-parser-prompt.md          # 视频解析方法总结
│   ├── code-architecture-prompt.md     # 代码架构思维提升
│   ├── model-library.md                # AI 模型库（技术追踪）
│   └── model-library-full-archive.md   # 模型库完整存档
│
├── reports/                 # 所有分析报告输出目录
│   ├── news/                # AI 资讯日报
│   │   ├── 2026-02/  2026-03/  2026-04/
│   │   └── YYYY-MM-DD.md 格式
│   ├── tech/                # 技术前沿分析报告
│   │   ├── 2026-02/  2026-03/  2026-04/
│   ├── business/            # 商业洞察报告
│   │   ├── 2026-02/  2026-03/  2026-04/
│   ├── openclaw/            # OpenClaw 使用与配置报告
│   │   ├── openclaw-usage-guide.md      # 使用指南
│   │   └── openclaw-config-review.md   # 配置诊断
│   ├── voice-cloning/        # 语音克隆完整技术报告（权威）
│   │   ├── 选型指南/
│   │   ├── 集成指南/
│   │   ├── 生态地图/
│   │   ├── GPT-SoVITS/  CoquiXTTS/  CosyVoice/  CosyVoice2/  CosyVoice3/
│   │   ├── F5-TTS/  Fish-Audio-S2/  OpenVoice/  Orpheus-TTS/
│   │   ├── ChatTTS/  Kokoro-82M/  VoxCPM/  XTTS-v2/
│   │   ├── Qwen3-TTS/  GLM-TTS/  MOSS-TTS/  MegaTTS3/
│   │   ├── IndexTTS/  OmniVoice/  Silma-TTS/  Sesame-CSM/
│   │   └── [更多 TTS 模型子目录]
│   ├── ai-music-biz/        # AI+音乐商机分析报告
│   │   ├── AI扒谱/           # 核心方向：视频→吉他TAB
│   │   ├── AI辅助教学/
│   │   ├── AI创作工具/
│   │   └── 内容创作/
│   ├── ai-coding/           # AI Coding 工作流与最佳实践
│   ├── ai-qa/               # AI Agent 协作调研报告
│   │   └── ai-qa-report-final.md
│   ├── recruitment/         # 推荐系统算法面试面经
│   │   └── recommendation-thoughts.md
│   ├── video-workflow/      # AI 协作视频制作
│   │   ├── 工作流/  工具/  技巧总结/
│   │   └── AI协作视频结果.md
│   ├── video-parser/        # 视频解析技术总结
│   │   ├── 通用视频解析/  通用方法类/  技术教程类/
│   │   ├── 社媒内容类/  行业分享类/  开源项目演示类/  通用工具/
│   ├── llm-tracker/         # 开源大模型追踪
│   │   ├── 基础层/  优化层/  应用层/
│   ├── llamafactory/         # LlamaFactory 论文资源
│   ├── oc-cross-device/     # 跨设备 OpenClaw 方案
│   │   ├── 设计文档/  部署指南/  代码实现/  docker/
│   ├── code-architecture/  # 代码架构思维
│   │   ├── 知识点/  学习路径/  练习册/  代码案例/  踩坑记录/
│   ├── book-recommender/   # 书籍推荐报告
│   │   ├── 2026-03/  2026-04/
│   ├── human-value/        # 人类价值市场分析
│   │   ├── 2026-03/  2026-04/
│   ├── stock-beginner/     # 股市趋势分析
│   │   ├── 2026-03/  2026-04/  趋势分析/
│   ├── xiaohongshu/        # 小红书内容运营
│   │   ├── 2026-03-22/  2026-03-25/
│   │   └── materials/
│   ├── sync/               # 跨 Agent 同步报告（Agent 间通信记录）
│   │   ├── 2026-03/  2026-04/
│   ├── self-maintenance/   # Agent 自我维护日志
│   └── interview-notes/    # 推荐系统算法面经（按日生成）
│
├── memory/                  # 每日会话记忆 & 任务记录
│   ├── YYYY-MM-DD.md        # 每日原始记忆（按日期）
│   ├── heartbeat-state.json # 心跳状态追踪
│   ├── heartbeat-notes.txt  # 心跳备注
│   ├── business-insights.md # 商业洞察长期记忆
│   ├── leetcode-progress.md # 刷题进度追踪
│   ├── ai-music-progress.md # AI 扒谱项目进度
│   └── [各专项记忆文件]
│
├── model-library-tts.md     # 🎵 TTS 模型完整评测库（权威文档）
│                             # 包含 Kokoro-82M / VoxCPM / GPT-SoVITS 等
│                             # 所有语音相关技术参考的首要文档
│
├── AI-music-score-featch/   # AI 吉他扒谱 Web 应用（独立 Git 仓库）
│                             # GitHub: YuruiZhu9/AI-music-score-featch
│   ├── backend/   frontend/   model_cache/
│   ├── outputs/   test_audio/ uploads/   tests/
│   └── [架构/设计/部署文档]
│
├── ai-coding-workflow/      # AI Coding 工作流沉淀
│   ├── workflow/  phases/  patterns/  notes/
│
├── extract/                 # 外部内容抓取缓存
│   └── raw_content/
├── imgs/                    # 图片资源
├── skills/                  # OpenClaw 技能包
│   └── voice-clone-assistant/
├── tmp/                     # 临时文件（.gitignore 已排除）
├── user_input_files/        # 用户上传的原始文件
│   ├── agent信息来源补充.docx
│   └── image.png
│
├── .env                     # 环境变量（不提交）
├── .gitignore               # Git 忽略规则
├── .github-token            # GitHub Token（不提交）
└── voice-cloning/           # 语音克隆环境脚本
    ├── env_setup.sh         # 环境安装脚本
    └── scripts/            # 各模型推理脚本
```

---

## 📊 关键文件说明

### 根目录核心文件
| 文件 | 用途 |
|------|------|
| `TOOLS.md` | API密钥、模型配置、TTS模型索引 |
| `model-library-tts.md` | TTS/语音克隆模型完整评测报告 |
| `AGENTS.md` | Workspace 运行规则宪法 |
| `MEMORY.md` | 小M 长期记忆 |
| `HEARTBEAT.md` | 心跳任务配置 |

### Agent 核心任务（定时）
| Agent | 调度时间 | 任务 |
|-------|---------|------|
| 信息抓取助手 | 09:00 / 18:00 | AI 资讯日报 |
| 技术前沿分析师 | 11:30 / 19:30 | 技术报告 + JD分析 |
| 商业洞察分析师 | 19:30 | 商机发现 |
| AI+音乐商机探索 | 19:40 | 吉他扒谱/AI音乐 |
| OpenClaw 配置专家 | 22:30 | OpenClaw 动态追踪 |
| 小红书内容运营 | 05:00 / 07:30 | 内容抓取+发布 |
| LeetCode 刷题助手 | 07:00 | 推荐算法题 |
| AI Coding 助手 | 09:00 | AI Coding 最佳实践 |
| 推荐系统面经搜集 | 10:00 | 面试题解析 |
| AI 协作视频制作 | 20:00 | 视频流水线 |
| GitHub 自动上传 | 20:00 | 推送 reports 到 GitHub |
| AI Guitar Tab Dev | 14:00 / 16:30 | 扒谱代码开发 |
| Git 仓库每日同步 | 03:00 | 三仓库同步 |

---

## 🗂️ 文件清理记录（2026-04-09）

### 已删除的一次性脚本
- `scripts/clean-old-token.sh` — 已完成 token 清理
- `scripts/fix-token-commit.sh` — 已完成 token 修复
- `scripts/git-askpass.sh` — 含明文 GitHub Token，**安全风险**，已删除
- `scripts/fix-cron.sh` — cron job 不再引用，已删除
- `scripts/push-clean.sh` — 已完成历史清理
- `scripts/upload-reports.sh` — cron job 改用直接 push，已删除
- `scripts/clean-push.py` / `full-clean.py` / `push-clean.py` — 均为一次性清理脚本，已删除

### 已删除的残留数据
- `paper_detail_3436.json` / `paper_detail_3437.json` — arXiv 残留
- `papers_raw.json` / `papers_page2.json` — arXiv 残留
- `语音克隆方案报告.md` — 内容已整合至 `model-library-tts.md`

### 已归档的报告（移入 reports/）
- `AI协作视频结果.md` → `reports/video-workflow/`
- `openclaw-config-review.md` → `reports/openclaw/`
- `openclaw-usage-guide.md` → `reports/openclaw/`
- `ai-qa-report-final.md` / `ai-qa-report-v2.md` → `reports/ai-qa/`
- `recommendation-thoughts.md` → `reports/recruitment/`

---

## 🔗 GitHub 仓库

| 仓库 | 地址 | 内容 |
|------|------|------|
| Workspace 主仓库 | github.com/YuruiZhu9/Maxclaw- | 本 workspace |
| AI 吉他扒谱 | github.com/YuruiZhu9/AI-music-score-featch | Web 应用代码 |
| Video 自动流水线 | github.com/YuruiZhu9/video-auto | 视频生成内容 |

---

## 📝 注意事项

1. **Token 安全**：`git-askpass.sh` 含有明文 Token 已彻底删除，所有 Git 操作现已改用 `.github-token` 文件或 cron job 内嵌 Token
2. **定时任务监控**：HEARTBEAT.md 负责监控所有 cron job 状态，连续失败3次会发送钉钉提醒
3. **memory/ 日记忆**：所有每日产生的分析结果会同步写入 memory/ 目录，长期洞察写入 MEMORY.md
4. **model-library-tts.md**：TTS 模型权威文档，所有语音相关 Agent 均应引用此文件
