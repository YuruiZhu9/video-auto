# 附录 — 常见问题 FAQ

## Q1：视频文件太大（超过 20MB）无法用 Gemini API 处理怎么办？

**方案：**
1. FFmpeg 压缩后上传：
   ```bash
   ffmpeg -i input.mp4 -vf "scale=1280:-2" -crf 28 output.mp4
   ```
2. 分割为多个小片段：
   ```bash
   ffmpeg -i input.mp4 -c copy -f segment -segment_time 300 part_%03d.mp4
   ```
3. 使用 Cloud Storage URL 代替 base64（无大小限制）

---

## Q2：Whisper 转写中文准确率低怎么办？

**方案：**
1. 使用更大的模型（`medium` / `large` 效果明显更好）
2. 使用 `faster-whisper` + `medium` 精度更高
3. 提前分离人声（去除背景音乐）：
   ```bash
   pip install spleeter
   spleeter separate -i audio.wav -o output/
   ```
4. 调整采样率为 16kHz（WAV格式）：
   ```bash
   ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
   ```

---

## Q3：B站 / 国内平台视频无法直接用 summarize 处理？

**方案：**
```bash
# 1. yt-dlp 下载（需要登录 Cookie）
yt-dlp --cookies-from-browser chrome -o "%(title)s.%(ext)s" "https://www.bilibili.com/video/BVxxx"

# 2. summarize 处理本地文件
summarize "视频文件.mp4" --length medium

# 3. 如果下载也被限制 → 用 browser 工具访问B站后截图，再用 images_understand 分析
```

---

## Q4：长视频（超过 1 小时）怎么处理效率最高？

**推荐流水线：**
```
1. ffmpeg 按时间均匀分段（每10分钟一段）
2. 并行调用 videos_understand 处理各段
3. 合并各段输出 + LLM 二次总结
```

具体命令：
```bash
# 切分为每段 10 分钟
ffmpeg -i long_video.mp4 -c copy -f segment -segment_time 600 part_%03d.mp4
```

---

## Q5：技术教程视频需要提取代码片段，最佳方案是什么？

**推荐方案：Whisper + 正则提取**
1. `faster-whisper` 转写（保留时间戳）
2. 正则匹配命令行/代码片段：
   ```python
   import re
   pattern = r'(git\s+\w+|pip\s+install|npm\s+\w+|python\s+\S+|docker\s+\w+|curl\s+\S+)'
   commands = re.findall(pattern, transcript, re.IGNORECASE)
   ```
3. 配合 ffmpeg 提取代码帧（关键时间点）：
   ```bash
   ffmpeg -ss 00:05:30 -i demo.mp4 -frames:v 1 -c:v png code_frame.png
   ```

---

## Q6：视频只有画面没有语音（如纯操作演示），Whisper 无效怎么办？

**方案：**
1. `videos_understand` → 直接多模态理解
2. `ffmpeg` 提取关键帧 → `images_understand` 逐帧 OCR + 分析
3. 结合使用：先 `images_understand` 提取帧内文字，再 `videos_understand` 整体理解

---

## Q7：summarize YouTube 提取失败（无字幕/隐私视频）？

**方案：**
1. 检查是否为无字幕视频 → 改用 `videos_understand` 直接分析
2. 使用 Apify 备选通道：
   ```bash
   export APIFY_API_TOKEN=your_token
   summarize "URL" --youtube auto --extract-only
   ```
3. yt-dlp 下载后本地处理

---

## Q8：视频解析结果如何存储管理？

**推荐知识库结构：**
```
/workspace/reports/video-parser/
├── README.md
├── 技术教程类/
│   ├── OpenClaw-Skill解析.md
│   └── Gemini-API解析.md
├── 行业分享类/
│   └── summarize-cli解析.md
├── 开源项目演示类/
│   └── FFmpeg-Whisper方案.md
├── 索引/
│   └── （定期汇总所有解析结果）
└── raw/
    └── （原始转写文本、字幕文件存放）
```

**命名规范**：
```
{日期}_{视频标题}_{解析类型}.md
例：2026-04-11_OpenClaw教程_videos_understand解析.md
```
