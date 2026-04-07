# OpenClaw 跨设备控制方案

**文档版本**: 1.0  
**创建时间**: 2026-03-05  
**目标**: 实现手机/公司电脑/出差设备远程触发家里/服务器上运行的OpenClaw任务

---

## 1. 方案概述

本文档详细介绍如何实现跨设备远程控制OpenClaw的多种技术方案，帮助用户在任意网络环境下安全、便捷地触发本地OpenClaw任务。

### 1.1 核心需求

- 在手机浏览器上查看OpenClaw状态
- 远程触发特定任务
- 查看任务执行结果
- 安全可靠的认证机制

---

## 2. 方案对比

### 2.1 工具选型对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Tailscale + VS Code Remote** | 安全、内网体验、无公网暴露 | 需要安装客户端 | 开发调试、深度操作 |
| **自定义Web控制台** | 跨浏览器、易定制 | 需要公网暴露、有安全风险 | 快速查看、简单触发 |
| **Telegram Bot指令** | 手机友好、无需安装APP、功能丰富 | 需要翻墙、功能相对受限 | 简单触发、状态通知 |
| **Cloudflare Tunnel** | 免费、安全、无需公网IP | 国内访问可能慢 | 临时暴露服务 |
| **Ngrok/FRP** | 简单快速 | 付费/有限制 | 临时使用 |

### 2.2 推荐方案优先级

1. **首选**: Tailscale - 安全性最高，体验最接近本地
2. **备选**: Telegram Bot - 手机端最方便
3. **临时方案**: Cloudflare Tunnel - 快速暴露服务

---

## 3. 方案详解

### 3.1 Tailscale + VS Code Remote 方案

#### 3.1.1 方案原理

Tailscale基于WireGuard协议创建虚拟局域网，将分布在不同物理位置的多台设备组成一个安全的虚拟内网。通过这个虚拟内网，可以直接SSH到远程服务器或使用VS Code Remote进行开发。

#### 3.1.2 部署步骤

**步骤1: 注册Tailscale账号**

1. 访问 https://tailscale.com 注册账号
2. 创建个人网络

**步骤2: 在服务器安装Tailscale**

```bash
# Ubuntu/Debian
curl -fsSL https://tailscale.com/install.sh | sh

# 启动并设置开机自启
sudo tailscale up --operator=root --advertise-exit-node

# 查看分配的虚拟IP
tailscale ip -4
```

**步骤3: 在客户端设备安装Tailscale**

- Windows/Mac: 从官网下载安装包
- iOS/Android: 从App Store/Play Store下载
- Linux: 使用上述安装脚本

**步骤4: 授权设备**

1. 登录Tailscale管理后台 https://login.tailscale.com/admin
2. 找到待授权的设备，点击授权
3. 记录分配的虚拟IP地址

**步骤5: 配置SSH访问**

```bash
# 在客户端配置SSH config (~/.ssh/config)
Host remote-server
    HostName <tailscale虚拟IP>
    User <username>
    IdentityFile ~/.ssh/id_rsa
    ForwardAgent yes
```

**步骤6: VS Code Remote连接**

1. 安装VS Code Remote插件
2. 按 `Ctrl+Shift+P` 打开命令面板
3. 输入 `Remote-SSH: Connect to Host`
4. 输入远程服务器IP或选择已保存的配置

#### 3.1.3 触发OpenClaw任务

通过SSH执行命令：

```bash
ssh <tailscale虚拟IP> "cd /path/to/openclaw && python main.py --task your-task"
```

#### 3.1.4 优缺点分析

**优点**:
- 端到端加密，安全性高
- 虚拟内网体验，延迟低
- 不需要公网IP
- 支持端口转发

**缺点**:
- 需要在所有设备安装客户端
- 首次配置稍复杂
- 部分地区可能无法访问Tailscale服务器

---

### 3.2 Telegram Bot 方案

#### 3.2.1 方案原理

通过Telegram Bot接收用户消息指令，将指令转发给OpenClaw执行，并把执行结果通过Bot返回给用户。

#### 3.2.2 部署步骤

**步骤1: 创建Telegram Bot**

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 记录Bot Token

**步骤2: 获取用户ID**

1. 搜索 `@userinfobot`
2. 发送任意消息获取Chat ID

**步骤3: 安装Python依赖**

```bash
pip install python-telegram-bot requests
```

**步骤4: 创建Bot服务脚本**

