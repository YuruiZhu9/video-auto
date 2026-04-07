# Telegram Bot 配置指南（v1.1.0）

## 快速配置

### 1. 创建 Bot

1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot`，按提示填写 Bot 名称
3. 获得 `Bot Token`：格式为 `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. 获取 Chat ID

**方式 A：直接对话**
1. 搜索你的 Bot，点击「开始」
2. 访问：`https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. 找到 `"chat":{"id":123456789,...}` — 这就是你的 Chat ID

**方式 B：通过 Bot 获取**
```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates" | jq
```

### 3. 配置环境变量

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjkl..."
export TELEGRAM_CHAT_ID="123456789"
```

**生产 Webhook 模式（推荐公网部署）**：
```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
export TELEGRAM_WEBHOOK_URL="https://your-domain.com/api/v1/telegram/webhook"
export TELEGRAM_WEBHOOK_SECRET="your-secret-token"
```

### 4. 重启服务

```bash
# 如果用 systemd
sudo systemctl restart clawremote

# 或手动
python fastapi_server/main.py --port 8081
```

## Bot 命令一览

| 命令 | 说明 |
|------|------|
| `/status` | 查看 OpenClaw 系统状态 |
| `/list [数量]` | 列出最近任务（默认5条） |
| `/templates` | 列出可用任务模板 |
| `/exec <模板>` | 触发任务（如 `/exec tech_brief`） |
| `/cancel <ID>` | 取消任务（如 `/cancel t_abc123`） |
| `/help` | 显示帮助 |

**直接发消息** → 透传给 OpenClaw 作为子任务执行

## 架构说明

```
Telegram 服务器
      ↓ (Webhook POST / Polling)
TelegramBot 实例
      ↓
OpenClawClient ← → OpenClaw Gateway
      ↓
NotifyManager → 钉钉/飞书/企业微信
```

**两种运行模式**：
- **Polling**（默认）：服务定时向 Telegram API 拉取更新，无需公网 IP
- **Webhook**（生产推荐）：Telegram 服务器主动推送，需要 HTTPS 域名

## 与钉钉的对比

| | 钉钉 | Telegram |
|---|---|---|
| 消息格式 | Markdown | Markdown/HTML |
| 命令支持 | ❌ | ✅ 原生命令菜单 |
| 交互按钮 | ✅ | ✅ Inline Keyboard |
| 公网要求 | ❌ | ⚠️ Webhook 模式需要 |
| 隐私 | 国内数据 | 全球 |
| 延迟 | ~1s | ~0.5s |
