# TikHub-Bilibili 专业弹幕解析 — B站弹幕提取与情绪分析

## 核心工具/API

| 工具 | 用途 |
|------|------|
| **TikHub API** | B站视频元数据+字幕+弹幕一站式获取 |
| **TikHub MCP Server** | Model Context Protocol 标准化接口 |
| **BiliBili 官方弹幕 API** | 直接抓取实时弹幕 XML（需逆向） |
| **BiliAPI / Bilibili-API** | Python 弹幕/评论/用户数据抓取 |
| **弹幕在线解析站** | 无需代码的 Web 端弹幕提取 |

---

## 核心技术方法

### 1. TikHub MCP Server（B站生态）

TikHub MCP 是一个标准化的 B站 数据获取工具，通过 Model Context Protocol 与 Claude/OpenClaw 等 AI 助手无缝集成：

**支持能力：**
- ✅ 视频元数据（标题、UP主、播放量、标签）
- ✅ 字幕提取（SRT/ASS/JSON 格式）
- ✅ 弹幕抓取（带时间戳、用户属性）
- ✅ 评论提取（热评、楼层结构）
- ✅ UP主信息与粉丝数据

**典型调用：**
```json
// MCP 工具调用示例
{
  "tool": "tikhub_bilibili_video_info",
  "params": { "bvid": "BV1xx411c7mD" }
}

{
  "tool": "tikhub_bilibili_danmu",
  "params": { "bvid": "BV1xx411c7mD" }
}
```

**OpenClaw 集成方式：**
```bash
# 通过 MCP 工具调用 TikHub
openclaw mcp add tikhub -- python -m tikhub.mcp
```

---

### 2. 弹幕数据结构

TikHub 提取的弹幕数据格式：

```json
{
  "dm_id": 12345678,
  "progress": 45000,       // 弹幕出现时间（毫秒）
  "content": "这个知识点太棒了",
  "color": "ffffff",        // 弹幕颜色
  "font_size": 25,
  "pool_type": 0,          // 弹幕池（普通/高级）
  "user_id": 12345678,
  "nickname": "xxx",
  "like_count": 520,
  "send_time": "2024-03-15 18:30:00",
  "弹幕类型": "普通弹幕"    // 普通/增强/BAS特效
}
```

---

### 3. 弹幕分析方法论

弹幕是 B站 视频的独特副语言，包含大量观众实时反馈：

#### 3.1 弹幕情绪分析

```python
from collections import Counter
import re

def analyze_danmu_sentiment(danmu_list):
    """弹幕情绪分析"""
    positive_keywords = ["厉害", "太强了", "学到了", "点赞", "顶", "棒", "绝了"]
    negative_keywords = ["听不懂", "太难了", "废话", "垃圾", "退钱"]
    question_keywords = ["怎么", "为什么", "请问", "有没有", "不懂"]
    
    positive = sum(1 for d in danmu_list if any(k in d['content'] for k in positive_keywords))
    negative = sum(1 for d in danmu_list if any(k in d['content'] for k in negative_keywords))
    questions = sum(1 for d in danmu_list if any(k in d['content'] for k in question_keywords))
    
    return {
        "正向": positive,
        "负向": negative,
        "疑问": questions,
        "正向占比": round(positive / len(danmu_list) * 100, 1),
        "整体情绪": "正面" if positive > negative else "中性/争议"
    }

def extract_hot_moments(danmu_list, min_likes=100):
    """提取高互动弹幕（热时刻）"""
    hot = [d for d in danmu_list if d['like_count'] >= min_likes]
    hot.sort(key=lambda x: x['like_count'], reverse=True)
    return hot[:20]  # Top 20 热弹
```

#### 3.2 弹幕时间密度分析

```python
import pandas as pd

def danmu_density_analysis(danmu_list, video_duration_ms):
    """弹幕密度热力图"""
    # 每10秒统计弹幕数量
    bucket_size = 10000  # 10秒
    buckets = (video_duration_ms // bucket_size) + 1
    density = [0] * buckets
    
    for d in danmu_list:
        idx = d['progress'] // bucket_size
        if idx < buckets:
            density[idx] += 1
    
    # 找出弹幕高密度区间（知识点/高潮时刻）
    threshold = max(density) * 0.6
    hot_segments = [(i * 10, (i+1) * 10, c) 
                    for i, c in enumerate(density) if c >= threshold]
    return density, hot_segments
```

---

## 适用场景

| 场景 | 方法 | 价值 |
|------|------|------|
| **技术教程优化** | 弹幕密度 → 找观众困惑点 | 优化讲解节奏 |
| **行业分享分析** | 情绪分析 → 识别共鸣/争议内容 | 内容质量评估 |
| **竞品视频对比** | 多视频弹幕对比 | 用户需求挖掘 |
| **热点追踪** | 弹幕热词提取 | 实时舆情监控 |
| **内容创作灵感** | 热弹内容整理 | 生成新视频选题 |

---

## 避坑指南

### ⚠️ 弹幕抓取常见问题

**Q1: 弹幕池限制**
- B站有普通弹幕池和增强弹幕池，部分视频只显示普通池
- 解决：TikHub 默认抓全池；如需高级弹幕需登录态

**Q2: 时间戳偏移**
- 长视频弹幕存在分段加载，时间戳可能不连续
- 解决：用视频总时长校准弹幕进度

**Q3: API 限流**
- B站对非官方 API 有严格频率限制（60次/分钟）
- 解决：加请求间隔、使用 TikHub MCP 代理（自带速率控制）

**Q4: 弹幕去重**
- 同一弹幕可能被多人发送，需要去重
- 解决：`Counter` 统计 + 按 `dm_id` 去重

**Q5: 隐私合规**
- 用户弹幕数据涉及个人信息，需脱敏处理
- 解决：只分析内容，不存储/追踪用户 ID

---

## 推荐分析 Prompt 模板

```python
# 弹幕分析完整 Prompt
ANALYZE_DANMU_PROMPT = """
你是一位 B站 视频内容分析师。请对以下弹幕数据进行分析：

1. **弹幕密度热力图**：每10秒弹幕数量，找出视频高潮时刻
2. **情绪分析**：正向/负向/中性占比，整体情绪倾向
3. **热词提取**：出现频率最高的弹幕关键词（top 30）
4. **观众反馈要点**：
   - 观众最认可的知识点（高赞弹幕）
   - 观众最困惑的地方（高频疑问弹幕）
   - 观众的建议或补充
5. **互动峰值分析**：弹幕数量最多的时间点及原因推测

弹幕数据（共 {count} 条）：
{content}

请输出一份结构化分析报告，包含Markdown格式表格和文字总结。
"""
```

---

## 工具对比：TikHub vs 官方 API vs 爬虫

| 维度 | TikHub MCP | B站官方 API | 自建爬虫 |
|------|-----------|-----------|---------|
| **弹幕获取** | ✅ 完整 | ⚠️ 需登录 | ✅ 完整 |
| **字幕提取** | ✅ 支持 | ✅ 部分 | ✅ 可行 |
| **无需登录** | ✅ | ❌ | ✅ |
| **速率限制** | 内置重试 | 严格 | 需自控 |
| **维护成本** | 低 | 中 | 高 |
| **OpenClaw 集成** | ✅ MCP 原生 | ❌ 需适配 | ❌ |

---

## 参考链接

- TikHub 官网：https://tikhub.io
- TikHub GitHub：https://github.com/Evilsocket/tikhub
- Bilibili API 文档：https://github.com/SocialSisterYi/bilibili-API-collect
- TikHub MCP Server：https://github.com/SocialSisterYi/tikhub-mcp
