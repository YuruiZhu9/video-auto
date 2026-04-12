# YouTube Watcher — ClawHub字幕抓取工具

> 🤖 分类：通用方法/第三方Skill
> 📅 更新日期：2026-04-12
> 📌 来源：ClawHub（`clawhub.ai/skills/youtube-watcher`）
> ⭐ 热度：🔥 254星 | 📥 41.9k安装

---

## 核心工具/API

| 工具 | 功能描述 | 角色 |
|------|---------|------|
| **yt-dlp** | 抓取YouTube视频字幕/字幕文件 | 字幕获取 |
| **Python脚本** | 解析字幕文件，清理并输出纯文本 | 文本处理 |

---

## 步骤流程

### 3步完成YouTube视频字幕提取

```
视频URL → yt-dlp字幕抓取 → 文本清理 → 标准输出
```

### 详细步骤

**1. 安装依赖**
```bash
brew install yt-dlp
# 或
pip install yt-dlp
```

**2. 安装Skill（ClawHub）**
```bash
npx clawhub@latest install youtube-watcher
```

**3. 抓取字幕**
```bash
# 基本用法
youtube-watcher "https://www.youtube.com/watch?v=VIDEO_ID"

# 指定语言
youtube-watcher "URL" --lang zh-Hans

# 输出到文件
youtube-watcher "URL" > transcript.txt
```

---

## 输出格式

```
[00:00] 欢迎来到今天的教程
[00:15] 今天我们来学习如何使用OpenClaw
[00:32] 首先需要安装yt-dlp
...
```

---

## 适用场景

- **快速字幕提取**：不需要视频文件，只需字幕文本
- **技术教程总结**：提取字幕后用LLM总结要点
- **B站/YouTube内容监控**：批量抓取频道视频字幕
- **多语言翻译**：抓取字幕作为翻译素材
- **搜索引擎优化**：将视频字幕文本化便于检索

---

## 避坑指南

### 问题1：视频无字幕
- **问题**：部分视频关闭了字幕功能
- **解决**：
  ```bash
  # 检查可用字幕
  yt-dlp --list-subs "VIDEO_URL"
  # 强制转录（无字幕时使用Whisper）
  yt-dlp --write-auto-sub --skip-download "VIDEO_URL"
  ```

### 问题2：字幕语言不对
- **问题**：抓取到非目标语言字幕
- **解决**：指定语言代码
  ```bash
  yt-dlp --write-subs --sub-langs "zh-Hans,en" "URL"
  ```

### 问题3：字幕时间戳混乱
- **问题**：输出包含大量元数据
- **解决**：使用清理脚本去除格式符号
  ```bash
  youtube-watcher "URL" | sed 's/<[^>]*>//g' > clean.txt
  ```

---

## 与知识库同类工具对比

| 维度 | YouTube Watcher | summarize | bibigpt-skill | yt-dlp+Whisper |
|------|----------------|-----------|---------------|----------------|
| 字幕抓取速度 | ⚡ 秒级 | ⚡ 秒级 | ⚡ 秒级 | ❌ 需额外步骤 |
| Whisper转录 | ❌ | ✅ | ✅ | ✅ |
| 多平台支持 | YouTube专属 | YouTube+B站 | YouTube+B站等 | 所有平台 |
| 安装复杂度 | ⭐ 一键 | ⭐ 内置 | 中等 | 中 |
| 星标热度 | 🔥 254⭐ | 内置 | 社区 | DIY |

---

## 核心价值

**YouTube Watcher 是YouTube字幕抓取的"最轻量解"：**
1. 仅依赖yt-dlp，无需Whisper/API密钥
2. 纯本地执行，字幕秒级提取
3. 254星验证，可靠性高
4. 输出纯文本，直接喂给LLM做总结
5. 配合`summarize`或`videos_understand`实现完整Pipeline

**推荐组合：**
```bash
# 最快方案：YouTube Watcher + summarize
youtube-watcher "URL" | summarize --stdin

# 最全方案：YouTube Watcher + Whisper转录 + videos_understand
youtube-watcher "URL" > subtitle.txt
ffmpeg -i video.mp4 audio.mp3
whisper audio.mp3 --model medium
videos_understand video.mp4 --prompt "详细总结"
```

---

## 安全评估（ClawHub官方）

- ✅ 仅使用yt-dlp获取字幕，行为与声明一致
- ✅ 无凭证/密钥要求
- ✅ 仅操作临时目录，不访问敏感文件
- ✅ MIT-0许可证，完全免费可再分发
- ⚠️ 字幕内容会发送到AI模型，注意隐私保护

---

## 参考链接

- ClawHub：https://clawhub.ai/skills/youtube-watcher
- 安装命令：`npx clawhub@latest install youtube-watcher`
- 作者：Michael Gathara（@michaelgathara）
- 许可证：MIT-0
- 安全扫描：VirusTotal Benign + OpenClaw Benign（高置信度）
