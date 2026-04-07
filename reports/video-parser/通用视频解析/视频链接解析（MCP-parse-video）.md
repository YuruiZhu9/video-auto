# 通用视频解析 - 视频链接解析（MCP parse-video）

## 核心工具/API

| 工具 | 类型 | 说明 |
|------|------|------|
| **MCP parse-video** | MCP 工具 | 通过 MCP（Model Context Protocol）接口解析多平台视频分享链接 |
| **yt-dlp** | CLI 工具 | 底层视频下载，支持 YouTube/B站等1000+ 平台 |
| **FFmpeg** | CLI 工具 | 音视频格式转换、音频提取、截图 |

---

## 步骤流程

### 第一步：调用 MCP 工具解析链接

```json
{
  "url": "视频分享链接（支持含分享文案的文本，自动提取链接）"
}
```

支持的输入格式：
- 纯视频链接：`https://v.douyin.com/xxx`
- 带文案的文本：`推荐这个视频 https://www.bilibili.com/xxx 太棒了！`

### 第二步：解析返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 是否解析成功 |
| `title` | string | 视频标题 |
| `thumbnail` | string | 封面缩略图URL |
| `video_url` | string | 无水印视频下载链接 |
| `video_urls` | array | 所有可用视频链接列表 |
| `audio_url` | string | 音频下载链接 |
| `image_urls` | array | 图集全部图片链接 |
| `parse_time` | string | 解析耗时 |

### 第三步：下载到本地

```bash
# 安装下载脚本（项目自带）
# 下载视频
python download.py --video "https://xxx.mp4"

# 下载视频+音频（部分平台音视频分离）
python download.py --video "https://xxx/v.mp4" --audio "https://xxx/a.mp3"

# 下载图集（小红书等）
python download.py --image "url1" --image "url2" --image "url3"

# 指定输出目录和文件名
python download.py --video "url" -o ~/Downloads -n "搞笑视频"
```

---

## 支持平台

| 平台 | 状态 | 说明 |
|------|------|------|
| 抖音 / Douyin | ✅ 完整支持 | 无水印视频+音频 |
| 快手 / Kuaishou | ✅ 完整支持 | 无水印视频 |
| 小红书 / Xiaohongshu | ✅ 完整支持 | 视频+图集 |
| 哔哩哔哩 / Bilibili | ✅ 完整支持 | 视频+音频 |
| 微博 / Weibo | ✅ 完整支持 | 视频 |
| TikTok | ✅ 完整支持 | 无水印视频 |
| Instagram | ✅ 完整支持 | 视频+图片 |
| YouTube | ✅ 完整支持 | 视频+音频 |
| 其他主流平台 | ✅ 支持 | 持续更新中 |

---

## 适用场景

- ✅ **视频素材采集**：快速获取无水印原版视频用于二次创作
- ✅ **图集内容获取**：小红书图集、微博相册批量下载
- ✅ **音频提取**：从视频中提取音频用于播客或语音转文字
- ✅ **竞品监控**：批量采集竞品短视频内容
- ❌ **私密/私密内容**：无法解析私密账号或已下架内容

---

## 避坑指南

### ⚠️ 解析失败常见原因

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 解析返回 null | 链接已过期或私密 | 更换为公开可访问链接 |
| 视频有水印 | 部分平台需登录 | 使用解析出的高清无水印链接，或用 yt-dlp 指定格式 |
| audio_url 为空 | 平台不支持音频分离 | 使用 FFmpeg 从视频提取音频：`ffmpeg -i video.mp4 -vn audio.mp3` |
| 下载速度慢 | 网络或CDN限制 | 使用代理或选择其他镜像链接（video_urls 列表中可能有多个） |

### 💡 进阶技巧

```bash
# FFmpeg 提取音频（当 audio_url 不可用时）
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3

# FFmpeg 提取指定时间段
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:00 -c copy clip.mp4

# 批量下载（图集场景）
for url in "${image_urls[@]}"; do
  curl -sL "$url" -o "img_$i.jpg"
  ((i++))
done
```

---

## 安装来源

- **GitHub**：https://github.com/openclaw/skills/tree/main/skills/hexiaochun/parse-video
- **ClawHub/LobeHub**：搜索 `parse-video`
- **安装命令**：`npx clawhub@latest install parse-video`（通过 clawhub 安装）

---

## 参考链接

- ClawHub Skill 页面：https://lobehub.com/zh/skills/openclaw-skills-parse-video
- yt-dlp 官方：https://github.com/yt-dlp/yt-dlp
- FFmpeg 官网：https://ffmpeg.org/
