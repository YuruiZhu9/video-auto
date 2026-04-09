# 视频解析 → 个人知识库（Obsidian/Notion）同步方案

> 🤖 Agent：视频解析方法总结Agent（小M）
> 📅 创建时间：2026-04-09
> 📁 路径：`/workspace/reports/video-parser/通用工具/`

---

## 一、核心工具/API

| 工具 | 功能描述 |
|------|---------|
| **Obsidian shell commands** | Obsidian 内置自动化，可触发外部脚本 |
| **obsidian-notion-sync（插件）** | Markdown → Notion 双向同步，保留富文本/表格/代码块 |
| **OpenClaw agents** | 视频解析完成后自动触发同步流程 |
| **Notion API** | 直接写入 Notion Database，字段：标题/标签/摘要/时间戳/原视频链接 |
| **Python（notion-client）** | 编程方式管理 Notion 页面和数据库 |
| **Obsidian Metadata Menu 插件** | 为视频笔记添加时间、来源、标签等元数据 |

---

## 二、完整工作流架构

```
视频 URL / 文件
       ↓
  OpenClaw Agent
  （视频解析任务）
       ↓
  ┌──────────────────┐
  │  结构化输出        │
  │  ├─ 摘要 Markdown │
  │  ├─ 时间戳目录     │
  │  ├─ 关键帧截图     │
  │  └─ 原始字幕 SRT   │
  └────────┬─────────┘
           ↓
  ┌─────────────────────────────────────┐
  │  同步触发方式（任选）                 │
  ├─ 方式A：Obsidian shell command       │
  ├─ 方式B：Python notionalient API      │
  ├─ 方式C：OpenClaw Cron 定时同步       │
  └─ 方式D：MCP 服务器事件驱动            │
           ↓
  ┌─────────────────────────┐
  │  个人知识库              │
  │  ├─ Obsidian（本地+图谱） │
  │  ├─ Notion（跨设备同步）  │
  │  └─ 双向增量同步（可选）   │
  └─────────────────────────┘
```

---

## 三、方案A：视频解析 → Obsidian 直接写入

### 步骤流程

**1. 安装 Obsidian 插件**
```
Settings → Community Plugins → 搜索安装：
- "Templater"（视频笔记模板）
- "Metadata Menu"（元数据管理）
- "Shell Commands"（触发外部脚本）
```

**2. 创建视频笔记模板（Templater）**
```markdown
---
title: "{{title}}"
source: "{{source}}"          <!-- B站/YouTube/本地 -->
url: "{{url}}"
date: {{date}}
duration: "{{duration}}"      <!-- 时长 -->
tags: [{{tags}}]              <!-- 自动打标签 -->
type: video-note
platform: {{platform}}
---

## 📌 视频摘要
{{summary}}

## 🕐 时间戳目录
{{timestamp_index}}

## 🔗 关键引用
{{key_quotes}}

## 📊 相关截图
![[frame_001.jpg]]
![[frame_002.jpg]]

## 🏷️ 关联标签
#{{primary_tag}} #视频笔记

## 📎 原始字幕
<srt>{{srt_content}}</srt>
```

**3. 触发脚本（Shell Commands 配置）**
```bash
# ~/.obsidian/shell_commands.json 或 Obsidian Settings → Shell Commands
# 触发命令：
python3 /workspace/scripts/video-to-obsidian.py \
  --input /workspace/parsing-output/video123/ \
  --obsidian-vault /path/to/your-vault/Vault/ \
  --template video-template
```

**4. Python 同步脚本**
```python
#!/usr/bin/env python3
"""video-to-obsidian.py - 将视频解析结果同步到 Obsidian"""
import os, json, argparse, shutil
from datetime import datetime
from pathlib import Path

def parse_output_dir(output_dir: str) -> dict:
    """解析输出目录，提取结构化内容"""
    base = Path(output_dir)
    return {
        "summary": (base / "summary.md").read_text() if (base / "summary.md").exists() else "",
        "timestamps": (base / "timestamps.txt").read_text() if (base / "timestamps.txt").exists() else "",
        "frames": list(base.glob("frames/*.jpg")),
        "srt": (base / "transcript.srt").read_text() if (base / "transcript.srt").exists() else "",
        "video_url": (base / "url.txt").read_text().strip() if (base / "url.txt").exists() else "",
    }

def build_obsidian_note(data: dict, template: str, vault_path: str, title: str) -> str:
    """生成 Obsidian Markdown 文件"""
    vault = Path(vault_path)
    out_dir = vault / "Video Notes" / datetime.now().strftime("%Y-%m")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{title[:50].replace('/','_').replace(' ','_')}.md"
    filepath = out_dir / filename
    
    # 处理截图链接
    frame_links = "\n".join(f"![[Video Notes/frames/{f.name}]]" for f in data["frames"])
    
    content = f"""---
title: "{title}"
source: video-parser
date: {datetime.now().isoformat()}
tags: [视频笔记]
type: video-note
---

# {title}

## 📌 摘要
{data['summary']}

## 🕐 时间戳目录
{data['timestamps']}

## 📊 关键帧
{frame_links}

## 📎 字幕原文（部分）
```
{data['srt'][:500]}...
```
"""
    filepath.write_text(content)
    
    # 复制截图到 Obsidian 附件目录
    frame_dir = out_dir / "frames"
    frame_dir.mkdir(exist_ok=True)
    for f in data["frames"]:
        shutil.copy(f, frame_dir / f.name)
    
    return str(filepath)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--obsidian-vault", required=True)
    ap.add_argument("--template", default="video-template")
    args = ap.parse_args()
    
    data = parse_output_dir(args.input)
    title = data["video_url"].split("watch?v=")[-1][:30] or "video-note"
    result = build_obsidian_note(data, args.template, args.obsidian_vault, title)
    print(f"✅ Obsidian note created: {result}")
```

