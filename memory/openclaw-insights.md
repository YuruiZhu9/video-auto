# OpenClaw 配置心得（长期记忆）

## 2026-03-26 配置周刊要点

### GitHub Star 突破 31 万 + NVIDIA GTC 亮相
- CNBC、Forbes、Malwarebytes 等主流媒体报道
- OpenClaw 亮相 NVIDIA GTC 2026 大会主题演讲
- freeCodeCamp 完整教程上线（2026-03-23）

### 版本：2026.3.10（89项更新）+ 2026.3.12
- GPT-5.4 原生支持 + 上下文引擎插件 + lossless-claw
- Telegram 主题级别智能体路由隔离（新功能）
- Discord 断连重连修复 + 持久化频道绑定
- Docker 多阶段构建优化 + 西班牙语界面

### 安全预警（紧急）
- CNNVD：2026.1-3月共82个漏洞（超危12/高危21）
- 2026.3.22：CNCERT + 中国网络空间安全协会联合发布《OpenClaw安全使用实践指南》
- 2026.3.7 版本插件迁移崩溃问题（已知问题）
- 建议：立即 `openclaw security audit --deep` + `openclaw update`

### 钉钉接入新坑（2026-03-26 更新）
- ACK 太慢导致只能收到第一条消息 → 先 ACK 再异步处理
- 环境变量未继承 → 直接写入 openclaw.json
- event.type 实际是 "gateway" 而非 "gateway:startup"
- zod.toJSONSchema() 报错 → 改用手写 JSON schema

### Pi 是唯一 Coding Agent
- 旧版 Claude/Codex/Gemini/Opencode 路径全部移除
- Node ≥ 22 强制要求

### 定时任务推荐配置
```bash
openclaw cron add --name "OpenClaw配置专家日报" \
  --cron "0 22 * * *" \
  --session isolated \
  --message "生成今日OpenClaw技术周报" \
  --announce --channel dingtalk \
  --to "03003745585526383319"
```

### 多 Agent Skill 推荐
- agent-council（任务分派+结果聚合+冲突协调）⭐
- agent-browser、self-improving-agent、tavily-search

### 关键链接
- 官方文档：https://docs.openclaw.ai/zh-CN
- 中文社区：https://clawd.org.cn
- ClawHub：https://clawhub.com
- 阿里云部署：https://www.aliyun.com/activity/ecs/clawdbot

---

## 2026-03-09 配置周刊要点

### 本周热点
- OpenClaw 2026.3.7 版本发布
- Star 突破 28 万，成为 GitHub 最热门开源项目
- 央视报道，腾讯云官方活动推广
- 上下文引擎插件 (Context Engine Plugin) 上线
- 记忆热插拔功能
- GPT-5.4 模型支持

### 定时任务配置
- 任务存储：`~/.openclaw/cron/jobs.json`
- 支持 at/every/cron 三种调度类型
- 隔离会话模式支持消息推送

### 多 Agent 路由
- 支持 WhatsApp/Telegram/Discord 多账号绑定
- 路由优先级：peer > accountId > 渠道 > 默认

### 常见问题解决
- 权限问题：tools.profile 需设为 coding
- 浏览器启用：browser.enabled: true
- 钉钉 405：启用 chatCompletions 端点

---

## 2026-03-08 配置周刊要点

### 安全预警（重要！最新变更）
- ⚠️ OpenClaw 2026.3.2 重大安全升级
- **新安装默认权限从 `messaging` 开始**（不再默认 broad/coding）
- 需手动配置：`openclaw config set tools.profile coding`
- 需清空 allowlist：`openclaw config set tools.allow '[]'`
- 执行 `openclaw gateway restart` 生效

### 历史时刻
- OpenClaw 超越 React，成为 GitHub Star 榜第一（26.9万+⭐）
- 2026年3月期间版本快速迭代：2.25 → 2.26 → 3.1 → 3.2

### 2026.3.2 版本更新
- 新权限系统：minimal/messaging/coding/full 四级
- 浏览器功能需手动启用：`browser.enabled: true`
- 需切换到系统 Chrome：`browser.defaultProfile: "chrome"`

### 快速安装
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### 启用完整权限（必做）
```bash
openclaw config set tools.profile coding
openclaw config set browser.enabled true
openclaw config set browser.defaultProfile "chrome"
openclaw config set tools.allow '[]'
openclaw gateway restart
```

### 国内大模型配置
1. **阿里云百炼（通义千问）** - 需完成实名认证
2. **DeepSeek** - 直接配置 API Key
3. **Moonshot (Kimi)** - 支持 256K Context Window
4. **智谱 GLM** - API地址 `https://open.bigmodel.cn/api/anthropic`

### 常用命令
- `openclaw status` - 查看状态
- `openclaw health` - 健康检查
- `openclaw gateway start/stop/restart` - Gateway 管理
- `openclaw doctor` - 诊断问题
- `openclaw update --channel beta/dev/stable` - 切换更新渠道

### 配置文件位置
- 主配置：`~/.openclaw/openclaw.json`
- 环境变量：`~/.openclaw/.env`

### 安全建议
- Gateway 绑定 127.0.0.1（本地）
- 使用环境变量管理 API Key
- 定期执行 `openclaw security audit --deep`
- 限制文件操作仅在工作空间：`tools.fs.workspaceOnly: true`

### 常见问题
- 安装卡住：使用国内镜像 `npm config set registry https://registry.npmmirror.com`
- 发消息没反应：检查 Gateway 状态和配对
- 钉钉 405 错误：启用 chatCompletions 端点
- 钉钉 401 错误：检查 gateway.auth 中的 token/password

---

## 2026-03-18 配置周刊要点

### 定时任务配置详解（官方文档更新）
- 三种调度类型：at（一次性）/ every（间隔）/ cron（定时）
- 任务持久化：`~/.openclaw/cron/jobs.json`
- 支持多渠道投递：WhatsApp/Telegram/Discord/Slack/钉钉
- 执行模式：main（主会话）/ isolated（隔离会话）

### 常用 Cron 表达式
- `0 7 * * *` - 每天早上 7 点
- `0 22 * * *` - 每天晚上 10 点
- `0 6 * * 1` - 每周一早上 6 点

