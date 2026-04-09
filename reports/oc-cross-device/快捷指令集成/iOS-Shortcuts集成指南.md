# iOS 快捷指令集成指南 (v2.8.0)

> 所属项目：[OpenClaw 跨设备控制框架 (clawctl)](../README.md)

> 一句话说清楚要什么，OpenClaw 自动执行 — 无需打开 App

---

## 核心原理

```
┌──────────────────────────────────────────────────────────────┐
│                  iOS 快捷指令 × OpenClaw                      │
│                                                              │
│  用户：Hey Siri "AI简报"                                      │
│       ↓                                                       │
│  快捷指令：触发 GET /api/v1/shortcuts/cmd?q=AI简报            │
│       ↓                                                       │
│  OpenClaw NL Routes：自然语言解析 + 执行任务                  │
│       ↓                                                       │
│  钉钉/微信：收到任务执行结果推送 🎉                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 快速开始（3 步）

### 第 1 步：安装快捷指令

1. 打开 iOS **快捷指令 App**
2. 点击 **+** 创建新快捷指令
3. 添加 **"URL"** 动作
4. 输入：`https://你的服务器地址/api/v1/shortcuts/cmd`
5. 添加 **"获取内容"** 动作（将 URL 传入）
6. 配置：**方法 = GET**，**内容类型 = JSON**

### 第 2 步：添加触发参数

在快捷指令中，URL 的 Query 参数可以动态设置：

| 参数 | 说明 | 示例 |
|------|------|------|
| `q` | 自然语言指令 | `生成今日技术简报` |
| `channel` | 通知渠道 | `dingtalk` / `telegram` |
| `template` | 快捷指令模板ID | `quick_report` |

**快捷指令 URL 示例：**
```
https://your-server.com/api/v1/shortcuts/cmd?q=生成今日技术简报&channel=dingtalk
```

### 第 3 步：配置 Siri 语音触发

1. 在快捷指令详情页，点击 **🏷 图标**
2. 输入 **Siri 短语**，如：`AI简报`
3. 以后对 Siri 说 **"Hey Siri，AI简报"** 即可触发

---

## 推荐快捷指令模板

### 📋 日常使用（建议全部导入）

| 快捷指令 | Siri 短语 | 触发内容 |
|---------|----------|---------|
| 生成今日简报 | `AI简报` | 生成当日AI热点简报 |
| AI热点新闻 | `AI新闻` | 实时抓取AI领域热门资讯 |
| 技术前沿扫描 | `技术扫描` | 深度扫描技术前沿动态 |
| 市场动态洞察 | `市场洞察` | 分析AI商业应用和创业公司 |
| 全面信息扫描 | `全面扫描` | 全量执行信息抓取+分析 |

### ⚡ 快速查询（按需导入）

| 快捷指令 | Siri 短语 | 触发内容 |
|---------|----------|---------|
| 查看系统状态 | `系统状态` | 查询OpenClaw运行状态 |
| 最近任务记录 | `任务记录` | 查看最近10条任务历史 |
| 待处理任务 | `待办任务` | 查看排队/失败任务 |

### 🎯 个性化分析（高级用户）

| 快捷指令 | Siri 短语 | 触发内容 |
|---------|----------|---------|
| 推荐系统分析 | `推荐分析` | 专注推荐系统算法进展 |
| 大模型进展 | `大模型` | 追踪GPT/Claude/国产大模型 |
| 就业市场分析 | `求职市场` | 分析推荐算法岗位需求 |
| 本周论文速递 | `论文推荐` | 筛选本周最值得读的AI论文 |

---

## 进阶用法

### 方式 1：使用"查找 URL"动作（推荐）

适合需要动态参数的快捷指令：

```
1. 添加"文本"动作 → 输入 Siri 短语
2. 添加"URL"动作 → https://your-server.com/api/v1/shortcuts/cmd
3. 添加"查找/替换文本" → 将 URL 中的 {{q}} 替换为步骤1的文本
4. 添加"获取内容"动作 → URL = 步骤3结果，方法=GET
```

