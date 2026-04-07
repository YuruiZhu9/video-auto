# 技术教程类 - Summarize Skill 解析

## 核心工具/API

- **@steipete/summarize**：OpenClaw 官方 Skill，封装了多类型内容（网页/视频/音频/PDF/图片）的 AI 总结能力
- **支持的 LLM 提供商**：OpenAI（GPT-4o）、Anthropic（Claude）、xAI（Grok）、Google Gemini
- **支持的平台**：YouTube、网页、PDF、图片、音频文件
- **特色功能**：幻灯片提取（从视频中提取 PPT 画面）、OCR 识别

---

## 步骤流程

### 安装与配置

```bash
# 方法1：npm 全局安装（推荐，跨平台）
npm i -g @steipete/summarize

# 方法2：Homebrew（仅 macOS/Linux）
brew install steipete/tap/summarize

# 配置 API Key
export OPENAI_API_KEY="sk-xxxx"
export ANTHROPIC_API_KEY="sk-ant-xxxx"
# 或写入配置文件 ~/.summarize/config.json
```

### 使用流程

1. **YouTube 视频总结**
   ```bash
   summarize "https://www.youtube.com/watch?v=视频ID" \
     --provider anthropic \
     --model claude-sonnet-4-20250514
   ```

2. **本地视频总结**
   ```bash
   summarize "/workspace/video.mp4" \
     --provider openai \
     --format markdown
   ```

3. **提取幻灯片/关键帧**
   ```bash
   summarize "/workspace/tutorial.mp4" \
     --slides \
     --provider anthropic
   ```

4. **批量总结（脚本）**
   ```bash
   # 遍历目录下所有 mp4 文件
   for f in *.mp4; do
     summarize "$f" --provider anthropic --output "${f%.mp4}.md"
   done
   ```

---

## 适用场景

- **快速概览**：想知道一个 YouTube 技术视频讲了什么，不需要完整分析
- **多模态内容**：视频中含 PPT/幻灯片，需提取并总结
- **多语言内容**：支持 100+ 语言，适合国外技术分享视频
- **API 统一接口**：不想自己组合 yt-dlp + Whisper + LLM，直接一条命令搞定
- **PDF + 视频组合**：教程同时有视频和配套 PDF，一起总结

---

## 避坑指南

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 安装失败（arm64 报错） | Homebrew 安装方式有架构限制 | 改用 `npm i -g @steipete/summarize` |
| 总结质量差 | 默认模型太弱 | 明确指定 `--provider anthropic --model claude-sonnet-4` |
| 视频太长超时 | 默认超时时间有限 | 先用 FFmpeg 截取前 30 分钟，或分段处理 |
| 提取幻灯片失败 | 视频帧率太低或无明显 PPT | 用 `ffmpeg -i video.mp4 -vf "select='eq(pict_type\,I)'" -vsync vfr frames/%03d.png` 手动提取关键帧 |
| API Key 不生效 | 环境变量未正确加载 | 检查 `~/.summarize/config.json` 配置或显式传入 |
| 需要网络代理 | 访问 YouTube/某些网站 | 配置代理：`export HTTPS_PROXY=http://127.0.0.1:7890` |

---

## 与 videos_understand 的对比

| 维度 | @steipete/summarize | videos_understand |
|------|---------------------|-------------------|
| **数据处理** | 上传到 LLM 服务商 | 在 OpenClaw 平台内处理 |
| **YouTube 支持** | ✅ 直接传 URL | ❌ 需先下载 |
| **幻灯片提取** | ✅ | ❌ |
| **本地文件** | ✅ | ✅ |
| **离线运行** | ❌（需 API Key） | 部分功能可离线 |
| **速度** | 较快（云端处理） | 取决于模型 |
| **隐私** | 数据上传外部 | 平台内处理 |
| **费用** | 消耗 API 配额 | 消耗平台配额 |

---

## 参考链接

- Skill 主页：https://clawhub.ai/kn70pywhg0fyz996kpa8xj89s57yhv26/summarize
- GitHub：搜索 `@steipete/summarize`
