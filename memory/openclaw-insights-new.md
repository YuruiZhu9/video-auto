
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