### 配置模板
```bash
# 每日早报投送到钉钉
openclaw cron add --name "Daily report" --cron "0 22 * * *" --session isolated --message "生成今日技术周报" --announce --channel dingtalk --to "03003745585526383319"
```

### 常见问题
- 钉钉 405：启用 chatCompletions 端点
- 钉钉 401：检查 auth token/password

---
*更新于 2026-03-18*

## 2026-03-16 配置周刊要点

### 本周热点
- OpenClaw 2026.3.12 版本发布（连续两版更新）
- GPT-5.4 原生支持
- 200+ Bug 一次性修复
- GitHub Star 突破 28 万

### 安全预警（重要！）
- ⚠️ 2026.2.25 版本修复 Gateway 高危漏洞
- 建议立即升级：`openclaw update`
- 审计并撤销不必要凭证

### 15个高频报错解决方案
- npm error code 128：配置国内镜像
- Web 界面无法访问：检查端口/防火墙
- 钉钉 405：启用 chatCompletions 端点
- 钉钉 401：检查 auth token/password

### 性能优化
- 限定 CUDA 设备与显存分配
- 提升 gRPC 并发与 KeepAlive
- 启用 MMAP 模型加载
- 降低日志级别禁用 metrics

### 资源推荐
- 官方文档：https://docs.openclaw.ai/zh-CN
- 中文站：https://openclaw.cc/
- Awesome-OpenClaw-Skills：数千技能包

---
*更新于 2026-03-16*

## 2026-03-20 配置周刊要点

### 本周热点
- GitHub Star 突破 28 万
- Windows/macOS/Linux 全平台教程涌现
- 多飞书机器人配置指南发布

### 定时任务配置（4种方式）
1. `openclaw cron add` 命令
2. 手动编辑 `~/.openclaw/cron/jobs.json`
3. 系统 crontab + Shell 脚本
4. Workflow 时间触发

### 常见问题解决
- CUDA 初始化失败：`nvidia-smi` + `nvcc --version` 检查
- ClawModule 加载失败：`pip install -e .`
- 钉钉 405：启用 chatCompletions 端点
- 钉钉 401：检查 auth token/password

### 最佳实践
- 启用多 Agent 协同架构
- 批量部署 Skill 插件
- 配置 Cron 定时任务实现无人值守

### 资源
- 官方文档：https://docs.openclaw.ai/
- 中文站：https://openclaw.cc/

---

## 2026-03-19 配置周刊要点

### 本周热点
- GitHub Star 突破 28 万
- Windows/macOS/Linux 全平台教程涌现
- 多飞书机器人配置指南发布

### 定时任务配置（4种方式）
1. `openclaw cron add` 命令
2. 手动编辑 `~/.openclaw/cron/jobs.json`
3. 系统 crontab + Shell 脚本
4. Workflow 时间触发

### 常见问题解决
- CUDA 初始化失败：`nvidia-smi` + `nvcc --version` 检查
- ClawModule 加载失败：`pip install -e .`
- 钉钉 405：启用 chatCompletions 端点
- 钉钉 401：检查 auth token/password

### 最佳实践
- 启用多 Agent 协同架构
- 批量部署 Skill 插件
- 配置 Cron 定时任务实现无人值守

### 资源
- 官方文档：https://docs.openclaw.ai/
- 中文站：https://openclaw.cc/

---
*更新于 2026-03-20*

---

## 2026-03-21 配置周刊要点

### 本周重大发现
- ⚠️ Pi 是唯一 coding-agent（旧的 Claude/Codex/Gemini/Opencode 路径已全部移除）
- Gateway 默认端口：18789（WS）/ 18793（HTTP Canvas）
- 仪表板必须用 `http://127.0.0.1:18789/` 本地访问，HTTP 直连 IP 会触发 `device identity required`

### 定时任务三种方式
1. CLI：`openclaw cron add --cron "0 22 * * *" --session isolated --announce --channel dingtalk`
2. jobs.json：`~/.openclaw/cron/jobs.json`
3. Crontab + Shell 脚本

### SubAgent 五种启用方式
1. 命令行 spawn（`/subagents spawn`）
2. AGENTS.md 规则触发
3. agentToAgent 工具
4. Coding Team Setup v2.0（`claw skill install coding-team-setup@v2.0`）
5. 飞书多账户物理隔离

### 常见问题
- 15个高频报错：EBADENGINE/EADDRINUSE/HTTP 429/AUTH_TOKEN_MISMATCH/cron scheduler disabled 等
- 快速诊断：`openclaw doctor --repair` > `openclaw logs --follow`

### 安全提醒
- Node ≥22，tools.profile=coding，allowlist 清空
- Gateway 绑定 127.0.0.1，API Key 用环境变量

### 资源
- 官方文档：https://docs.openclaw.ai/
- 中文站：https://openclaw.cc/

## 2026-03-23 配置周刊要点

### 本周重大发现
- ⚠️ Pi 是唯一 coding-agent（旧的 Claude/Codex/Gemini/Opencode 路径已全部移除）
- Gateway 默认端口：18789（WS）/ 18793（HTTP Canvas）
- 仪表板必须用 `http://127.0.0.1:18789/` 本地访问，HTTP 直连 IP 会触发 `device identity required`

### 定时任务三种方式
1. CLI：`openclaw cron add --cron "0 22 * * *" --session isolated --announce --channel dingtalk`
2. jobs.json：`~/.openclaw/cron/jobs.json`
3. Crontab + Shell 脚本

### SubAgent 五种启用方式
1. 命令行 spawn（`/subagents spawn`）
2. AGENTS.md 规则触发
3. agentToAgent 工具
4. Coding Team Setup v2.0（`claw skill install coding-team-setup@v2.0`）
5. 飞书多账户物理隔离

### 常见问题
- 15个高频报错：EBADENGINE/EADDRINUSE/HTTP 429/AUTH_TOKEN_MISMATCH/cron scheduler disabled 等
- 快速诊断：`openclaw doctor --repair` > `openclaw logs --follow`

### 安全提醒
- Node ≥22，tools.profile=coding，allowlist 清空
- Gateway 绑定 127.0.0.1，API Key 用环境变量

### 资源
- 官方文档：https://docs.openclaw.ai/
- 中文站：https://openclaw.cc/

## 2026-03-25 配置周刊要点

### GitHub Star 突破 31 万
- 引发 CNBC、Forbes 等主流媒体报道
- 亮相 NVIDIA GTC 大会主题演讲

