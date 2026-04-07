# ClawRemote 部署指南

## 环境要求

- Python 3.10+
- 已有 OpenClaw Gateway 运行中
- 网络可达钉钉/Telegram（如需要推送）

## 安装

```bash
cd /workspace/reports/oc-cross-device/代码实现
pip install -e .
```

## 快速启动

### 1. 配置环境变量

```bash
export OPENCLAW_API_KEY="your-openclaw-gateway-api-key"
export OPENCLAW_GATEWAY_URL="http://localhost:18789"
export DINGTALK_WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=xxx"
export DINGTALK_SECRET="SEC..."  # 可选，开启加签
```

### 2. 生成 API Key

```bash
clawremote key create "手机执行Key" --level EXECUTE
# 输出示例：
# sk-a3f2b1c4d5e6f7g8h9i0j-EXECUTE
# ⚠️ 只显示一次，请复制保存！
```

### 3. 启动服务

```bash
clawremote server
# 服务启动：http://0.0.0.0:8080
# API 文档：http://0.0.0.0:8080/docs
```

### 4. 配置钉钉机器人

1. 打开钉钉群 → 设置 → 智能群助手 → 添加机器人
2. 选择「自定义」机器人
3. 填写名称，安全设置勾选「加签」，复制 Secret
4. 复制 WebHook URL

## 使用示例

### 命令行触发任务

```bash
# 查看 OpenClaw 状态
clawremote status

# 发送消息
clawremote send "测试消息"

# 触发任务
clawremote exec "生成今日技术简报" --agent tech-analyst
```

### HTTP API 触发

```bash
# 触发每日简报任务
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Authorization: Bearer sk-xxxxx-EXECUTE" \
  -H "Content-Type: application/json" \
  -d '{"template": "daily_brief", "params": {"scope": "tech"}}'

# 查询任务状态
curl http://localhost:8080/api/v1/tasks/t_abc123 \
  -H "Authorization: Bearer sk-xxxxx-READ_ONLY"
```

### 快捷指令（iOS）配置

1. 打开快捷指令 → 创建个人自动化
2. 选择「App」→ 选择任意 App
3. 添加操作：「获取 URL」
   - URL：`https://your-domain.com/api/v1/tasks/trigger`
   - 方法：POST
   - 头：`Authorization` / `Bearer sk-xxxxx-EXECUTE`
   - 请求体：`{"template": "daily_brief"}`
4. 添加操作：「显示通知」

### IFTTT Webhook 配置

1. IFTTT → Create Applet
2. Trigger: Webhook（Receive web request）
3. Action: Notification
4. Event Name: `daily_brief`
5. 调用：`https://your-domain.com/api/v1/webhook?secret=YOUR_WEBHOOK_SECRET`
   - Body: `{"template": "daily_brief", "params": {"scope": "tech"}}`

## Docker 部署

```bash
docker run -d \\
  --name clawremote \\
  -p 8080:8080 \\
  -e OPENCLAW_API_KEY=xxx \\
  -e OPENCLAW_GATEWAY_URL=http://host.docker.internal:18789 \\
  -e DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx \\
  -e DINGTALK_SECRET=SECxxx \\
  clawremote
```

## 配置参考

见 `config.py` 中的 `DEFAULT_CONFIG`，或创建 `config.yaml`：

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  debug: false

openclaw:
  gateway_url: "http://localhost:18789"

auth:
  rate_limit:
    READ_ONLY: 30
    EXECUTE: 20
    ADMIN: 60

notify:
  dingtalk:
    enabled: true
    webhook_url: "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    secret: "SEC..."

triggers:
  cron:
    enabled: true
    schedules:
      - template: "daily_brief"
        cron: "0 8 * * *"   # 每天早上 8 点
      - template: "quick_scan"
        cron: "0 */4 * * *"  # 每 4 小时

templates:
  daily_brief:
    display_name: "每日简报"
    action: "spawn"
    agent: "tech-analyst"
    params:
      scope: "all"
```

## Systemd 守护（生产推荐）

```ini
# /etc/systemd/system/clawremote.service
[Unit]
Description=ClawRemote - OpenClaw Cross-Device Control
After=network.target

[Service]
Environment=OPENCLAW_API_KEY=xxx
Environment=DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
ExecStart=/usr/local/bin/clawremote server
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable clawremote
sudo systemctl start clawremote
```
