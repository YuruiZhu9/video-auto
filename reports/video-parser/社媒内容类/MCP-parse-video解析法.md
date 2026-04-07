# 社媒内容类 - MCP parse_video解析法

## 核心工具/API

| 工具 | 功能描述 |
|------|---------|
| **MCP parse_video** | 解析抖音/快手/小红书/B站等链接，获取无水印视频 |
| **videos_understand** | 理解短视频内容，提取主题/文案/卖点 |
| **download.py 脚本** | 批量下载解析出的视频/音频/图集 |
| **FFmpeg** | 视频压缩/格式转换/混音 |

## 步骤流程

### 社媒视频解析工作流（MCP方案）

分享链接（带文案或不带）
  └→ MCP parse_video ─→ 结构化资源（video_url/audio_url/images）
    ├→ 直接使用URL（流媒体播放）
    └→ download.py ─→ 本地文件
      └→ videos_understand ─→ 内容理解报告

### Step 1：MCP解析视频链接

支持平台：抖音/TikTok、快手、小红书、B站、微博、Instagram、YouTube

调用方式（MCP工具）：
输入参数：
{"url": "抖音分享文案（包含链接）"}

返回字段：
{"success": true/false, "title": "标题", "thumbnail": "封面URL",
 "video_url": "首选视频URL", "video_urls": ["所有URL"],
 "audio_url": "音频URL", "image_urls": ["图集图片"],
 "parse_time": "解析时间"}

### Step 2：下载资源

bash
# 单个视频
python download.py --video "https://xxx.mp4" --name "作品名"
# 图集下载（小红书）
python download.py --image "url1" --image "url2" --image "url3" --name "图集"
# 指定输出目录
python download.py --video "URL" -o ~/workspace/downloads -n "作品"

### Step 3：内容理解（videos_understand）

分析prompt模板：
分析这个短视频/社交媒体内容：
- 内容类型（带货/种草/娱乐/知识/情感）
- 目标受众
- 主线故事/情节
- 关键台词/文案
- 视觉亮点（配图/剪辑风格/BGM）
- CTA（行动号召）分析
- 带货转化潜力评估
- 爆款元素分析

## 适用场景

- 抖音/快手带货视频素材采集
- 小红书种草笔记/图集保存
- B站up主内容存档
- 竞品视频内容分析
- 无水印素材用于二次创作

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 解析失败 | 平台接口更新 | 提供更完整的分享链接（含文案） |
| 私密/已下架内容 | 权限问题 | MCP无法处理，提示用户内容不可访问 |
| 下载视频文件过大 | 原画质太高 | 下载后用ffmpeg压缩：ffmpeg -i v.mp4 -crf 28 small.mp4 |
| 小红书图集图片数很多 | 批量下载 | 一次传入所有URL，脚本循环处理 |
| 解析速度慢 | 平台限速 | 并行处理多个链接 |

## Skill信息

- 名称：视频链接解析（parse-video）
- 来源：openclaw/skills @ GitHub
- 版本：1.0.2 | 下载量：102.6k
- 是否免费：完全免费，无需认证

## 参考链接

- ClawHub Skill：https://lobehub.com/zh/skills/openclaw-skills-parse-video
- GitHub源码：https://github.com/openclaw/skills/tree/main/skills/hexiaochun/parse-video