### 2026.3.10 版本：89 项更新
- **Discord**：断连重连修复 + 持久化频道绑定
- **Telegram**：主题级别智能体路由隔离 + 持久化频道绑定（同一群组不同主题可运行不同 Agent）
- 新增西班牙语界面、Web 搜索升级、Docker 多阶段构建优化

### 多 Agent 协作 Skill 推荐（2026-03-24 最新）
- **agent-council** ⭐：任务分派 + 结果聚合 + 冲突协调（核心）
- agent-browser：浏览器自动化
- self-improving-agent：长期记忆优化
- tavily-search：实时事实验证
- messaging-integration：跨平台消息路由

### Telegram 多主题隔离（新功能）
- 同一群组不同 thread 可独立运行不同 Agent
- 配置：channels.telegram.threads[thread-id].agent

### 常用链接
- 官方文档：https://docs.openclaw.ai/
- 中文站：https://openclaw.cc/

---
*更新于 2026-03-27*

## 2026-03-24 配置周刊要点

### CNNVD 安全预警（紧急）
- CNNVD 统计 2026.1-3月：OpenClaw 漏洞共82个（超危12/高危21/中危47/低危2）
- 建议：立即 `openclaw update` + `openclaw security audit --deep`
- 2026.2.25/2.26 版本已修复高危漏洞

### 官方文档本周要点
- Node ≥ 22（强制）
- Pi 是唯一编码 Agent（Claude/Codex/Gemini/Opencode 旧路径全部移除）
- TCP 桥接已移除
- Gateway WS：18789，Canvas HTTP：18793
- 仪表板必须用 http://127.0.0.1:18789/（直连 IP 需 token）

### Telegram Bot 接入四法
- BotFather 创建 + 手动 Token
- openclaw onboard 向导（推荐）
- 环境变量 TELEGRAM_BOT_TOKEN
- 手动 JSON 配置

### 钉钉 401/405 速查
- 401：gateway.auth token/password 与钉钉后台不一致
- 405：channels.dingtalk.compatibilityMode: true

### 性能优化
- 多 Agent 协同架构、批量 Skill 插件（节省 60%+ token）
- CUDA 设备限定、MMAP 模型加载
- 腾讯云 Lighthouse 一键部署（25分钟）

---
*更新于 2026-03-23*

## 2026-03-23 配置周刊要点

### 本周重大动态
- 🎉 GitHub Star 突破 **31 万**（+3万/周），引发 CNBC 等主流媒体报道
- OpenClaw 亮相 NVIDIA GTC 大会主题演讲
- Forbes、Malwarebytes 等权威媒体专题报道
- freeCodeCamp 完整教程上线

### 版本重要变更
- ⚠️ Pi 是唯一 Coding Agent（Claude/Codex/Gemini/Opencode 旧路径全部移除）
- 令牌生成：向导默认生成网关令牌（回环地址也生成）
- TCP 桥接器已移除
- **Node ≥ 22 强制要求**

### 钉钉 401/405 速查
- 401：gateway.auth token/password 与钉钉后台不一致
- 405：`channels.dingtalk.compatibilityMode: true` 启用兼容模式
- 无响应：确认 Gateway 运行，检查端口 18789

### GitHub Actions 自动化部署
- 需 Node 22 + `openclaw gateway start`
- API Key 通过 secrets 注入
- 参考模板见报告

---
*更新于 2026-03-21*

## 2026-03-10 配置周刊要点

### 定时任务配置增强
- 官方文档：https://docs.openclaw.ai/zh-CN/automation/cron-jobs
- 任务存储：`~/.openclaw/cron/jobs.json`，持久化不丢失
- 支持三种调度：at（一次性）/ every（间隔）/ cron（定时）
- 隔离会话模式支持多渠道消息投递（WhatsApp/Telegram/Slack/钉钉）

### 定时任务 vs 心跳
- 定时任务：精确时间、持久化、支持消息投递
- 心跳：近似时间、内存临时、仅主会话

### 常用命令
- `openclaw cron add` - 创建任务
- `openclaw cron list` - 查看任务
- `openclaw cron runs` - 查看运行历史
- `openclaw cron edit` - 编辑任务
- `openclaw cron run --force` - 手动执行

### Cron 表达式示例
- `0 7 * * *` - 每天早上 7 点
- `0 22 * * *` - 每天晚上 10 点
- `0 6 * * 1` - 每周一早上 6 点

### 常见问题
- 定时任务没通知：检查 `--announce` + `--channel` + `--to` 参数
- 任务执行失败：使用 `--force` 手动重试

---
*更新于 2026-03-08*

---

## 2026-03-27 配置周刊要点

### v2026.3.13 不可变恢复版（2026-03-15）
- 紧急修复 v2026.3.13 插件迁移崩溃问题
- 覆盖：网关 / Agents / UI / 移动端 / Docker / 浏览器 / 安全

### 定时任务四种配置方式（官方最新推荐）
1. `openclaw cron add` CLI 命令（推荐新手）
2. 手动编辑 `~/.openclaw/cron/jobs.json`
3. 系统 crontab + Shell 脚本
4. Workflow 时间触发 YAML（复杂多步骤任务）

### 关键新增内容
- Telegram 主题级隔离（v2026.3.12+）：同一群组不同 thread 运行不同 Agent
- Cron 参数新增 `--tz "Asia/Shanghai"` 支持
- Workflow 定时触发：trigger.type=time，schedule=Cron表达式

### 常用安装命令
- agent-council：`npx clawhub@latest install agent-council`
- agent-browser：`npx clawhub@latest install agent-browser`
- tavily-search：`npx clawhub@latest install tavily-search`
- self-improving-agent：`npx clawhub@latest install self-improving-agent`

## 2026-03-27 配置周刊要点

### 史上最大规模更新（3月24日）
- 停更9天发布"史诗级"版本，官方：内容多到需单独做目录
- **ClawHub 官方插件市场正式上线**：`openclaw plugins install` 优先从市场搜索
- 模型升级：默认 GPT-5.4，MiniMax M2.5→M2.7，Per-agent 可独立选模型
- 新增 **/btw 轻量问答指令**，不改变当前上下文快速补充提问
- 安全四维升级：OpenShell/SSH沙盒 + 审批流程穿透 + 镜像/远程沙盒 + SecretRef
- ⚠️ 发布后翻车：Web UI资源遗漏、微信插件失效、第三方插件集体熄火
- ✅ 24小时内火速发布 v2026.3.23 修复数十个问题

