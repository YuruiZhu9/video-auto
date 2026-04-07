# Android Tasker + OpenClaw Control 集成指南

> 用 Tasker 创建自动化任务，联动 OpenClaw 实现手机与 AI 助手无缝协作

## 方案概览

```
Android Tasker
    │
    ├── 触发条件
    │    ├── 时间（定时执行）
    │    ├── 位置（到家/公司）
    │    ├── 应用（打开某 App）
    │    ├── 手势（摇晃/双击）
    │    └── NFC 标签
    │
    ├── HTTP 请求 → OpenClaw Control API
    │    ├── 触发 Agent 任务
    │    ├── 发送消息
    │    └── 查询状态
    │
    └── 执行结果
         ├── 手机通知
         ├── 语音播报
         └── HTTP Response 内容显示
```

---

## 基础配置

### 1. Tasker 网络设置

确保 Tasker 有网络权限：
- 设置 → 应用 → Tasker → 权限 → **允许访问网络**

### 2. 安装 HTTP Request 插件（推荐）

Tasker 原生 HTTP Request 功能较基础，推荐安装：
- **HTTP Request Tasker Plugin**（作者：JayXon）
- 或使用 Tasker 内置的 **HTTP Get/Post** + **JavaScriptlet**

---

## Tasker 配置示例

### 示例 1：定时生成早报（每天 8:00）

**创建 Task：「OpenClaw 晨报」**

```
Task Edit → Task Name: OpenClaw 晨报
    │
    ├─ 1. HTTP Request（插件）
    │      URL: https://your-server/api/v1/tasks
    │      Method: POST
    │      Headers:
    │          Authorization: Bearer YOUR_API_KEY
    │          Content-Type: application/json
    │      Body: 
    │          {
    │            "name": "Tasker-早间简报",
    │            "template_id": "tech_brief",
    │            "action": "spawn",
    │            "params": {"scope": "morning"}
    │          }
    │      Timeout: 30
    │      Output Vars: %HTTPRESPONSE, %HTTPCODE
    │
    ├─ 2. Flash（显示结果）
    │      Text: OpenClaw 晨报已触发 ✓
    │
    └─ 3. Say（语音播报，可选）
           Text: 早报已生成，稍后推送至钉钉
           Engine: com.google.android.tts
```

**创建 Profile：**
```
Profile → Time → 08:00 Every Day
    → Link: Task "OpenClaw 晨报"
```

---

### 示例 2：到家自动状态巡检（位置触发）

**创建 Task：「OpenClaw 状态巡检」**
```
1. HTTP Request
      URL: https://your-server/api/v1/status
      Method: GET
      Headers: Authorization: Bearer YOUR_READONLY_KEY
      Output Vars: %HTTPRESPONSE

2. JavaScriptlet（解析 JSON 响应）
      const resp = JSON.parse(%HTTPRESPONSE);
      const gw = resp.gateway_connected ? '🟢 已连接' : '🔴 离线';
      const sessions = resp.active_sessions || 0;
      const jobs = resp.stats ? resp.stats.active_jobs || 0 : 0;
      setLocal('STATUS', gw + '\n活跃会话: ' + sessions + '\n定时任务: ' + jobs);

3. Flash
      Text: %STATUS

4. Say
      Text: OpenClaw 系统正常，会话数 %sessions
```

**创建 Profile：**
```
Profile → Location → 添加家庭位置（地图点击）
    → Enter: Task "OpenClaw 状态巡检"
    → Exit:（可选）离开时发送离线通知
```

---

### 示例 3：摇晃手机触发快捷任务

**创建 Profile：**
```
Profile → Event → Sensor → Accelerometer
    → Configuration:
          Movement: Shake
          Duration: 0.5s
          Sensitivity: High
    → Link: Task "OpenClaw 快捷任务"
```

**创建 Task：「OpenClaw 快捷任务」**
```
1. Scene: 显示任务选择菜单
      （可用 Tasker Scene 创建一个半透明浮层）
      - 技术简报
      - 商业洞察
      - 状态检查
      - 发送钉钉消息

2. 根据选择，调用对应 HTTP Request
```

---

### 示例 4：NFC 标签触发

