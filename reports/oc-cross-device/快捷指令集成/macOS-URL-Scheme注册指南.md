# macOS / Windows URL Scheme 注册指南

> 让浏览器和桌面应用也能触发 `clawctl://`，实现"一键直达"式远程控制。

---

## 1. macOS Safari + Chrome 注册 clawctl:// 协议

### 1.1 原理

macOS 上通过创建 `clawctl-register.html` 页面 + AppleScript/JavaScript 自动注册 URI Scheme。
注册一次后，所有浏览器和应用都识别 `clawctl://`。

### 1.2 注册脚本

```html
<!-- clawctl-register.html — 保存到本地，双击打开即可注册 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>clawctl:// 协议注册</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 600px; margin: 60px auto; padding: 20px; }
  h1 { color: #333; }
  .ok { color: green; font-size: 1.2em; }
  .fail { color: red; }
  button { padding: 10px 20px; font-size: 16px; cursor: pointer; margin: 5px; }
  pre { background: #f5f5f5; padding: 15px; border-radius: 8px; overflow-x: auto; }
</style>
</head>
<body>
<h1>🔗 clawctl:// 协议注册</h1>
<p>注册后即可在浏览器地址栏输入 <code>clawctl://...</code> 直接触发 OpenClaw 任务。</p>

<button onclick="register()">✅ 注册 clawctl:// 协议</button>
<button onclick="testScheme()">🧪 测试连接</button>

<div id="result" style="margin-top:20px"></div>

<script>
function register() {
  // 尝试通过 iframe 触发注册（现代浏览器安全限制，大多会失败但可触发提示）
  const iframe = document.createElement("iframe");
  iframe.style.display = "none";
  iframe.src = "clawctl://register?app=OpenClaw+Control&description=OpenClaw+Remote+Control";
  document.body.appendChild(iframe);
  setTimeout(() => {
    document.getElementById("result").innerHTML =
      '<p class="ok">✅ 协议注册请求已发送！</p>' +
      '<p>如果浏览器弹出"是否允许打开 clawctl"提示，请选择<strong>允许</strong>。</p>' +
      '<p>如果没有提示，说明浏览器已识别该协议。</p>';
  }, 500);
  setTimeout(() => document.body.removeChild(iframe), 2000);
}

function testScheme() {
  const iframe = document.createElement("iframe");
  iframe.style.display = "none";
  iframe.src = "clawctl://status";
  document.body.appendChild(iframe);
  setTimeout(() => {
    document.getElementById("result").innerHTML =
      '<p class="ok">✅ clawctl:// 协议已注册成功！</p>';
    document.body.removeChild(iframe);
  }, 1000);
}
</script>
</body>
</html>
```

### 1.3 永久注册（推荐 — AppleScript）

```applescript
-- clawctl-register.scpt
-- 使用方法: osascript clawctl-register.scpt
-- 需要在"系统偏好设置 → 安全性与隐私 → 隐私 → 自动化"中授权

set schemeURL to "clawctl://status"

-- 尝试打开 URL（macOS 会记住已注册的处理程序）
try
    open location schemeURL
    display notification "clawctl:// 协议注册成功！" with title "OpenClaw Control"
on error errMsg
    display alert "注册失败" message errMsg
end try
```

### 1.4 通过 macOS Automator 创建 App

1. 打开 **Automator** → 新建文稿 → **应用程序**
2. 添加 **"运行 AppleScript"** 操作：
   ```applescript
   on run {input, parameters}
       open location "clawctl://register?app=OpenClaw+Control"
       return input
   end run
   ```
3. 保存为 `clawctl-Register.app`
4. 双击运行即可注册协议

---

## 2. macOS 浏览器书签栏方案（最简）

不想注册协议？用书签栏一键触发：

```javascript
// 在 Chrome/Safari 地址栏创建书签
// 名称：🤖 AI早报
// URL：
javascript:(function(){
  const apiKey='YOUR_EXECUTE_KEY';
  const tmpl='quick_fetch';
  const name='AI早报';
  const base='https://YOUR_SERVER.COM';  // 改成你的服务器地址
  fetch(base+'/api/v1/templates/'+tmpl+'/execute',{
    method:'POST',
    headers:{'Content-Type':'application/json','Authorization':'Bearer '+apiKey},
    body: JSON.stringify({notify_channel:'dingtalk'})
  }).then(r=>r.json()).then(d=>{
    navigator.clipboard.writeText(JSON.stringify(d));
    alert('✅ 任务已触发: '+d.name+'\\nID: '+d.id);
  }).catch(e=>alert('❌ 失败: '+e));
})();
```