### CNNVD 通报更新（82个漏洞）
- 超危12/高危21/中危47/低危2
- CVE-2026-28391（Windows cmd.exe命令注入）
- CVE-2026-28463（Exec Allowlist绕过任意文件读取）
- QVD-2026-13829（WebSocket共享令牌权限提升）

### 新配置技巧
- ClawHub 新API：`openclaw plugins install <name>`（替代 npx clawhub@latest install）
- Per-agent 模型独立选择（轻量任务nano，复杂推理5.4）
- 低配机6个轻量技能：shell-exec/file-read-write/datetime-query/weather-basic/text-summarize-light/http-request-simple
- Cron `--tz "Asia/Shanghai"` 参数（解决容器化时区漂移）
- 立即：`openclaw update` + `openclaw security audit --deep`

### SubAgent 五种方式
- 命令行spawn、AGENTS.md规则触发、agentToAgent跨体调用
- Coding Team Setup v2.0（批量初始化architect+developer+tester）
- 飞书多账户物理隔离

### 常用链接
- 官方文档：https://docs.openclaw.ai/
- 中文站：https://openclaw.cc/

---
*更新于 2026-03-27*

## 2026-03-30 配置周刊要点

### CVE-2026-28466（CVSS 9.4 新发！）
- Gateway node.invoke 请求未过滤参数，认证客户端可绕过 RCE
- 立即：openclaw update + openclaw doctor --security

### CNNVD 最新：283个漏洞（2026.1-3月）
- 超危12（新增CVE-2026-28470 exec白名单绕过/CVE-2026-27002 Docker沙箱/CVE-2026-28472 WebSocket身份缺陷）
- 高危21
- Top新漏洞：CVE-2026-28466（CVSS 9.4 RCE via node.invoke）

### v2026.3.24 最新版
- OpenAI API 兼容端点（/v1/models + /v1/embeddings）
- /tools 显示实际可用工具
- 7个核心Skill一键安装（自动检测依赖）
- CLI --container 参数

### Breaking Changes（持续）
- skill-vetter 正式推荐为必装安全扫描工具
- Chrome扩展 relay 已完全移除（v2026.3.22+）
- 环境变量 CLAWDBOT_*/MOLTBOT_* → OPENCLAW_*（持续清理）

### 本周必做
```bash
openclaw update && openclaw doctor --security
clawhub install skill-vetter
```

## 2026-04-02 配置周刊要点

### CVE-2026-32914（CVSS 8.7 高危）
- /config、/debug 接口权限校验缺失（command-authorized 未验证 owner）
- 影响版本：openclaw ≤ 2026.3.11，修复版本 ≥ 2026.3.12
- 紧急：`openclaw update && openclaw doctor --security`

### v2026.3.31 重要变更（2026-03-31）
- 后台任务统一 SQLite 账本管理，新增 `openclaw flows list|show|cancel`
- QQ Bot 官方通道上线（首个国内社交平台原生支持）
- 插件安装默认拒绝含 critical 安全问题的插件
- Gateway 令牌混用直接拒绝，节点命令需审批
- MCP 支持 HTTP/SSE 远程服务器

## 2026-04-01 配置周刊要点

### v2026.3.31（2026-03-31 最新版！）
- **QQ Bot 官方原生插件**：首个国内社交平台原生支持，完整支持私聊/群聊/富媒体
- **后台任务系统重构**：ACP/子代理/定时任务统一 SQLite 分类账管理，新增 `openclaw flows` 命令
- **安全三大收紧**：插件安装默认拦截危险代码 / Gateway 令牌混用拒绝 / Node 命令需配对审批
- **Plugin SDK 路径迁移**：`openclaw/extension-api/*` → `openclaw/plugin-sdk/*`
- **MCP 远程服务器**：`mcp.servers` 支持 HTTP/SSE 远程地址
- **Matrix 增强**：`historyLimit` 群组历史上下文 / HTTP 代理 / 流式回复草稿
- **WhatsApp Emoji 回应** / **Slack 审批内联完成** / **LINE 富媒体发送**

### v2026.3.28（2026-03-28/29）
- xAI / Grok → Responses API（原生联网搜索）
- **MiniMax 图像生成**（新增 image-01 模型）
- Qwen portal-auth **彻底移除**（需切换 Model Studio API Key）
- 旧配置迁移规则：超过2个月不再自动迁移，直接报错
- `requireApproval` 插件审批钩子（Telegram按钮/Discord交互支持）

### 必做
```bash
openclaw update && openclaw doctor --security
```
**如用 Qwen**：`openclaw onboard --auth-choice modelstudio-api-key`

---
*更新于 2026-04-01*

## 2026-04-03 配置周刊要点

