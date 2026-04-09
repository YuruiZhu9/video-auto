# OpenClaw bibigpt-skill 全攻略 — BibiGPT 全平台视频 AI 总结

## 核心工具/API

| 工具 | 用途 |
|------|------|
| **BibiGPT** | 一键提取 B站/YouTube/小鹅通等平台视频核心内容 |
| **bibigpt-skill** | OpenClaw 官方 Skill，一句话触发 BibiGPT 总结 |
| **BibiGPT API** | 批量视频自动总结 + 定时推送 |
| **Webhook / 消息推送** | 总结完成后推送到钉钉/Telegram 等渠道 |
| **UP主订阅功能** | 自动追踪目标 UP 主新视频并总结 |

---

## bibigpt-skill 是什么

bibigpt-skill 是 OpenClaw 的官方技能插件，让用户无需打开 BibiGPT 网站，在任意对话中一句话完成视频总结：

```
用户：帮我总结这个 B站 视频：https://www.bilibili.com/video/BV1xx411c7mD
         ↓ OpenClaw 自动调用 bibigpt-skill
         ↓ 调用 BibiGPT API 完成总结
用户收到：结构化总结报告（核心观点 + 关键数据 + 金句）
```

---

## 核心技术方法

### 1. BibiGPT 总结流程

BibiGPT 的核心处理流程：

```
视频URL → 音视频下载 → 语音转写（Whisper）→ AI 提炼 → 结构化输出
```

**支持平台：**
- ✅ B站（BV号 / av号 / 合集）
- ✅ YouTube / YouTube Shorts
- ✅ 小鹅通
- ✅ 微信公众号视频
- ✅ 微博视频
- ✅ 知乎视频
- ✅ 抖音（部分）
- ✅ Vimeo / Twitter / TED

**输出格式：**
- 核心要点（3-7 条）
- 时间戳目录（可跳转）
- 思维导图（可选）
- 字幕原文（可选）
- AI 播客（文字转音频，可选）

---

### 2. bibigpt-skill 在 OpenClaw 中的配置

**安装方式：**
```bash
# 通过 OpenClaw 安装 bibigpt-skill
openclaw skills add bibigpt

# 或通过 clawhub 安装
openclaw clawhub install bibigpt
```

**环境变量配置：**
```bash
# BibiGPT API Key（BibiGPT 官网获取）
BIBIGPT_API_KEY=your_api_key_here

# 可选：自定义 API 地址（国内用户）
BIBIGPT_API_BASE=https://bibigpt.co/api
```

**调用方式：**
```
触发词（任意一个）：
- "用 bibigpt 总结这个视频"
- "bibigpt: https://xxx"
- "BibiGPT 这个 B站 视频"
- "帮我 AI 总结 B站视频"
```

---

### 3. BibiGPT API 深度用法

#### 3.1 单视频总结（API 调用）

```python
import requests

def bibigpt_summarize(url, api_key):
    """调用 BibiGPT API 总结视频"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "model": "gpt-4",           # 可选：gpt-4 / gpt-3.5 / claude
        "language": "zh",            # 输出语言
        "template": "outline",       # 模板：outline / mindmap / transcript
        "highlights": True,         # 是否提取亮点
        "timestamps": True,          # 是否包含时间戳
    }
    
    # 异步提交任务
    resp = requests.post(
        "https://bibigpt.co/api/v1/summarize",
        headers=headers, json=payload
    )
    task_id = resp.json()["task_id"]
    
    # 轮询结果
    for _ in range(60):
        result = requests.get(
            f"https://bibigpt.co/api/v1/tasks/{task_id}",
            headers=headers
        )
        if result.json()["status"] == "completed":
            return result.json()["data"]
        time.sleep(5)
    
    return None

# 典型输出结构
{
  "title": "视频标题",
  "summary": "核心总结文字...",
  "highlights": [
    {"time": "00:05:20", "content": "关键知识点1"},
    {"time": "00:12:30", "content": "关键知识点2"},
  ],
  "timestamps": [
    {"time": "00:00:00", "title": "开场介绍"},
    {"time": "00:03:00", "title": "核心内容1"},
  ],
  "mindmap": "思维导图 JSON...",
  "transcript": "完整字幕文字..."
}
```

