# iOS 快捷指令集成指南

> 通过 iOS 快捷指令（Shortcuts）实现 Siri 语音控制 OpenClaw，随时随地一句话搞定任务。

---

## 目录

1. [快速开始（3步完成）](#1-快速开始3步完成)
2. [URL Scheme 协议说明](#2-url-scheme-协议说明)
3. [推荐快捷指令模板](#3-推荐快捷指令模板)
4. [Siri 语音触发配置](#4-siri-语音触发配置)
5. [添加到主屏幕](#5-添加到主屏幕)
6. [高级用法](#6-高级用法)

---

## 1. 快速开始（3步完成）

### Step 1: 获取 API Key

在 OpenClaw 控制台（`/api/v1/keys`）创建一个 **execute** 级别的 Key：

```
sk-oc-execute-xxxxxxxxxxxxx
```

> ⚠️ 推荐只授予 `execute` 级别权限，不要使用 admin Key。

### Step 2: 构造 URL

```bash
# 格式
clawctl://run?template=模板ID&api_key=你的KEY&name=任务名

# 示例：触发快速信息抓取
clawctl://run?template=quick_fetch&api_key=sk-oc-execute-xxxxxxxxxxxxx&name=iOS快速抓取

# 示例：发送钉钉消息
clawctl://message?text=服务器状态正常&channel=dingtalk&api_key=sk-oc-execute-xxxxxxxxxxxxx
```

### Step 3: 创建快捷指令

1. 打开 **快捷指令** App
2. 点击 **+** 新建
3. 添加操作：**打开 URL**
4. 填入上面构造的 URL
5. 点击 **···** 设置名称和图标
6. 完成！点击即可执行

---

## 2. URL Scheme 协议说明

### 2.1 触发任务执行

```
clawctl://run
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `template` | string | ✅ | 任务模板 ID |
| `api_key` | string | ✅ | 你的 execute API Key |
| `name` | string | ❌ | 自定义任务名称 |
| `params` | JSON | ❌ | 任务参数（URL 编码） |

**示例：**

```
clawctl://run?template=tech_brief&api_key=sk-oc-execute-xxx&name=Siri技术简报
```

### 2.2 发送消息

```
clawctl://message
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | ✅ | 消息内容 |
| `channel` | string | ✅ | 渠道：`dingtalk` / `feishu` / `telegram` |
| `api_key` | string | ✅ | API Key |

**示例：**

```
clawctl://message?text=回家路上记得买菜&channel=dingtalk&api_key=sk-oc-execute-xxx
```

### 2.3 查询状态

```
clawctl://status
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `api_key` | string | ✅ | API Key |

**示例：**

```
clawctl://status?api_key=sk-oc-execute-xxx
```

---

## 3. 推荐快捷指令模板

### 模板一：Siri "AI 早报"

> 一句话让 Siri 生成今日 AI 早报，推送到钉钉。

**快捷指令内容：**

```
快捷指令名称：AI 早报
触发词：Hey Siri，AI 早报

操作序列：
1. [文本] 内容："生成今日AI资讯简报，输出Markdown格式，发送到钉钉"
2. [打开URL]
   URL: clawctl://run?template=quick_fetch&api_key=sk-oc-execute-xxx&name=AI早报
3. [显示通知] 标题："AI 早报已触发" 内容："正在生成中，稍后推送到钉钉"
```

---

### 模板二：快速状态检查

> 一句话检查 OpenClaw 系统状态。

```
快捷指令名称：检查系统状态
触发词：Hey Siri，检查 AI 服务器

操作序列：
1. [打开URL]
   URL: clawctl://status?api_key=sk-oc-execute-xxx
2. [显示结果] 展示网页内容
```

---

### 模板三：商业洞察速报

> 快速获取当日商业 AI 应用动态。

```
快捷指令名称：商业速报
触发词：Hey Siri，商业洞察

操作序列：
1. [打开URL]
   URL: clawctl://run?template=biz_brief&api_key=sk-oc-execute-xxx&name=商业速报
2. [显示通知] 标题："商业洞察已触发"
```

---

### 模板四：发送快捷笔记

> 随时记录想法，自动发送到 OpenClaw 存档。

```
快捷指令名称：AI 笔记
触发词：Hey Siri，记笔记 [内容]

操作序列：
1. [要求输入] 提示："记什么？"  （也可用 Siri 语音输入）
2. [打开URL]
   URL Template:
   clawctl://message?text={{-clipboard}}&channel=dingtalk&api_key=sk-oc-execute-xxx
   （配合剪贴板使用）
3. [显示通知] 标题："笔记已保存"
```

---

### 模板五：定时任务管理

> 用快捷指令管理定时任务。

```
快捷指令名称：开启晨报
触发词：Hey Siri，开启 AI 晨报

操作序列：
1. [打开URL]
   URL: clawctl://schedule?action=enable&job=daily_brief&api_key=sk-oc-execute-xxx
```

---

## 4. Siri 语音触发配置

### 4.1 设置 Siri 短语

在快捷指令详情页，点击 **⌷ 图标** → **添加到 Siri**：

- "AI 早报" → 说出 "AI 早报"
- "商业洞察" → 说出 "商业洞察"
- "检查服务器" → 说出 "检查服务器状态"

### 4.2 离线使用

所有快捷指令均为本地执行，不依赖网络（API 调用时才需要网络）。

### 4.3 快捷指令小组件

添加到 iOS 主屏幕小组件（快捷指令小组件），一键触达：

1. 长按主屏幕 → 点击左上角 **+**
2. 搜索 **快捷指令**
3. 选择 **快捷指令** 小组件
4. 拖动到主屏幕
5. 小组件显示你常用的快捷指令，点击即可执行

---

## 5. 添加到主屏幕

### 5.1 快捷指令图标

1. 打开快捷指令 App
2. 长按你的指令 → 点击 **···**
3. 点击 **图标** 更换（推荐使用 🤖 或 🔔 等）
4. 设置**颜色**（推荐蓝色）

### 5.2 添加到主屏幕

1. 在快捷指令详情页
2. 点击 **···** → **添加到主屏幕**
3. 编辑名称 → 点击 **添加**
4. 完成！主屏幕出现图标

### 5.3 主屏幕布局建议

```
┌────────┬────────┬────────┐
│  AI早报 │ 商业洞察│ 状态检查│
│  🤖    │  📊    │  🔍    │
├────────┼────────┼────────┤
│ 记忆备份│ 发消息  │ 定时任务│
│  💾    │  💬    │  ⏰    │
└────────┴────────┴────────┘
```

---

## 6. 高级用法

### 6.1 与 iOS 自动化联动

**场景：到家时自动触发信息抓取**

1. 打开快捷指令 → **自动化** → **创建个人自动化**
2. 触发条件：**到达** → 选择地点（家）
3. 操作：**运行快捷指令** → 选择 "AI 早报"
4. 关闭运行前询问（可选）

> 到家后 iPhone 自动触发，OpenClaw 开始抓取信息，推送到钉钉。

---

### 6.2 与提醒事项联动

**场景：Siri 记录想法 → OpenClaw 存档**

```
快捷指令：Siri 记录想法
触发词：Hey Siri，记 [内容]

1. [听写文本] → 保存到变量 content
2. [打开URL]
   URL: clawctl://message?text={{content}}&channel=dingtalk&api_key=sk-oc-execute-xxx
3. [创建提醒事项] 标题："已发送到 AI" 内容：{{content}}
```

---

### 6.3 带参数的任务触发

使用快捷指令的 **变量** 功能，传递自定义参数：

```
快捷指令：AI 分析
触发词：Hey Siri，分析 [内容]

1. [听写文本] → 保存到变量 query
2. [URL编码] {{query}} → 保存到 encoded
3. [打开URL]
   URL: clawctl://run?template=tech_analysis&api_key=sk-oc-execute-xxx&params={"query":"{{encoded}}"}
```

---

### 6.4 快捷指令 + iOS 锁屏小组件

在锁屏界面添加快捷指令小组件（iOS 16+）：

1. 锁屏编辑模式 → 添加小组件 → 搜索 **快捷指令**
2. 拖入小组件即可在锁屏直接触发

---

## 安全建议

1. **不要**在快捷指令中硬编码 admin Key，用 execute 级别
2. **不要**通过任何公开渠道分享你的 Key
3. 建议在钉钉中开启**签名验证**（Secret）
4. 定期（每 30 天）轮换 Key

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| URL Scheme 不生效 | 确认服务器可公网访问；检查 `clawctl://` 是否注册 |
| Siri 无法触发 | 在快捷指令 → 设置中重新添加 Siri 短语 |
| 返回 401 Unauthorized | 检查 API Key 是否正确、是否过期 |
| 无响应 | 检查服务器是否在线，端口是否放行 |
| 消息发送成功但无推送 | 检查钉钉 Webhook URL 和 Secret |

---

## 参考链接

- [OpenClaw 控制台](http://localhost:18790)
- [clawctl API 文档](http://localhost:18790/api/v1/docs)
- [iOS 快捷指令官方指南](https://support.apple.com/zh-cn/HT211052)
