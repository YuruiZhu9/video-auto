# 通用工具 - AutoClip（AI智能视频剪辑与高光提取）

> 更新时间：2026-04-10
> 项目来源：https://github.com/zhouxiaoka/autoclip
> 官网：https://zhouxiaoka.github.io/autoclip_intro/

---

## 核心工具/API

| 工具 | 类型 | 说明 |
|------|------|------|
| **AutoClip** | 开源 AI 系统 | 自动从视频平台下载视频，AI 分析提取高光片段 |
| **Vue 3 前端** | Web UI | 现代化的浏览器界面，操作简单 |
| **FastAPI 后端** | Python API | 视频处理核心逻辑，支持批量任务 |
| **YouTube/B站 集成** | 数据源 | 自动抓取平台视频进行剪辑 |
| **LLM 高光判断** | AI 引擎 | 基于大模型判断哪些片段是"高光" |
| **FFmpeg** | 视频处理 | 实际剪辑、切片、拼接的后端工具 |

---

## 步骤流程

### 方案一：快速体验（Docker 一键部署）

```bash
# 1. 克隆项目
git clone https://github.com/zhouxiaoka/autoclip.git
cd autoclip

# 2. 一键启动（Docker）
docker-compose up -d

# 3. 打开浏览器访问
# http://localhost:3000
```

### 方案二：本地开发模式

```bash
# 1. 前端安装依赖
cd frontend
npm install
npm run dev

# 2. 后端安装依赖
cd backend
pip install -r requirements.txt

# 3. 配置环境变量
# 在 backend/.env 中设置：
# YOUTUBE_API_KEY=你的YouTube API密钥
# OPENAI_API_KEY=你的OpenAI API密钥（或智谱GLM等其他LLM）
# BILIBILI_COOKIE=你的B站 Cookie（用于获取高画质视频）

# 4. 启动后端
uvicorn main:app --reload

# 5. 启动前端（另一个终端）
cd frontend && npm run dev
```

### 第三步：使用 AutoClip 提取高光

**通过 Web UI 操作：**

```
1. 打开 http://localhost:3000
2. 输入视频 URL（YouTube / B站）
3. 设置参数：
   - 高光数量：5-10 个片段
   - 最短时长：30秒
   - 最长时长：5分钟
   - 关键词过滤：（可选）指定包含某些词才是高光
4. 点击"开始分析"
5. AI 自动分析并返回高光片段列表
6. 预览每个片段，确认后点击"导出"
7. 下载 MP4 片段或拼接后的完整视频
```

**通过 API 调用（开发者模式）：**

```bash
curl -X POST "http://localhost:8000/api/clip" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.bilibili.com/video/BV1xxx",
    "highlights": 5,
    "min_duration": 30,
    "max_duration": 300,
    "keywords": ["技巧", "方法", "教程"]
  }'
```

### 第四步：结合 OpenClaw 定时任务

AutoClip + OpenClaw 可以实现自动化视频高光监控：

```bash
# OpenClaw 定时任务脚本示例
# 监控指定 YouTube 频道，每有新视频自动提取高光

#!/bin/bash
# 1. 获取订阅频道最新视频
NEW_VIDEOS=$(youtube-dl --playlist-end 1 --flat-playlist "频道URL" 2>/dev/null)

# 2. 调用 AutoClip API 提取高光
for VIDEO_URL in $NEW_VIDEOS; do
  curl -s -X POST "http://localhost:8000/api/clip" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$VIDEO_URL\", \"highlights\": 3}" \
    >> /tmp/autoclip_results.json
done

# 3. 汇总结果发送到钉钉
echo "今日高光汇总：$(cat /tmp/autoclip_results.json)" | send_to_dingtalk
```

---

## 适用场景

- **自媒体创作者**：快速从长视频中提取精华片段，生成短视频素材
- **知识博主**：将讲座/课程视频剪辑成"3分钟精华版"发布到抖音/视频号
- **企业营销**：提取产品发布会、CEO 演讲中的关键金句片段
- **粉丝二次创作**：自动提取电竞/体育/综艺的精彩瞬间
- **个人学习**：把教程视频中高光知识点剪出来，做个人知识库

---

## 避坑指南

| 问题 | 解决方案 |
|------|----------|
| B站视频画质太低 | 登录 B站账号，设置 Cookie，提高画质 |
| YouTube 下载失败 | 配置代理（FFmpeg 代理设置）或使用 yt-dlp 配合 |
| AI 判断高光不准确 | 调整 `keywords` 参数，增加领域关键词引导 |
| 片段时长不稳定 | 设置 `min_duration` 和 `max_duration` 约束 |
| API 调用超时 | 视频太长时分段处理，或提高 API 超时设置 |
| Docker 内存不足 | 建议 4GB+ RAM，或在 docker-compose.yml 中限制并发数 |
| LLM API 费用高 | 替换为本地模型（Ollama + llama3）或使用智谱 AI 免费额度 |

---

## 核心原理

AutoClip 的高光提取依赖以下技术链路：

```
原始视频（YouTube/B站 URL）
    │
    ▼
【1】yt-dlp 下载/流式获取视频
    │
    ▼
【2】FFmpeg 音频提取 → Whisper ASR 语音识别
    │
    ▼
【3】字幕 + 音频 → LLM 分析
    Prompt: "请从以下字幕中找出5个最精彩的片段，给出时间戳和原因"
    │
    ▼
【4】FFmpeg 按时间戳剪辑 → 输出多个 MP4 高光片段
    │
    ▼
【5】可选：添加字幕、背景音乐、BGM
```

---

## 优缺点总结

**优点：**
- ✅ 开源免费，可本地部署，隐私安全
- ✅ 支持 YouTube + B站双平台
- ✅ Web UI 友好，非技术用户也能用
- ✅ 支持 API 批量处理
- ✅ Docker 一键部署，学习成本低

**缺点：**
- ❌ 需要配置多 API Key（YouTube/LLM/B站 Cookie）
- ❌ 高光判断依赖 LLM，长视频处理较慢
- ❌ 音频质量差时 Whisper 识别率下降
- ❌ 不支持本地视频直接导入（需先上传/下载）
- ❌ 没有预设的剪辑模板，需手动调整

---

## 参考链接

- GitHub 主仓库：https://github.com/zhouxiaoka/autoclip
- 在线演示：https://zhouxiaoka.github.io/autoclip_intro/
- 国内镜像（备用）：https://github.com/tqtcloud/autoclip
- 相关博客：https://blog.csdn.net/j8267643/article/details/151748400
- 博客园详细教程：https://www.cnblogs.com/chuanzhang053/p/19823084