> 在 Chrome 书签栏点击书签 → 自动发送请求 → 弹出通知确认。

---

## 3. Windows 注册 clawctl:// 协议

### 3.1 通过注册表（需要管理员权限）

创建 `clawctl-register.reg` 文件：

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\clawctl]
@="URL:OpenClaw Control Protocol"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\clawctl\DefaultIcon]
@="\"C:\\\\Program Files\\\\clawctl\\\\icon.ico\""

[HKEY_CLASSES_ROOT\clawctl\shell]

[HKEY_CLASSES_ROOT\clawctl\shell\open]

[HKEY_CLASSES_ROOT\clawctl\shell\open\command]
@="\"C:\\\\Program Files\\\\clawctl\\\\clawctl.exe\" \"%1\""
```

双击运行 `.reg` 文件（需要管理员权限）。

### 3.2 Windows 小工具（PowerShell）

```powershell
# clawctl-launcher.ps1
# 创建一个 Windows 快捷方式指向这个脚本

param(
    [Parameter(Mandatory=$true)]
    [string]$Action,      # run | message | status

    [string]$Template = "",
    [string]$Text = "",
    [string]$Channel = "dingtalk",
    [string]$ApiKey = "",
    [string]$Server = "https://your-server.com"
)

$headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Content-Type" = "application/json"
}