### v2026.3.31 发布（2026-04-01）—— 零信任安全元年
- 从"默认信任"切换到"零信任执行模型"
- 五大核心安全变更：
  1. Nodes 执行入口统一：nodes.run() 废止 → exec(host="node")
  2. 插件 dangerous-code 扫描 fail closed（危险代码直接阻止安装）
  3. Gateway 不再信任 localhost（所有调用必须带 Authorization: Bearer TOKEN）
  4. Node 配对需审批才能执行命令
  5. Plugin SDK 路径迁移到 openclaw/plugin-sdk/*
- 立即：openclaw update && openclaw doctor --security

### 新功能亮点（v2026.3.31）
- 首个国内社交平台：QQ Bot 原生支持（私聊/群聊/频道/多媒体）
- 后台任务统一 SQLite 管理：openclaw flows list|show|cancel
- 插件 requireApproval Hook（Telegram/Discord 审批按钮）
- MCP 远程服务器 HTTP/SSE 支持
- Qwen portal-auth 彻底移除，需切换 Model Studio API Key

### 升级避坑实战（来源：margrop.net）
- 插件 SDK 不兼容：DingTalk Connector 0.8.3 报错 createPluginRuntimeStore
- 源码已修但错误还在：rm -rf /tmp/jiti 清 JIT 缓存
- 同一机器两份 OpenClaw：which vs systemd 实际调用不一致
- 边缘节点无法访问 npm：直接复制金丝雀已验证产物
- 升级策略：金丝雀节点验证 → 复制已验证产物 → 三重验证

### ClawHub 最新（截至 2026-04-03）
- self-improving-agent: 495k★ | gog: 316k★ | Summarize: 153k★ | Tavily: 145k★ | Ontology: 78k★
- skill-vetter 正式推荐为必装安全扫描工具

### 本周必做
- openclaw update && openclaw doctor --security
- 如用 Qwen：openclaw onboard --auth-choice modelstudio-api-key

---
*更新于 2026-04-04*

## 2026-03-31 配置周刊要点

### v2026.2.3（2026-02-05）版本重点
- **隔离 Cron announce 投递**：默认成功后删除一次性任务，新增 `--keep-after-run`
- **Cloudflare AI Gateway**：新增为模型提供商，支持 Workers AI 代理
- **Moonshot（.cn）**：新增认证选项，中国区更易接入
- 跨渠道 per-account responsePrefix 覆盖
- 安全：阻止 Slack/Discord 不信任元数据、沙盒化媒体路径

### ClawHub 热门 Skills TOP 5（截至 2026-03-31）
- self-improving-agent ⭐495 | gog ⭐316 | Tavily Search ⭐145 | Summarize ⭐153 | Github ⭐98

### 必做
- `openclaw update && openclaw doctor --security`

---
*更新于 2026-03-31*

## 2026-03-30 配置周刊要点

### CVE-2026-28466（CVSS 9.4 新发！）
- Gateway node.invoke 请求未过滤参数，认证客户端可绕过 RCE
- 立即：openclaw update + openclaw doctor --security

### CNNVD 最新：283个漏洞（2026.1-3月）
- 超危12（新增CVE-2026-28470 exec白名单绕过/CVE-2026-27002 Docker沙箱/CVE-2026-28472 WebSocket身份缺陷）
- 高危21
- Top新漏洞：CVE-2026-28466（CVSS 9.4 RCE via node.invoke）

### v2026.3.24 最新版
- OpenAI API 兼容端点（/v1/models + /v1/embeddings）
- /tools 显示实际可用工具
- 7个核心Skill一键安装（自动检测依赖）
- CLI --container 参数

### Breaking Changes（持续）
- skill-vetter 正式推荐为必装安全扫描工具
- Chrome扩展 relay 已完全移除（v2026.3.22+）
- 环境变量 CLAWDBOT_*/MOLTBOT_* → OPENCLAW_*（持续清理）

### 本周必做
```bash
openclaw update && openclaw doctor --security
clawhub install skill-vetter
```

---
*更新于 2026-03-30*

## 2026-03-27 配置周刊要点

### 三版本连发：v2026.3.22（架构升级）+ v2026.3.23（紧急补丁）+ v2026.3.24（功能增强）

### Breaking Changes（2026-03-23 新增）
- ClawHub 优先：插件安装优先从 ClawHub 查找，无才回退 npm
- Chrome 扩展中继已移除：`driver: "extension"` 废止
- 环境变量重命名：`CLAWDBOT_*` / `MOLTBOT_*` → 全部 `OPENCLAW_*`
- SDK 路径：`openclaw/extension-api` → `openclaw/plugin-sdk/*`

### v2026.3.22 新功能
- ClawHub 官方集成：`openclaw skills search/install/update`
- 多市场支持：clawhub: / claude: 前缀
- 默认 GPT-5.4，新增 gpt-5.4-mini/nano，MiniMax M2.7
- 飞书交互卡片、ACP 绑定、流式推理卡片
- Android 暗色主题、短信/通话记录搜索
- 新搜索：Exa、Tavily、Firecrawl
- 安全：韩文填充字符转义、remote file:///UNC 阻止、Webhook 恒定时间签名

### v2026.3.23 紧急修复
- 控制台 Web UI 打包遗漏（已修复）
- 微信插件失效（已修复）
- 第三方插件兼容性问题
- Mistral 422（token 限制过高，已修复）
- 子代理超时误报

### v2026.3.24 新功能
- OpenAI API 兼容：`/v1/models` + `/v1/embeddings` 端点，RAG 应用可直接用 OpenAI SDK
- 工具可见性：`/tools` 显示实际可用工具
- Microsoft Teams 官方 SDK 升级（流式回复/welcome卡片/typing指示器）
- 7个核心 Skill 一键安装（coding-agent、gh-issues、weather 等）
- CLI `--container` 参数
- Discord autoThreadName: "generated"
- Node 22.14+ 最低要求放宽
- 沙箱媒体访问修复（#54034）

### 本周必做
```bash
openclaw update
# 替换 CLAWDBOT_* 环境变量为 OPENCLAW_*
openclaw security audit --deep
```

### 推荐 Skills（v2026.3.22+）
```bash
openclaw skills install agent-council  # 多 Agent 协调
openclaw skills install coding-agent
openclaw skills install tavily-search
openclaw skills install self-improving-agent
```

---
*更新于 2026-03-27*

## 2026-03-28 配置周刊要点

### v2026.3.24 发布（体验优化）
- OpenAI API 兼容端点：/v1/models + /v1/embeddings，RAG 可直接用 OpenAI SDK
- /tools 显示实际可用工具（而非所有声明工具）
- Microsoft Teams 官方 SDK 升级（流式回复/welcome卡片/typing指示器）
- 7个核心 Skill 一键安装（coding-agent、gh-issues、weather等）
- Discord autoThreadName: "generated"，Node 22.14+ 最低要求放宽

### CVE-2026-25253（CVSS 9.8 紧急！）
- Gateway 远程代码执行漏洞，18789 端口，正被积极利用
- 暴露实例：135,000+（Bitdefender数据），+69%增长
- 立即：openclaw update + openclaw doctor --security
- 封堵防火墙 18789 外部访问，确认 gateway.bind=127.0.0.1

### ClawHub 安全升级
- VirusTotal 扫描：openclaw skill virustotal \<name\>
- 技能签名验证 Beta：openclaw skill install --signed-only \<name\>
- ClawHavoc 已清除 2,400+ 恶意技能，数千 API Key 泄露，强烈建议轮换

