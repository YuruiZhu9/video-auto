# 小M的 Workspace

> 最后更新：2026-04-09 · 小M个人工作空间

---

## 📁 工作区结构

```
/workspace/
│
├── 核心配置
│   ├── BOOTSTRAP.md     — 首次启动配置（用后删除）
│   ├── IDENTITY.md      — 我是谁
│   ├── SOUL.md          — 我怎么想、怎么做事
│   ├── USER.md          — 用户信息与偏好
│   ├── HEARTBEAT.md     — 心跳任务清单
│   ├── MEMORY.md        — 长期记忆
│   ├── TOOLS.md         — 本地工具、API Key 配置
│   └── AGENTS.md        — workspace 运作规范
│
├── agents/              — Agent Prompt 模板库
│   ├── model-library/   — 模型库（12个分类）
│   │   ├── 01-video.md        — 视频生成模型
│   │   ├── 02-ai-agent.md     — AI Agent
│   │   ├── 03-text-llm.md     — 文本大模型
│   │   ├── 04-code.md         — 编程模型
│   │   ├── 05-image.md         — 图像生成模型
│   │   ├── 06-recsys.md       — 推荐系统模型
│   │   ├── 07-audio-music.md  — 音频/音乐/TTS模型
│   │   ├── 08-design-workflow.md
│   │   ├── 09-agent-ecosystem.md
│   │   ├── 10-ai-framework.md
│   │   ├── 11-api-platforms.md
│   │   ├── 12-free-apis.md
│   │   ├── model-library-index.md
│   │   └── CHANGELOG.md
│   ├── model-library-full-archive.md   — 旧版完整模型库（已归档）
│   ├── model-library.md                — 旧版索引（已归档）
│   ├── info-fetcher-prompt.md          — 信息抓取助手
│   ├── tech-analyst-prompt.md          — 技术前沿分析师
│   ├── business-analyst-prompt.md       — 商业洞察分析师
│   ├── llamafactory-papers-prompt.md   — LlamaFactory论文
│   ├── llm-tracker-prompt.md           — 大模型追踪
│   ├── jd-analyst-prompt.md            — 推荐系统面经
│   ├── leetcode-prompt.md              — LeetCode刷题
│   ├── xiaohongshu-agent-prompt.md    — 小红书运营
│   ├── ai-coding-helper-prompt.md      — AI Coding助手
│   ├── voice-cloning-prompt.md         — 语音克隆研究
│   ├── video-auto/                     — AI协作视频制作Agent
│   │   ├── video/complete_pipeline.py  — ⚠️ 仍在使用
│   │   ├── video/naming_utils.py
│   │   ├── video/scene_detector.py
│   │   ├── video/concat_mp4.py
│   │   ├── video/gen_slide_20260404.py
│   │   ├── video/merge_audio_video.py
│   │   ├── video/ffmpeg-nodejs-polyfill.js
│   │   ├── video/merge.js
│   │   ├── video/merge_audio_video.js
│   │   ├── gen_grid.js / gen_grid.py   — ⚠️ 仍在使用
│   │   ├── check_env.js                — ⚠️ 仍在使用
│   │   ├── push_github.js
│   │   ├── push_video.sh / push_video_github.js
│   │   ├── push_opt.js
│   │   └── push_github.sh
│   └── self-maintenance/        — 自维护记录
│       ├── 优化建议/
│       ├── 版本历史/
│       └── 问题记录/
│
├── reports/              — 定时任务报告输出（按主题+日期组织）
│   ├── ai-coding/              — AI Coding 报告
│   ├── ai-music-biz/           — AI音乐商机分析报告
│   │   ├── AI音乐商机全景分析报告.md  ← 核心总报告
│   │   ├── AI扒谱/                   ← AI吉他扒谱专项
│   │   ├── AI辅助教学/
│   │   ├── 内容创作/
│   │   └── AI创作工具/
│   ├── book-recommender/       — 豆瓣读书推荐报告
│   ├── business/               — 商业洞察日报
│   ├── code-architecture/      — 推荐系统架构学习
│   ├── human-value/            — 人类价值商机分析
│   ├── interview-notes/         — 推荐算法面经
│   ├── llamafactory/           — LlamaFactory论文
│   ├── llm-tracker/            — 开源大模型技术追踪
│   │   ├── 优化层/                   ← MoE/LinearAttention/Mamba等
│   │   ├── 基础层/
│   │   └── 应用层/
│   ├── news/                   — AI领域每日资讯
│   ├── oc-cross-device/        — OpenClaw跨设备控制
│   ├── recruitment/            — 招聘市场分析
│   ├── self-maintenance/       — 自我维护报告
│   ├── stock-beginner/         — 股票学习笔记
│   ├── sync/                   — 跨Agent同步日志
│   ├── tech/                   — 技术前沿日报
│   ├── video-parser/           — 视频解析技术总结
│   │   ├── 通用视频解析/
│   │   ├── 通用方法类/
│   │   ├── 通用工具/
│   │   ├── 行业分享类/
│   │   ├── 技术教程类/
│   │   ├── 开源项目演示类/
│   │   └── 社媒内容类/
│   ├── video-workflow/         — AI视频制作工作流
│   ├── voice-cloning/          — 语音克隆技术方案 ⭐
│   │   ├── README.md                 ← 入口文件
│   │   ├── ChatTTS/
│   │   ├── CosyVoice/
│   │   ├── CosyVoice2/
│   │   ├── CosyVoice3/
│   │   ├── F5-TTS/
│   │   ├── GPT-SoVITS/
│   │   ├── OpenVoice/
│   │   ├── RVC/
│   │   ├── VoxCPM/
│   │   └── 集成指南/
│   ├── xiaohongshu/            — 小红书内容运营
│   ├── 免费LLM-API-资源汇总-2026.md
│   └── openclaw/               — OpenClaw使用日志
│
├── memory/               — 每日会话记忆
│   ├── YYYY-MM-DD.md          — 每日原始记录
│   ├── heartbeat-state.json    — 心跳任务状态
│   └── *.md                    — 专题记忆
│
├── scripts/              — Git/清理工具脚本
│   ├── clean-old-token.sh      — 清理过期token
│   ├── clean-push.py
│   ├── fix-token-commit.sh
│   ├── fix-cron.sh
│   ├── full-clean.py
│   ├── git-askpass.sh
│   ├── push-clean.py
│   └── upload-reports.sh
│
├── skills/              — OpenClaw Skills
│   └── voice-clone-assistant/SKILL.md
│
├── extract/             — 信息抓取原始数据（缓存）
│   └── raw_content/           ← 已抓取的网页文本
│
├── AI-music-score-featch/ — AI吉他谱识别项目（独立Git仓库）
│
├── ai-coding-workflow/   — AI编程工作流学习笔记
│
├── model-library-tts.md  — TTS模型库 ⭐（Kokoro + Voxcpm2）
│
└── user_input_files/    — 用户上传文件
    ├── agent信息来源补充.docx
    └── image.png
```