```python
#!/usr/bin/env python3
"""
OpenClaw Telegram Bot
功能: 接收指令并转发给OpenClaw执行
"""

import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 配置
BOT_TOKEN = "YOUR_BOT_TOKEN"
ALLOWED_USER_IDS = [YOUR_CHAT_ID]  # 允许的用户ID列表
OPENCLAW_PATH = "/path/to/openclaw"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text(
        "🤖 OpenClaw Bot 已启动！\n\n"
        "可用命令:\n"
        "/start - 显示此帮助\n"
        "/status - 查看OpenClaw状态\n"
        "/list - 列出可用任务\n"
        "直接发送命令执行任务"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看OpenClaw状态"""
    if not check_user(update.effective_user.id):
        return
    
    try:
        # 检查OpenClaw进程状态
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        if "openclaw" in result.stdout.lower():
            await update.message.reply_text("✅ OpenClaw 正在运行")
        else:
            await update.message.reply_text("❌ OpenClaw 未运行")
    except Exception as e:
        await update.message.reply_text(f"❌ 检查失败: {str(e)}")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出可用任务"""
    if not check_user(update.effective_user.id):
        return
    
    tasks = """
📋 可用任务列表:

1. daily-report - 生成日报
2. sync-files - 同步文件
3. backup - 备份数据
4. check-status - 检查状态

使用方式: /run daily-report
"""
    await update.message.reply_text(tasks)

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """执行指定任务"""
    if not check_user(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ 请指定任务名称\n用法: /run <task-name>")
        return
    
    task_name = context.args[0]
    await update.message.reply_text(f"⏳ 正在执行任务: {task_name}...")
    
    try:
        # 执行OpenClaw任务
        result = subprocess.run(
            ["python", "main.py", "--task", task_name],
            cwd=OPENCLAW_PATH,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            output = result.stdout[:4000]  # 限制输出长度
            await update.message.reply_text(f"✅ 任务完成！\n\n{output}")
        else:
            error = result.stderr[:4000]
            await update.message.reply_text(f"❌ 任务失败！\n\n{error}")
            
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏰ 任务执行超时")
    except Exception as e:
        await update.message.reply_text(f"❌ 执行错误: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息"""
    if not check_user(update.effective_user.id):
        await update.message.reply_text("⛔ 未授权用户")
        return
    
    await update.message.reply_text(
        "📝 消息已收到\n"
        "请使用 /run <task-name> 执行任务"
    )

def check_user(user_id: int) -> bool:
    """检查用户是否授权"""
    return user_id in ALLOWED_USER_IDS

def main():
    """启动Bot"""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 注册命令处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("run", run_command))
    
    # 注册消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()
```

**步骤5: 配置系统服务**

```bash
# 创建服务文件 /etc/systemd/system/openclaw-bot.service
[Unit]
Description=OpenClaw Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/openclaw-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable openclaw-bot
sudo systemctl start openclaw-bot
```

#### 3.2.3 使用方式

```
/start          - 启动Bot
/status         - 查看状态
/list           - 列出任务
/run daily-report - 执行任务
```

#### 3.2.4 优缺点分析

**优点**:
- 手机端使用方便
- 无需安装额外软件
- 支持消息推送
- 免费、稳定

**缺点**:
- 国内需要翻墙
- 功能相对简单
- 需要Bot服务器24小时运行

---

### 3.3 Web控制台方案

#### 3.3.1 方案原理

搭建一个轻量级的Web界面，通过浏览器访问来查看OpenClaw状态和触发任务。

#### 3.3.2 部署步骤

**步骤1: 创建Flask应用**

```python
#!/usr/bin/env python3
"""
OpenClaw Web Console
"""

from flask import Flask, render_template_string, request, jsonify
import subprocess
import os
import hashlib

app = Flask(__name__)

# 安全配置
ADMIN_PASSWORD = hashlib.sha256("your-secure-password".encode()).hexdigest()
API_KEY = "your-api-key"

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 控制台</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .status { display: flex; align-items: center; gap: 8px; }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; }
        .running { background: #4CAF50; }
        .stopped { background: #f44336; }
        button { background: #2196F3; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
        button:hover { background: #1976D2; }
        .log { background: #1e1e1e; color: #ddd; padding: 12px; border-radius: 6px; font-family: monospace; max-height: 300px; overflow-y: auto; white-space: pre-wrap; }
        input { padding: 10px; border: 1px solid #ddd; border-radius: 6px; width: 200px; }
        .task-list { list-style: none; padding: 0; }
        .task-item { padding: 12px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <h1>🤖 OpenClaw 控制台</h1>
    
    <div class="card">
        <h3>📊 运行状态</h3>
        <div class="status">
            <div class="status-dot {{'running' if running else 'stopped'}}"></div>
            <span>{{'运行中' if running else '已停止'}}</span>
        </div>
    </div>
    
    <div class="card">
        <h3>▶️ 执行任务</h3>
        <form action="/run" method="post">
            <input type="text" name="task" placeholder="任务名称" required>
            <input type="password" name="password" placeholder="密码" required>
            <button type="submit">执行</button>
        </form>
        {% if result %}
        <div class="log">{{ result }}</div>
        {% endif %}
    </div>
    
    <div class="card">
        <h3>📋 任务日志</h3>
        <button onclick="refreshLog()">刷新</button>
        <div class="log" id="log">{{ log }}</div>
    </div>
    
    <script>
    function refreshLog() {
        fetch('/log')
            .then(r => r.text())
            .then(text => document.getElementById('log').textContent = text);
    }
    setInterval(refreshLog, 5000);
    </script>
</body>
</html>
'''

def check_password(password: str) -> bool:
    """验证密码"""
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD

@app.route('/')
def index():
    """主页"""
    running = os.system('pgrep -f openclaw > /dev/null') == 0
    return render_template_string(HTML_TEMPLATE, running=running)

@app.route('/run', methods=['POST'])
def run_task():
    """执行任务"""
    password = request.form.get('password', '')
    task = request.form.get('task', '')
    
    if not check_password(password):
        return "❌ 密码错误", 403
    
    try:
        result = subprocess.run(
            ['python', 'main.py', '--task', task],
            capture_output=True,
            text=True,
            timeout=300,
            cwd='/path/to/openclaw'
        )
        output = result.stdout + result.stderr
        return render_template_string(HTML_TEMPLATE, running=True, result=output[:2000])
    except Exception as e:
        return f"❌ 执行失败: {str(e)}"

@app.route('/log')
def get_log():
    """获取日志"""
    try:
        with open('/path/to/openclaw/logs/app.log', 'r') as f:
            return f.read()[-5000:]
    except:
        return "暂无日志"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

**步骤2: 使用Cloudflare Tunnel暴露**

```bash
# 安装cloudflared
curl -Ls https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 登录
cloudflared tunnel login