switch ($Action) {
    "run" {
        $body = @{ name = "Windows-$Template"; notify_channel = $Channel } | ConvertTo-Json
        $resp = Invoke-RestMethod -Uri "$Server/api/v1/templates/$Template/execute" `
            -Method Post -Headers $headers -Body $body
        Write-Host "✅ 任务已触发: $($resp.name) | ID: $($resp.id)"
    }
    "message" {
        $body = @{ channel = $Channel; message = $Text } | ConvertTo-Json
        $resp = Invoke-RestMethod -Uri "$Server/api/v1/send" `
            -Method Post -Headers $headers -Body $body
        Write-Host "✅ 消息已发送"
    }
    "status" {
        $resp = Invoke-RestMethod -Uri "$Server/api/v1/status" -Headers $headers
        Write-Host "系统状态: $($resp | ConvertTo-Json -Compress)"
    }
}
```

创建快捷方式：
```
powershell -ExecutionPolicy Bypass -File "C:\Program Files\clawctl\clawctl-launcher.ps1" -Action run -Template quick_fetch -ApiKey "YOUR_KEY"
```

---

## 4. 跨平台统一入口页面

在服务器上部署一个静态页面，作为所有设备的统一入口：

```html
<!-- /var/www/clawctl/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🤖 OpenClaw 控制台</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
  .container { max-width: 480px; margin: 0 auto; }
  h1 { text-align: center; margin-bottom: 30px; }
  .card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
  .card h3 { margin: 0 0 10px; color: #38bdf8; }
  .btn { display: block; width: 100%; padding: 14px; margin: 8px 0; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; text-decoration: none; text-align: center; transition: background 0.2s; }
  .btn:hover { background: #2563eb; }
  .btn-success { background: #22c55e; }
  .btn-success:hover { background: #16a34a; }
  .status { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155; }
  .status:last-child { border-bottom: none; }
  .badge { padding: 2px 8px; border-radius: 4px; font-size: 12px; }
  .badge-ok { background: #22c55e; }
  .badge-err { background: #ef4444; }
  .qr { text-align: center; margin-top: 20px; }
  .qr img { border-radius: 8px; }
  a { color: #38bdf8; }
</style>
</head>
<body>
<div class="container">
  <h1>🤖 OpenClaw 控制台</h1>

  <div class="card">
    <h3>📊 系统状态</h3>
    <div class="status">
      <span>clawctl 服务</span><span class="badge badge-ok">运行中</span>
    </div>
    <div class="status">
      <span>OpenClaw Gateway</span><span class="badge badge-ok">已连接</span>
    </div>
    <div class="status">
      <span>定时任务</span><span class="badge badge-ok">4 个活跃</span>
    </div>
  </div>

  <div class="card">
    <h3>🚀 快捷操作</h3>
    <a class="btn btn-success" href="clawctl://run?template=quick_fetch&api_key=YOUR_KEY&name=快捷指令-AI早报">📰 AI 早报</a>
    <a class="btn" href="clawctl://run?template=tech_brief&api_key=YOUR_KEY&name=快捷指令-技术早读">🔬 技术早读</a>
    <a class="btn" href="clawctl://run?template=biz_brief&api_key=YOUR_KEY&name=快捷指令-商业速报">💼 商业速报</a>
    <a class="btn" href="clawctl://status?api_key=YOUR_KEY">🔍 系统状态</a>
    <a class="btn" href="clawctl://message?text=测试消息&channel=dingtalk&api_key=YOUR_KEY">💬 发送测试消息</a>
  </div>

  <div class="card">
    <h3>⏰ 定时任务</h3>
    <a class="btn" href="clawctl://schedule?action=trigger&job=daily_brief&api_key=YOUR_KEY">▶️ 立即触发晨报</a>
    <a class="btn" href="clawctl://schedule?action=list&api_key=YOUR_KEY">📋 查看所有定时任务</a>
  </div>

  <div class="card">
    <h3>📱 快捷指令</h3>
    <p style="color:#94a3b8; font-size:14px;">
      在 iOS 快捷指令 App 中添加以下 URL：<br><br>
      <code style="font-size:12px; word-break:break-all;">clawctl://run?template=quick_fetch&api_key=YOUR_KEY</code>
    </p>
  </div>

  <p style="text-align:center; color:#64748b; font-size:12px;">
    OpenClaw Cross-Device Control · v1.3.0<br>
    <a href="/api/v1/docs">API 文档</a> · <a href="/api/v1/shortcuts">快捷指令列表</a>
  </p>
</div>
</body>
</html>
```

---

## 5. 命令行快速触发工具

```bash
# ~/bin/clawctl (添加到 PATH)
#!/usr/bin/env bash
# 用法: clawctl run <template> [name]
#        clawctl msg <text> [channel]
#        clawctl status

API_KEY="${OPENCLAW_API_KEY:-sk-oc-execute-default}"
SERVER="${OPENCLAW_SERVER:-https://your-server.com}"
AUTH="Authorization: Bearer $API_KEY"

cmd="$1"
shift

case "$cmd" in
  run)
    tmpl="${1:-quick_fetch}"; name="${2:-cli-$tmpl}"
    curl -s -X POST "$SERVER/api/v1/templates/$tmpl/execute" \
      -H "$AUTH" -H "Content-Type: application/json" \
      -d "{\"name\":\"$name\",\"notify_channel\":\"dingtalk\"}" | jq .
    ;;
  msg)
    text="$1"; channel="${2:-dingtalk}"
    curl -s -X POST "$SERVER/api/v1/send" \
      -H "$AUTH" -H "Content-Type: application/json" \
      -d "{\"channel\":\"$channel\",\"message\":\"$text\"}" | jq .
    ;;
  status)
    curl -s "$SERVER/api/v1/status" -H "$AUTH" | jq .
    ;;
  list)
    curl -s "$SERVER/api/v1/tasks?limit=10" -H "$AUTH" | jq .
    ;;
  *)
    echo "用法: clawctl run <template> [name]  |  msg <text> [channel]  |  status  |  list"
    ;;
esac
```

> 将 `~/bin/clawctl` chmod +x 后，从任何终端秒触发任务。

---

## 6. Chrome 扩展快捷触发

```json
// manifest.json
{
  "manifest_version": 3,
  "name": "OpenClaw Quick Trigger",
  "version": "1.0",
  "permissions": ["activeTab"],
  "action": {
    "default_title": "🤖 OpenClaw",
    "default_icon": "icon.png"
  },
  "background": {
    "service_worker": "background.js"
  }
}
```

```javascript
// background.js
chrome.action.onClicked.addListener((tab) => {
  chrome.tabs.sendMessage(tab.id, { action: "showPanel" });
});
```

> 用户点击扩展图标 → 弹出面板显示常用任务 → 一键触发。