#### 3.2 批量总结 + 自动推送

```python
def batch_summarize_and_push(urls, channel="dingtalk"):
    """批量总结 + 推送"""
    results = []
    for url in urls:
        result = bibigpt_summarize(url, API_KEY)
        if result:
            report = format_report(result)
            # 推送到钉钉
            message.send(channel=channel, message=report)
        time.sleep(3)  # 避免 API 限流
    return results
```

#### 3.3 UP主自动追踪

```python
def track_up主(bvid_list, push_channel):
    """追踪指定 UP 主新视频并自动总结"""
    seen = load_seen_bvids()
    
    for bvid in bvid_list:
        latest = get_latest_video(bvid)  # B站 API 获取最新视频
        if latest['bvid'] not in seen:
            summary = bibigpt_summarize(latest['url'], API_KEY)
            message.send(
                channel=push_channel,
                message=f"📺 {latest['title']}\n\n{summary['summary']}"
            )
            add_to_seen(latest['bvid'])
    
    # 建议配合 cron 定时执行（每2小时一次）
```

---

## 适用场景

| 场景 | 使用方式 | 价值 |
|------|---------|------|
| **B站技术教程** | 一句话总结 + 时间戳目录 | 快速判断是否值得看 |
| **行业分享/演讲** | AI 播客功能 → 通勤听 | 碎片时间利用 |
| **知识管理** | 批量总结 → 存入笔记库 | 构建个人知识库 |
| **竞品监控** | 追踪目标 UP 主 → 定时推送 | 竞品动态追踪 |
| **内容创作灵感** | 批量总结 → 提取热门观点 | 选题参考 |

---

## 避坑指南

### ⚠️ BibiGPT 使用常见问题

**Q1: API Key 获取**
- BibiGPT 官网注册后，在设置 → API 中获取
- 免费版有次数限制（5次/天）；Pro 版无限制
- 国内用户注意 API 域名可能需要代理

**Q2: 视频过长导致超时**
- BibiGPT 对超长视频（>2h）可能超时
- 解决：先用 FFmpeg 截取关键片段再总结

**Q3: B站独家内容限制**
- B站部分大会员专属视频无法通过 BibiGPT 解析
- 解决：需要本地下载后手动上传

**Q4: API 费用**
- BibiGPT API 按调用次数计费
- 建议开启用量告警，避免意外超支

**Q5: 推送格式优化**
- 钉钉推送有字数限制（2048字）
- 解决：设置 `max_length`，只推送摘要部分

---

## bibigpt-skill + OpenClaw 工作流

```
┌─────────────────────────────────────────────────────┐
│                  bibigpt-skill 工作流                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  触发 → bibigpt-skill 拦截                          │
│    ↓                                                │
│  判断：是否 B站/YouTube 视频 URL？                    │
│    ↓ 是                                            │
│  调用 BibiGPT API（异步提交）                         │
│    ↓                                                │
│  轮询结果（最多60次 × 5秒 = 5分钟）                    │
│    ↓                                                │
│  格式化输出：摘要 + 时间戳 + 亮点                     │
│    ↓                                                │
│  通过当前 channel 返回给用户                         │
│                                                     │
│  [可选] Cron 定时：UP主追踪 + 自动推送                 │
└─────────────────────────────────────────────────────┘
```

---

## 参考链接

- BibiGPT 官网：https://bibigpt.co
- BibiGPT API 文档：https://bibigpt.co/docs/api
- OpenClaw bibigpt-skill：clawhub 安装
- B站 API 参考：https://github.com/SocialSisterYi/bilibili-API-collect
