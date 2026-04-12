# YouTube Factory — ClawHub AI视频生成工具

> 🤖 分类：视频制作/AI生成
> 📅 更新日期：2026-04-12
> 📌 来源：ClawHub（`clawhub.ai/skills/youtube-factory`）
> ⭐ 热度：27星 | 📥 4.2k安装
> 🔧 版本：v1.3.0

---

## 核心工具/API

| 工具 | 功能描述 | 角色 |
|------|---------|------|
| **FFmpeg** | 视频合成、音频混合、格式转换 | 视频制作 |
| **edge-tts** | Microsoft TTS，AI语音合成 | 配音生成 |
| **Pexels API** | 免费库存视频素材库 | B-Roll获取 |
| **Python PIL** | 缩略图生成 | 封面制作 |

---

## 完整Pipeline

```
提示词 → 脚本生成 → TTS配音 → Pexels素材 → FFmpeg合成 → 成片
```

---

## 步骤流程

### 5步生成完整YouTube视频

**1. 安装依赖**
```bash
brew install ffmpeg
pip install edge-tts requests pillow python-dotenv
```

**2. 配置API密钥**
```bash
export PEXELS_API_KEY="your_pexels_key"
mkdir -p ~/.openclaw-video-skills
echo 'PEXELS_API_KEY=your_pexels_key' > ~/.openclaw-video-skills/config.env
```

**3. 安装Skill**
```bash
npx clawhub@latest install youtube-factory
```

**4. 生成视频（提示词驱动）**
```bash
youtube-factory "A tutorial on how to use OpenClaw skills"
```

**5. 自定义配置**
```bash
# 指定输出目录
export OUTPUT_DIR="/path/to/output"

# 指定配音音色
export DEFAULT_VOICE="zh-CN-XiaoxiaoNeural"
```

---

## 输出产物

| 产物 | 路径 | 说明 |
|------|------|------|
| 视频文件 | `~/Videos/OpenClaw/` | MP4格式最终成片 |
| 字幕文件 | 同目录，.srt格式 | 同步字幕 |
| 缩略图 | 同目录，.png格式 | 视频封面 |

---

## 适用场景

- **AI自动化频道内容**：输入提示词自动生成教程视频
- **产品演示自动化**：API文档→演示视频
- **社交媒体内容**：批量生成短视频
- **快速MVP验证**：验证视频内容创意
- **教育内容批量生产**：知识点→动画讲解视频

---

## 避坑指南

### 问题1：Pexels素材获取失败
- **问题**：B-Roll视频下载失败
- **原因**：Pexels CDN域名不在白名单
- **解决**：
  ```python
  # 修改脚本，扩展白名单
  allowed_domains = ['pexels.com', 'video.pexels.com', '*.pexels.com', '*.pexels-cdn.com']
  ```

### 问题2：edge-tts网络问题
- **问题**：TTS合成超时
- **原因**：Microsoft服务器连接不稳定
- **解决**：
  ```bash
  # 使用离线TTS备选方案
  pip install pyttsx3  # 备选离线方案
  ```

### 问题3：FFmpeg依赖问题
- **问题**：ffmpeg未安装或路径不对
- **解决**：
  ```bash
  brew install ffmpeg
  # 确认路径
  which ffmpeg
  ```

### 问题4：视频文件过大
- **问题**：生成视频占用空间过大
- **解决**：
  ```bash
  # 压缩输出
  ffmpeg -i input.mp4 -vcodec libx264 -crf 23 output.mp4
  ```

---

## 局限性

1. **不是真正的AI视频生成**：仅是素材拼接，非Sora/Gen-3级别AI生成
2. **Pexels素材版权**：需遵守Pexels使用条款
3. **配音为Microsoft TTS**：非最自然的语音，但免费
4. **B-Roll依赖网络**：需要稳定的Pexels API连接
5. **SKILL.md声明不准确**：声称"self-contained, no external modules"但实际需要安装Python包

---

## 安全评估

- ✅ 仅需Pexels API密钥（无其他敏感信息）
- ✅ 代码验证域名白名单
- ⚠️ 调用Microsoft TTS服务器（edge-tts），文本会上传至微软
- ⚠️ 建议先在隔离环境测试

---

## 核心价值

**YouTube Factory 是视频内容创作的"AI加速器"：**
1. 提示词→完整视频，5分钟出片
2. 100%免费（FFmpeg+edge-tts+Pexels均免费）
3. 无需视频制作技能，会写提示词即可
4. 可批量生成，建立内容流水线
5. 与视频解析知识库互补（解析已有视频 vs 生成新视频）

**与知识库关系：**
- ✅ 视频解析（已有视频→文字/知识）
- ✅ 视频生成（文字/提示词→视频）
- 形成完整的内容生产闭环

---

## 参考链接

- ClawHub：https://clawhub.ai/skills/youtube-factory
- 安装命令：`npx clawhub@latest install youtube-factory`
- 作者：mayank8290
- 许可证：MIT-0
- 安全扫描：VirusTotal Benign + OpenClaw Benign（中置信度）
- Pexels官网：https://www.pexels.com/api/