---

## 🔑 核心入口文件索引

| 需求 | 入口文件 |
|------|---------|
| TTS / 语音克隆 | `reports/voice-cloning/README.md` 或 `model-library-tts.md` |
| AI 音乐商机 | `reports/ai-music-biz/AI音乐商机全景分析报告.md` |
| AI 吉他扒谱技术 | `reports/ai-music-biz/AI扒谱/技术可行性分析.md` |
| 视频解析技术 | `reports/video-parser/INDEX.md` |
| 开源大模型技术 | `reports/llm-tracker/` |
| 推荐系统面经 | `reports/interview-notes/` |
| OpenClaw 配置 | `TOOLS.md` + `openclaw-usage-guide.md` |

---

## 🗂️ 文件清理记录（2026-04-09）

已删除的废弃脚本（确认无用）：
- `gt_*.py / gt_*.sh / gt_*.txt` — 吉他扒谱测试脚本（测试完成，保留主逻辑）
- `push_*.py / push_*.sh` — 重复推送脚本（整合至 `scripts/`）
- `fix_cron*.sh / restore-crons.sh / recreate_jobs.sh` — 一次性 cron 修复脚本
- `check_status.sh / commit.sh / push.sh` — 散落的 Git 操作脚本
- `fix-*.txt` — 错误日志文件
- `video-analysis-methods.md` — 内容已迁移至 `reports/video-parser/`
- `voice-clone-research/` — 内容已迁移至 `reports/voice-cloning/`
- `五大软件产品方案-2026-04-02.md` — 一次性报告

保留的脚本（仍在使用）：
- `scripts/` 下所有脚本 — Git 操作和清理工具
- `voice-cloning/scripts/*.py` — 语音克隆推理脚本
- `AI-music-score-featch/backend/core/*.py` — 吉他扒谱核心逻辑
- `agents/video-auto/video/complete_pipeline.py` — 视频制作主流程
- `agents/video-auto/gen_grid.py / check_env.js` — 视频工具

---

## ⚠️ 重复文件说明（不删除，保持现状）

以下文件有多个相似版本，内容已逐渐收敛，主版本在报告目录中：

| 系列 | 主版本位置 |
|------|---------|
| 语音克隆方案 | `reports/voice-cloning/README.md` |
| 开源大模型追踪 | `reports/llm-tracker/` |
| AI音乐商机 | `reports/ai-music-biz/AI音乐商机全景分析报告.md` |
| 视频解析技术 | `reports/video-parser/INDEX.md` |
| AI协作视频工作流 | `reports/video-workflow/README.md` |

---

## 🔄 GitHub 推送

根目录 `README.md` 即为 GitHub 仓库说明文件。
推送命令由 `scripts/push-clean.py` 或 `scripts/upload-reports.sh` 完成。