**创建 NFC Tag：**
1. 安装 **NFC Tools** App
2. 写入任务 → 添加记录 → Tasker 命令 → 选择 Task
3. 将标签贴在桌面 → 碰一碰触发任务

**或用 Tasker 原生 NFC：**
```
Profile → NFC → 扫描标签
    → Link: Task "OpenClaw 晨报"
```

---

## JavaScriptlet 辅助函数库

在 Tasker 的 JavaScriptlet 中使用以下辅助函数：

```javascript
// 通用 HTTP POST 请求
function ocPost(path, body, apiKey) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://your-server' + path, false);
    xhr.setRequestHeader('Authorization', 'Bearer ' + apiKey);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(body));
    if (xhr.status === 200) {
        return JSON.parse(xhr.responseText);
    } else {
        throw new Error('HTTP ' + xhr.status + ': ' + xhr.responseText);
    }
}

// 触发定时任务
function triggerTask(templateId, name, params) {
    return ocPost('/api/v1/tasks', {
        name: name || 'Tasker触发',
        template_id: templateId,
        action: 'spawn',
        params: params || {}
    }, global('OC_API_KEY'));
}

// 发送钉钉消息
function sendDingtalk(message) {
    return ocPost('/api/v1/notify', {
        channel: 'dingtalk',
        message: message
    }, global('OC_API_KEY'));
}

// 查询状态
function getStatus(apiKey) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', 'https://your-server/api/v1/status', false);
    xhr.setRequestHeader('Authorization', 'Bearer ' + apiKey);
    xhr.send();
    return JSON.parse(xhr.responseText);
}

// 使用示例
try {
    const status = getStatus(global('OC_READONLY_KEY'));
    const gw = status.gateway_connected ? 'OK' : 'FAIL';
    setLocal('GW_STATUS', gw);
} catch(e) {
    setLocal('GW_STATUS', 'ERROR: ' + e.message);
}
```

---

## Tasker 变量配置

在 Tasker 中设置全局变量：

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `%OC_API_KEY` | `sk-xxxx-execute` | 执行权限 Key |
| `%OC_READONLY_KEY` | `sk-xxxx-readonly` | 只读权限 Key |
| `%OC_BASE_URL` | `https://your-server` | 服务地址 |
| `%OC_DINGTALK_WEBHOOK` | `https://oapi.dingtalk.com/...` | 钉钉 Webhook |

设置方式：
```
Tasks → 启动 OpenClaw → Edit → Variable Set
    Name: %OC_API_KEY
    To: sk-xxxxx
```

---

## AutoNotification 通知美化

安装 **AutoNotification** 插件，将 OpenClaw 任务结果美化为系统通知：

```
HTTP Request 完成后
    ↓
JavaScriptlet 解析响应
    ↓
AutoNotification
    ├─ Title: 🤖 OpenClaw 任务结果
    ├─ Text: %RESULT_SUMMARY
    ├─ Icon: (自定义 AI 图标)
    └─ Actions: [查看详情] [再次触发]
```

---

## AutoVoice + Google Assistant 语音控制

安装 **AutoVoice** 插件，实现自然语言控制：

```
配置示例：
"嘿 Google，生成今日简报" → Tasker 检测到 → 触发 HTTP Request
"嘿 Google，OpenClaw 状态" → Tasker 检测到 → 查询状态 + 语音播报
"嘿 Google，发送钉钉消息" → 弹出输入框 → 发送
```

---

## 安全性建议

| 建议 | 说明 |
|------|------|
| API Key 存储 | 用 Tasker 变量存储，不用硬编码在 Task 中 |
| HTTPS | 生产环境务必使用 HTTPS，防止 Key 被截获 |
| 只读 Key 查询 | 状态查询用 readonly Key |
| 执行 Key 管控 | 执行 Key 仅在需要触发任务时使用 |
| 家庭网络 | 建议配合 VPN（WireGuard）远程访问 |

---

## 调试技巧

```javascript
// 在 JavaScriptlet 中打印日志
console.log('响应:', xhr.responseText);

// 在 Tasker 中显示变量
Flash "%HTTPRESPONSE"
Flash "%HTTPCODE"

// 检查 Tasker 日志
Menu → Run Log（查看最近执行记录）
```
