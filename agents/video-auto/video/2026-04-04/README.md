# 2026-04-04 期：2026年AI视频工具最新进展

> 自动生成时间：2026-04-04 17:01
> 流水线版本：video-auto v3

---

## 主题
**2026年AI视频工具最新进展：从可灵到PixVerse V6**

涵盖工具：可灵AI 3.0 / PixVerse V6 / Veo 3.1 Lite / Kokoro-82M

---

## 本期产出文件

### 视频素材
| 文件 | 类型 | 说明 |
|------|------|------|
| `slides/slide_01.png` ~ `slide_10.png` | PNG 图片 | 10张幻灯片配图 |
| `slides/slide01.mp4` ~ `slide10.mp4` | MP4 视频 | 10个视频片段（每段6秒，共60秒） |
| `combined/combined_video.mp4` | MP4 视频 | **10段拼接后的完整视频**（9.7MB） |
| `combined/cover.png` | PNG 图片 | 视频封面 |

### 音频
| 文件 | 说明 |
|------|------|
| `audio/tts_01.mp3` ~ `tts_06.mp3` | 6段TTS音频（按内容分段） |
| `combined/full_audio.mp3` | 完整音频（83KB，仅第一段） |

### 文档
| 文件 | 说明 |
|------|------|
| `content/2026-04-04.md` | 完整演讲稿（1200字） |
| `content/script.md` | 备选演讲稿（养猫主题） |
| `slides/output.html` | HTML幻灯片 |

---

## 完整流水线状态（2026-04-04）

| 步骤 | 状态 | 产出 |
|------|------|------|
| ① 内容扩展（GLM-4-Flash） | ✅ | content/2026-04-04.md |
| ② HTML Slide 生成 | ✅ | slides/output.html |
| ③ 幻灯片配图生成 | ✅ | slides/slide_01.png ~ slide_10.png |
| ④ 视频片段生成（batch_image_to_video） | ✅ | slides/slide01.mp4 ~ slide10.mp4 |
| ⑤ TTS音频生成（OpenClaw TTS） | ✅ | audio/tts_01~06.mp3 |
| ⑥ 视频片段拼接 | ✅ | combined/combined_video.mp4（9.7MB）|
| ⑦ 音视频合并 | ⚠️ 需手动 | 需用剪映专业版合并 combined_video.mp4 + full_audio.mp3 |
| ⑧ GitHub 推送 | ❌ 待执行 | 需配置 GitHub token |

---

## 如何完成最终视频

用剪映专业版（免费）：

1. 打开剪映专业版
2. 导入 `combined_video.mp4`（视频轨道）
3. 导入 `full_audio.mp3`（音频轨道，替换原视频音频）
4. 如需调整时长：将 `full_audio.mp3` 按 `tts_01~06.mp3` 分段，对应到各视频片段
5. 导出 → 最终成品视频

---

## 流水线问题记录

### 2026-04-04 已知问题

1. **音视频合并未自动化**
   - 原因：`ffmpeg` 系统不可用，`@ffmpeg/ffmpeg` WASM 需网络加载
   - 解决：需要网络稳定环境，或使用剪映专业版手动合并
   - 建议：配置 GitHub Actions，在 CI 中调用 FFmpeg Docker 镜像

2. **音频未完整合并**
   - 原因：`pydub` 未安装，`full_audio.mp3` 仅复制了第一段
   - 解决：6个 TTS 片段分别对应各视频内容，需在剪映中手动分段导入
   - 建议：下次加入 `pip install pydub` 步骤