# 创建隧道
cloudflared tunnel create openclaw

# 配置隧道
cloudflared tunnel route ip add --udprule 0.0.0.0/0 openclaw

# 运行
cloudflared tunnel --url http://localhost:8080
```

#### 3.3.3 优缺点分析

**优点**:
- 跨平台、跨浏览器
- 界面友好
- 可定制性强

**缺点**:
- 需要公网暴露
- 需要配置HTTPS
- 有安全风险

---

## 4. 安全机制

### 4.1 身份验证方式

| 方案 | 认证方式 |
|------|----------|
| Tailscale | 设备授权 + SSH密钥 |
| Telegram Bot | 用户ID白名单 |
| Web控制台 | 密码/API Key |

### 4.2 安全建议

1. **强密码策略**: 使用复杂密码，定期更换
2. **IP白名单**: 限制可访问的IP范围
3. **API Key认证**: 为API调用生成独立密钥
4. **操作日志**: 记录所有操作以便审计
5. **二次确认**: 敏感操作需要额外确认
6. **HTTPS强制**: 所有Web访问使用HTTPS
7. **限流防护**: 防止暴力破解

### 4.3 权限控制

```python
# 示例: 基于角色的权限控制
ROLES = {
    'admin': ['run', 'stop', 'config', 'logs'],
    'operator': ['run', 'logs'],
    'viewer': ['status', 'logs']
}
```

---

## 5. 故障排查

### 5.1 Tailscale常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 设备不在线 | 网络问题 | 检查防火墙、端口 |
| 无法SSH | SSH服务未启动 | `sudo systemctl enable ssh` |
| 延迟高 | DERP服务器远 | 自建DERP或使用Exit Node |

### 5.2 Telegram Bot常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Bot无响应 | Token错误 | 检查BOT_TOKEN配置 |
| 用户未授权 | ID不在白名单 | 添加用户ID到ALLOWED_USER_IDS |
| 消息发送失败 | 隐私设置 | 用户需启动Bot |

### 5.3 Web控制台常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 无法访问 | 防火墙未开放 | 开放80/443端口 |
| HTTPS错误 | 证书问题 | 使用Let's Encrypt |
| 502错误 | 服务未启动 | 检查Flask应用状态 |

---

## 6. 推荐方案总结

### 6.1 场景推荐

| 场景 | 推荐方案 |
|------|----------|
| 日常开发调试 | Tailscale + SSH |
| 简单任务触发 | Telegram Bot |
| 快速临时访问 | Cloudflare Tunnel |
| 生产环境 | Tailscale + 自建Web |

### 6.2 部署难度

| 方案 | 难度 | 耗时 |
|------|------|------|
| Tailscale | ⭐⭐ | 30分钟 |
| Telegram Bot | ⭐⭐⭐ | 1小时 |
| Web控制台 | ⭐⭐⭐⭐ | 2小时 |
| Cloudflare Tunnel | ⭐ | 10分钟 |

---

## 7. 附录

### 7.1 相关资源

- Tailscale官网: https://tailscale.com
- Telegram Bot API: https://core.telegram.org/bots/api
- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps

### 7.2 配置文件示例

```
# OpenClaw 跨设备配置
# 保存位置: ~/.openclaw/config.yaml

remote:
  method: tailscale
  ip: 100.x.x.x
  ssh_port: 22
  username: ubuntu

telegram:
  enabled: true
  bot_token: xxx
  allowed_users:
    - 123456789

web:
  enabled: false
  port: 8080
  password_hash: xxx
```

---

*文档生成时间: 2026-03-05*
*版本: 1.0*