### 方式 2：使用"输入"动作（最简单）

适合固定指令的快捷指令：

```
1. 添加"文本"动作 → "生成今日技术简报"
2. 添加"URL"动作 → https://your-server.com/api/v1/shortcuts/cmd?q={{1}}&channel=dingtalk
3. 添加"获取内容"动作
```

### 方式 3：Shortcuts App 的"运行 JavaScript"（高级）

```javascript
// 从快捷指令列表获取并执行
const shortcuts = await fetch('https://your-server.com/api/v1/shortcuts/mobile');
const shortcutsJson = shortcuts.json();
const target = shortcutsJson.shortcuts.find(s => s.title.includes('简报'));
const result = await fetch(target.url);
const json = result.json();
console.log(json.message || json.error);
```

---

## URL Scheme 协议

### clawctl:// 协议

OpenClaw 支持 `clawctl://` 自定义 URL Scheme，可在 App 唤起时使用：

```
clawctl://run?q=生成今日简报&api_key=sk-xxx
clawctl://message?text=查一下AI新闻&channel=dingtalk
clawctl://status?api_key=sk-xxx
clawctl://schedule?template=full_scan&time=tomorrow
```

### iOS App 配置

在 iOS 的 `Info.plist` 中声明 URL Scheme：

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>clawctl</string>
    </array>
  </dict>
</array>
```

---

## API 端点一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/shortcuts` | 快捷指令库（iOS 快捷指令"获取内容"用） |
| GET | `/api/v1/shortcuts/library` | 导出完整快捷指令库 JSON |
| GET | `/api/v1/shortcuts/mobile` | 移动端专用格式 |
| GET | `/api/v1/shortcuts/{id}` | 单个快捷指令详情 |
| POST | `/api/v1/shortcuts/parse` | 解析 clawctl:// URL |
| **GET** | **`/api/v1/shortcuts/cmd`** | **🚀 核心端点：iOS 快捷指令专用** |
| GET | `/api/v1/shortcuts/share/{id}` | 生成分享链接 |

---

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `q 参数为空` | URL 中未指定 q 参数 | 在快捷指令 URL 中添加 `?q=你的指令` |
| `NL Routes 未启动` | 后端 NL 模块未加载 | 检查 server.py 日志，确保 nl_routes 可用 |
| `401 Unauthorized` | API Key 无效 | 在 URL 中添加 `&api_key=your_key` |
| `快捷指令不存在` | template ID 错误 | 使用正确的模板 ID，如 `quick_report` |

### 调试方法

1. **在浏览器中测试**：直接访问快捷指令 URL 查看返回结果
2. **查看服务端日志**：`tail -f /workspace/reports/oc-cross-device/logs/server.log`
3. **使用预览模式**：`/api/v1/shortcuts/cmd?q=...&intent_only=true`（只解析，不执行）

---

## 安全配置

### API Key 分级

| Key 级别 | 权限 | 适用场景 |
|---------|------|---------|
| `read` | 只读 | 快捷指令（仅查询状态） |
| `exec` | 可执行 | 完整功能快捷指令 |
| `admin` | 管理权限 | ⚠️ 不建议放快捷指令中 |

### 建议配置

```python
# 在 OpenClaw 配置中设置只允许特定 IP 范围
{
  "shortcuts": {
    "allowed_ips": ["10.0.0.0/8", "192.168.0.0/16"],
    "max_exec_per_minute": 10,
    "require_confirmation": ["full_scan", "market_pulse"]
  }
}
```

---

## Siri 短语设计建议

**好用的 Siri 短语：**
- ✅ `AI简报` / `AI新闻` — 简短，容易记
- ✅ `技术扫描` — 明确意图
- ✅ `市场洞察` — 与快捷指令名一致
- ❌ `帮我生成今日技术简报并发到钉钉` — 太长，Siri 识别困难

**命名规范：**
```
动词 + 对象（可省略）
AI + 名词
快捷指令名（保持一致）
```