### Breaking Changes（3月必改）
- CLAWDBOT_*/MOLTBOT_* → OPENCLAW_* 环境变量
- Chrome 扩展 driver: "extension" 废止
- ClawHub 优先插件安装
- SDK 路径：openclaw/extension-api → openclaw/plugin-sdk/*

### Tencent 中文生态（3月新开源）
- 微信官方 Adapter（取代 WeChatFerry）
- 中文 STT 模型（比 Whisper 更准）
- 飞书 Lark Adapter
- 中文 SOUL.md 模板

### Nvidia NemoClaw GPU 加速
- openclaw config set execution.gpu.enabled true
- openclaw config set execution.gpu.runtime nvidia
- 支持：Ollama+CUDA 本地 LLM、browser-use GPU 渲染、Whisper 加速

### 记忆系统 v2 预览
- 向量化搜索 / 记忆分层 / 自动脱敏 / 跨 Agent 共享
- openclaw start --experimental-memory-v2 开启

---
*更新于 2026-03-28*

## 2026-03-29 配置周刊要点

### v2026.3.24 发布（2026-03-25，体验优化）
- 技能一键安装依赖：自动检测缺失 + 一键安装（最实用功能）
- Gateway 重启 session 恢复：断电/重启后对话不中断
- OpenAI 兼容端点：/v1/models + /v1/embeddings，RAG 可直接用 OpenAI SDK
- Microsoft Teams 官方 SDK 升级（流式回复/welcome卡片/typing指示器）
- CLI --container 参数：直接在 Docker/Podman 容器内操作 OpenClaw
- Node 最低版本从 22.22.0 放宽至 22.14+，推荐 Node 24

### CVE-2026-25253（CVSS 9.8 紧急！）
- Gateway 远程代码执行漏洞，18789 端口，正被积极利用
- 立即：openclaw update + openclaw doctor --security
- 封堵防火墙 18789 外部访问，确认 gateway.bind=127.0.0.1

### v2026.3.22+v2026.3.23 安全修复汇总
- 10+ 安全修复：Memory/exec/webhook/SSRF/pairing/Browser/CSRF
- Memory autoCapture 默认禁用，需显式开启防 PII 泄露
- Telegram webhook 需配置 webhookSecret
- Pairing 令牌升级为 256-bit base64url

### Breaking Changes（持续清理）
- CLAWDBOT_*/MOLTBOT_* → OPENCLAW_*（完全删除）
- driver: "extension" 已废止
- gateway.auth mode "none" 已删除
- SDK 路径：openclaw/extension-api → openclaw/plugin-sdk/*

### 推荐 Skills
- self-improving-agent（297k★）
- ontology（131k★）：知识图谱记忆
- Agent Browser（44k★）：无头浏览器自动化
- MoltGuard（18.9k★）：安全护栏
- OpenClaw Agent Optimize（8.3k★）：成本+路由优化

### 记忆系统 v2 预览
- --experimental-memory-v2 开启
- 向量化搜索 / 记忆分层 / 自动脱敏 / 跨 Agent 共享

### 常用链接
- 官方文档：https://docs.openclaw.ai/
- 中文站：https://openclaw.cc/
- ClawHub：https://clawhub.com/

---
*更新于 2026-04-04*

## 2026-04-04 配置周刊要点（本期重点：Anthropic 断供！）

### 🚨 Anthropic 正式切断 OpenClaw Claude 订阅支持（最高优先级！）
- **宣布时间**：2026-04-03（周五晚间）
- **生效时间**：太平洋时间 04-04 中午12点（北京时间 04-05 凌晨）
- **原因**：Anthropic 称第三方工具"对系统造成过大压力"，违反服务条款
- **创始人回应**：Peter Steinberger 曾说服 Anthropic 推迟一周，"他们选择在周五晚间悄悄发布"
- **用户应对**：申请独立 Claude API Key（开发者平台）/ 切换 DeepSeek/GLM/通义千问

### v2026.4.2 紧急发布（2026-04-03）
- **Task Flow 核心功能恢复**：托管 + 镜像同步模式，新增 `openclaw flows` 命令
- **破坏性变更**：xAI 插件 `x_search` 迁移到 `plugins.entries.xai.config.xSearch.*`，Firecrawl 迁移到 fetch-provider
- **安全增强**：TLS 传输保护 / QQ Bot 媒体路径限制 / 时间安全密钥比较
- **多平台优化**：Android 语音唤醒 / 飞书评论线程 / Matrix 规范元数据 / WhatsApp MIME 支持

### v2026.4.1 正式版（2026-04-02）
- **16 项新功能**：/tasks 会话面板 / SearXNG 搜索 / Bedrock Guardrails / macOS 语音唤醒 / 飞书评论优化 / Cron 工具白名单
- **28 项 Bug 修复**：Bedrock 工具不匹配 / SQLite 阻塞 / Telegram 按钮限制
- **新支持**：GLM-5.1 / GLM-5v-turbo（智谱 Z.AI provider）

### CVE 更新（截至 2026-04-04）
- 暂无新 CVE 记录，参照上周

### 版本信息
- 当前系统：需确认（建议升级到 v2026.4.2）
- 最新稳定版：v2026.4.2（2026-04-03）

### 必做
```bash
openclaw update
openclaw doctor --fix    # 自动迁移 xAI/Firecrawl 配置
openclaw doctor --security
clawhub install skill-vetter
```

---
*更新于 2026-04-04*


---

*更新于 2026-04-04*

## 2026-04-05 配置周刊要点（本期重点：Anthropic 正式断供！）

### Anthropic 正式切断 OpenClaw Claude 订阅支持
- 宣布时间：2026-04-03（周五晚间），生效：北京时间04-05凌晨
- 原因：Anthropic称第三方工具对系统压力过大
- 创始人Steinberger批评"周五晚间悄悄发布"，曾争取一周缓冲期
- 用户应对：申请Claude独立API Key / 切换DeepSeek/GLM/通义千问/MiniMax

### v2026.4.2（2026-04-03）
- Task Flow核心功能恢复，新增openclaw flows命令
- xAI插件x_search迁移，Firecrawl迁移至fetch-provider
- TLS传输保护/QQ Bot媒体路径限制

### v2026.4.1（2026-04-02）
- 16项新功能：/tasks面板、SearXNG、Bedrock Guardrails、GLM-5.1/5v-turbo
- 28项Bug修复

### ClawHub热门Skills TOP 5（2026-04）
- self-improving-agent、Find Skills、Skill Vetter、Multi Search Engine、Summarize

### 国内模型推荐
- 通用→豆包/火山引擎；长文档→智谱GLM-5.1；推理→DeepSeek R1；创意→MiniMax M2.7

### 必做
- openclaw config get | grep model（检查当前模型）
- 如用Claude订阅→立即切换国内模型
- openclaw update（安全审计）

---
*更新于 2026-04-05*

## 2026-04-06 配置周刊要点（本期头条：Anthropic 正式封禁 OpenClaw！）

### Anthropic 封禁事件（2026-04-04 正式生效）
- 太平洋时间4月4日中午12点，Claude订阅不再覆盖任何第三方工具
- Peter Steinberger与Anthropic谈判，仅成功推迟一周（3月28日）
- Anthropic 2-3月密集发布 Dispatch/Claude Code Channels/Computer Use——精确对标OpenClaw三项核心功能
- GitHub Issue #17118 曾涌入1,416 Reactions+410条评论，当日被单方面关闭
- **真实原因**：Claude Max $200/月被用出$5,000实际算力（25倍超额）
- **Peter Steinberger**：今年初已加入OpenAI（讽刺！）
- 补偿：一次性等额积分（限4月17日前）+全额退款+30%用量折扣

### Anthropic 封禁后三条出路
1. **国内兼容端点**：`providers.anthropic.baseUrl` → `https://api.qnaigc.com`
2. **独立 Claude API Key**：sk-ant-api03-前缀，不受OAuth封锁
3. **LobeHub**：开源替代，完全自研Agent基础设施，不依赖Anthropic

### Google Gemini 也封了！
- 2026年2月起绕过Gemini CLI配额的用户被永久封号，无法申诉

### v2026.4.2（2026-04-03）
- Task Flow核心功能恢复，新增openclaw flows命令
- GLM-5.1/GLM-5v-turbo正式支持
- xAI插件迁移（x_search→新路径），Firecrawl迁移至fetch-provider
- TLS传输保护默认开启

### 本周必做
- 升级到 v2026.4.2：npm install -g openclaw@latest
- 执行安全审计：openclaw doctor --security
- 4月17日前领取Anthropic补偿

### 长期建议
降低对单一模型厂商依赖，多模型并行（MiniMax/DeepSeek/GLM）

---
*更新于 2026-04-06*

## 2026-04-07 配置周刊要点（本期头条：三个 Critical CVE 紧急预警！）

### 三个 Critical CVE 紧急预警（2026-04）
- **CVE-2026-33579**（CVSS 9.9）：/pair approve 权限提升，影响 < v2026.3.28
- **CVE-2026-32917**（CVSS 9.8）：iMessage 附件暂存流程远程命令注入，影响 < v2026.3.13
- **CVE-2026-32916**（CVSS 9.4）：插件子代理路由授权绕过，影响 v2026.3.7~v2026.3.11
- OpenCVE 共计 20 个 CVE（Critical 3 / High 8 / Medium 8 / Low 1）

### v2026.4.2（2026-04-03 最新版）
- Task Flow 核心功能恢复 + `openclaw flows list|show|cancel`
- GLM-5.1 / GLM-5v-turbo 正式支持
- xAI 插件 x_search 迁移（breaking change）
- CVE-2026-34511（Medium 5.3）修复

### Docker Agent Sandbox 安全配置（官方推荐）
- `OPENCLAW_SANDBOX=1` 开启 AI 工具隔离
- 容器非 root 运行（node UID 1000）
- `gateway.bind: "loopback"` 本机访问
- 定期清理 /tmp/openclaw/ 和过期 JSONL

### Cron 定时任务新增功能
- `--tz "Asia/Shanghai"` 精确时区支持
- `--model` / `--thinking` 逐任务覆盖
- `--light-context` 节省 token
- `--tools` 参数限制工具权限
- `--agent <name>` 多智能体路由

### 本周必做
```bash
openclaw update && openclaw doctor --security
```

---

## 2026-04-08 配置周刊要点（本期头条：版本落后+安全目录权限问题）

### v2026.4.5（2026-04-06 最新版，npm 2026.4.5）
- **内置 video_generate / music_generate 工具**：无需插件，智能体直接调用
- **Memory/Dreaming 实验功能**：/dreaming 命令 + 三阶段（light/deep/REM）+ Dreams UI，--experimental-memory-v2 开启
- **Control UI 多语言**：新增简体中文/繁体中文/日语等12种语言
- **新增 Provider**：Qwen / Fireworks AI / StepFun / MiniMax TTS / Ollama Web Search / MiniMax Search
- **Breaking Changes**：旧别名移除（talk.voiceId / talk.apiKey / sandbox.perSession 等），需 doctor --fix 迁移
- **Amazon Bedrock Mantle**：新增支持

### ⚠️ 系统版本落后
- npm 最新：2026.4.5（2026-04-06）
- 系统安装：2026.3.3（落后 2 个大版本，2026-04-07 发现）
- 必做：openclaw update && openclaw doctor --fix && openclaw gateway restart

### 🔴 安全审计 Critical 项（2026-04-07 发现）
- **CRITICAL：/root/.openclaw mode=777（world-writable）**
  - 修复：chmod 700 /root/.openclaw && chmod 700 /root/.openclaw/agents && chmod 700 /root/.openclaw/sessions
  - 同机器其他进程可篡改 OpenClaw 状态文件

### Anthropic 封禁后续（2026-04-04 生效）
- Claude订阅不再覆盖第三方工具
- 补偿截止4月17日前：等额积分+全额退款+30%用量折扣
- 建议切换 MiniMax/DeepSeek/GLM

### 本周必做
```bash
openclaw update && openclaw doctor --fix && openclaw gateway restart
chmod 700 /root/.openclaw /root/.openclaw/agents /root/.openclaw/sessions
openclaw doctor --security
```

---
*更新于 2026-04-08*

## 2026-04-09 配置周刊要点（本期头条：npm 落后6个版本！）

### npm 最新版：v2026.4.9（今日 beta）/ v2026.4.8（稳定版）
- v2026.4.8, v2026.4.7-1, v2026.4.7, v2026.4.5, v2026.4.2, v2026.4.1, v2026.3.31 连续发布
- **系统当前 v2026.3.3，落后 6 个版本！** 立即 `npm install -g openclaw@latest`

### 60秒安全加固基线（官方文档新增）
- gateway.bind: "loopback" + token 认证
- tools.profile: "messaging" + deny automation/runtime/fs/sessions_spawn/sessions_send
- 文件权限 700（当前 ~/.openclaw 是 777，Critical！）
- dmPolicy: "pairing" + requireMention: true

### Cron 新参数（v2026.3.31+）
- `--stagger 30s`：指定错开窗口，避免整点负载尖峰
- `--light-context`：跳过工作区引导文件，节省 token
- `--tools exec,read`：按任务限制工具权限
- `--agent <name>`：多智能体路由
- Gmail PubSub Webhook 集成

### SubAgent 嵌套深度（官方文档）
- maxSpawnDepth 默认 1，最大 5，建议 2
- maxChildrenPerAgent 默认 5，maxConcurrent 默认 8
- archiveAfterMinutes 默认 60

### 安全 Critical 检查
- fs.state_dir.perms_world_writable（当前 ~/.openclaw mode=777）
- gateway.bind_no_auth
- gateway.tailscale_funnel
- 立即：openclaw security audit --deep --fix

### ClawHub TOP 5（2026-04）
- self-improving-agent: 495k★ | gog: 316k★ | Summarize: 153k★ | Tavily: 145k★ | Github: 98k★

---
*更新于 2026-04-09*

## 2026-04-10 配置周刊要点（本期头条：6天7版本密集发布！）

### 密集发布周：v2026.4.5～v2026.4.9（04-06～04-09）
- v2026.4.9（04-09）：Memory/Dreaming增强，多项安全修复
- v2026.4.8（04-08）：修复 npm 安装后 Telegram/Slack/Matrix 启动时 dist/extensions/*/src/* 文件无法加载的严重问题（强烈推荐升级！）
- v2026.4.7（04-08）：🆕 openclaw infer CLI + memory-wiki 完整回归 + Webhook 入口插件 + 可插拔压缩提供者
- v2026.4.7-1（04-08）：小补丁
- v2026.4.6（04-07）：修复 Dreaming 重复摄入、OAuth 401（Claude API 端点变更）、Windows 插件 ESM 加载
- v2026.4.5（04-06）：内置 video_generate/music_generate + ComfyUI 集成 + 13 种语言 UI

### Anthropic 封禁后续
- 补偿截止日期：2026年4月17日（剩余约7天）
- 补偿：等额积分 + 全额退款 + 30% 用量折扣

### 本周必做
```bash
npm install -g openclaw@latest && openclaw doctor --fix && openclaw gateway restart
chmod 700 /root/.openclaw /root/.openclaw/agents /root/.openclaw/sessions
openclaw doctor --security
```

---
*更新于 2026-04-10*



## 2026-04-12 配置周刊要点（本期头条：落后8个版本！v2026.4.11已发布）

### 系统 v2026.3.3 严重落后！
- npm 最新稳定：v2026.4.11（2026-04-12）
- npm 最新测试：v2026.4.12-beta
- 落后 8 个大版本！openclaw update 跳过（not-git-install）
- 必须：npm install -g openclaw@latest && openclaw doctor --fix && openclaw gateway restart

### v2026.4.9（04-09）重点
- 梦境/记忆系统增强：落地式REM回填、结构化日记视图
- 5项安全修复：浏览器校验重执行、环境变量隔离、节点命令净化
- 多平台适配：Android/Matrix/Slack/QQBot

### v2026.4.8（04-08）强烈推荐升级
- 修复 Telegram/Slack/Matrix 启动严重Bug（dist/extensions/*/src/* 无法加载）
- Host exec/env消毒、SSRF重定向保护

### v2026.4.7（04-08）
- openclaw infer CLI 一体化推理入口
- Memory Wiki 完整回归、Webhook入口插件、Session分支恢复

### 安全：目录权限 777 问题再次出现
- chmod 700 /root/.openclaw /root/.openclaw/agents /root/.openclaw/sessions
- 这是 04-08/04-09 以来第三次发现

### Anthropic 补偿截止：2026年4月17日（剩余5天）

---

## 2026-04-11 配置周刊要点（本期头条：v2026.4.8修复严重Bug，系统落后6个版本！）

### 系统 v2026.3.3 严重落后！
- npm 最新稳定：v2026.4.8（2026-04-08）
- npm 最新测试：v2026.4.9（2026-04-09）
- 落后 6 个大版本，立即：npm install -g openclaw@latest

### v2026.4.7 新功能（04-08）
- openclaw infer CLI：一体化推理入口（推理/图像/视频/音乐/搜索/Embedding）
- Memory Wiki 完整回归（claim/evidence/矛盾聚类/新鲜度加权）
- Webhook 入口插件（外部自动化接入）
- Session 分支恢复（持久化压缩检查点）
- 新增 Provider：Arcee AI / Google Gemma 4 / Amazon Bedrock Mantle / Ollama Vision
- 媒体生成 V2V（视频到视频）支持

### v2026.4.8 强烈推荐升级！（04-08）
- 修复：Telegram/Slack/Matrix 启动时 dist/extensions/*/src/* 文件无法加载（严重！）
- Host exec/env 消毒（阻止危险环境变量覆盖）
- SSRF 重定向保护（307/308 丢弃请求体）
- Gateway Token 变更后旧会话自动失效

### v2026.4.9（04-09）
- Memory/Dreaming 增强、结构化日记视图、字符氛围评估、iOS 版本控制改进

### CVE-2026-33579（CVSS 9.9，Critical！）
- /pair approve 权限提升，影响 < v2026.3.28
- 修复：升级到最新版即可

### Anthropic 封禁后续
- 补偿截止日期：2026年4月17日（剩余约6天）
- 建议切换 MiniMax / DeepSeek / GLM

### 升级避坑（来自社区实战）
- 双版本共存：which openclaw + hash -r && rehash
- 配置文件覆盖：升级前 cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak-$(date +%Y%m%d)
- 路由绑定失效：绑定配置直接写入 JSON 文件
- 插件重复注册：检查 plugins.allow 配置

### 本周必做
- npm install -g openclaw@latest && openclaw gateway restart
- chmod 700 /root/.openclaw /root/.openclaw/agents /root/.openclaw/sessions

---
*更新于 2026-04-11*