---

## 四、方案B：视频解析 → Notion 数据库

### 步骤流程

**1. 创建 Notion Integration + Database**
- 访问 https://www.notion.so/my-integrations 创建 Integration（获取 API Key）
- 在 Notion 中创建 Database，字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 名称 | 标题 | 视频标题 |
| 来源平台 | 选择 | B站 / YouTube / 本地 |
| 视频链接 | URL | 原始链接 |
| 摘要 | 文本 | AI 生成摘要 |
| 时间戳目录 | 文本 | 带时间戳的章节 |
| 标签 | 多选 | AI / 推荐系统 / 视频 |
| 解析日期 | 日期 | 创建时间 |
| 字幕文件 | 文件 | SRT 字幕附件 |
| 状态 | 选择 | 待阅读 / 已阅读 / 重要 |

**2. Python 写入 Notion**
```python
from notion_client import NotionClient
from datetime import datetime

NOTION_TOKEN = "secret_xxxx"
DATABASE_ID = "xxxxx"

client = NotionClient(NOTION_TOKEN)

def create_video_note(title: str, url: str, summary: str, timestamps: str, tags: list):
    """创建视频笔记页面"""
    properties = {
        "名称": {"title": [{"text": {"content": title}}]},
        "来源平台": {"select": {"name": detect_platform(url)}},
        "视频链接": {"url": url},
        "摘要": {"rich_text": [{"text": {"content": summary[:2000]}}]},
        "时间戳目录": {"rich_text": [{"text": {"content": timestamps}}]},
        "标签": {"multi_select": [{"name": t} for t in tags]},
        "解析日期": {"date": {"start": datetime.now().isoformat()}},
        "状态": {"select": {"name": "待阅读"}},
    }
    return client.create_page(parent={"database_id": DATABASE_ID}, properties=properties)

# 使用示例
result = create_video_note(
    title="推荐系统架构详解",
    url="https://www.bilibili.com/video/BV1xxx",
    summary="本视频介绍推荐系统架构...",
    timestamps="[00:00] 概述\n[05:30] 召回层\n[15:00] 精排层",
    tags=["推荐系统", "AI", "架构"]
)
print(f"✅ Notion page created: {result['url']}")
```

**3. OpenClaw Cron 触发完整流程**
```yaml
# openclaw cron 配置示例
cron:
  video-to-notion:
    schedule: "0 2 * * *"  # 每天凌晨2点
    task: |
      1. 读取 /workspace/reports/video-workflow/pending/ 待处理视频列表
      2. 逐个调用 videos_understand 解析
      3. 调用 create_video_note() 写入 Notion
      4. 移动已处理视频到 /workspace/reports/video-workflow/processed/
      5. 发送钉钉通知
```

---

## 五、方案C：Obsidian ↔ Notion 双向同步

### obsidian-notion-sync 插件配置

```json
// Obsidian Settings → Notion Sync 插件配置
{
  "notionApiToken": "secret_xxxx",
  "targetDatabaseId": "xxxxx",
  "syncDirection": "bidirectional",
  "autoSync": true,
  "syncInterval": 30,  // 分钟
  "preserveFormatting": true,
  "syncImages": true,
  "syncCodeBlocks": true,
  "excludeProperties": ["解析日期", "状态"]
}
```

### 同步冲突解决策略
- **以 Obsidian 为准**：本地优先，适合经常离线使用
- **以 Notion 为准**：协作场景，团队共用
- **以时间戳决胜**：最新修改覆盖旧版本
- **手动解决**：重要笔记弹出冲突提示

---

## 六、适用场景

| 场景 | 推荐方案 |
|------|---------|
| 个人知识管理，本地优先 | Obsidian 直接写入 + 图谱可视化 |
| 团队协作，跨设备访问 | Notion 数据库 |
| 长期存档 + 快速检索 | Obsidian + Notion 双向同步 |
| 批量视频笔记管理 | OpenClaw Cron + Notion API |
| 研究项目文献管理 | Obsidian + Zotero 联动 |

---

## 七、避坑指南

| 问题 | 解决方案 |
|------|---------|
| Notion API 同步图片失败 | 使用 Obsidian 附件目录而非 Notion（Notion 文件上传需单独 API） |
| 同步循环（Obsidian ↔ Notion） | 设置单向同步或使用 syncDirection 标记来源优先 |
| 中文标签在 Obsidian 图谱乱码 | 使用英文标签名，Notion 用中文多选 |
| 视频笔记过多导致 Obsidian 变慢 | 使用 `{{date:YYYY-MM}}` 按月分目录 + 只在需要时打开 |
| Notion API 速率限制 | 添加 500ms 延迟，批量时用 exponential backoff |
| 字幕文件 SRT 过大 | 只同步前 1000 行，或拆分按章节创建子页面 |

---

## 八、参考工具链接

- Obsidian：https://obsidian.md
- Notion API：https://developers.notion.com
- obsidian-notion-sync 插件：https://llmbase.ai/openclaw/obsidian-notion/
- OpenClaw + Obsidian 记忆同步：https://eastondev.com/blog/zh/posts/ai/20260227-openclaw-obsidian-sync/

---

*本文档由视频解析方法总结Agent 自动生成 — 2026-04-09*
