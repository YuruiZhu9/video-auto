#!/usr/bin/env python3
with open('/workspace/AI-music-score-featch/README.md', 'r') as f:
    content = f.read()

# Update the version and features section
old_status = '''## 🎯 当前状态（v0.3.0）

**已实现功能：**
- ✅ 上传 MP3 / WAV / FLAC / MP4 音频
- ✅ 粘贴 YouTube / B站 / 抖音 等视频链接（自动下载+提取音频）
- ✅ Guitar 和弦识别（BPM + 时间轴）
- ✅ **Bass 音符识别**（低频音高检测 + 根音推断）
- ✅ **Guitar + Bass 双轨 GTA 文本谱**（ASCII 六线谱）
- ✅ **Guitar + Bass 双轨 MIDI**（可直接导入 Guitar Pro / DAW）
- ✅ PDF 乐谱导出
- ✅ Web 前端（上传 / 进度条 / 结果展示 / 导出下载）
- ✅ Spotify Basic Pitch 吉他转谱模型（参考 Tabby 项目架构）
- ✅ LLM 智能纠错 pipeline 增强
- ✅ Guitar Pro 7 MusicXML 生成
- ✅ **Beat Analyzer（节拍分析器）**— beat strength + downbeat 检测 + 节拍稳定性评分
- ✅ **BPM 双重校验** — 智能修正 librosa 的 2x/0.5x 误检
- ✅ **拍号智能推断** — 支持 4/4, 3/4, 6/8, 2/4, 5/4, 7/8 自动检测
- ⚠️ GPU 模式（Demucs 音频分离 + CREPE 音高检测）需自行安装 torch
- 🔄 Guitar Pro .gp5 二进制文件（MusicXML 生成已支持，纯二进制 GP5 暂无可靠 Python 库）'''

new_status = '''## 🎯 当前状态（v0.4.0）

**已实现功能：**
- ✅ 上传 MP3 / WAV / FLAC / MP4 音频
- ✅ 粘贴 YouTube / B站 / 抖音 等视频链接（自动下载+提取音频）
- ✅ Guitar 和弦识别（BPM + 时间轴）
- ✅ **Bass 音符识别**（低频音高检测 + 根音推断）
- ✅ **Guitar + Bass 双轨 GTA 文本谱**（ASCII 六线谱）
- ✅ **Guitar + Bass 双轨 MIDI**（可直接导入 Guitar Pro / DAW）
- ✅ PDF 乐谱导出
- ✅ Web 前端（上传 / 进度条 / 结果展示 / 导出下载）
- ✅ Spotify Basic Pitch 吉他转谱模型（参考 Tabby 项目架构）
- ✅ LLM 智能纠错 pipeline 增强
- ✅ Guitar Pro 7 MusicXML 生成
- ✅ **Beat Analyzer（节拍分析器）**— beat strength + downbeat 检测 + 节拍稳定性评分
- ✅ **BPM 双重校验** — 智能修正 librosa 的 2x/0.5x 误检
- ✅ **拍号智能推断** — 支持 4/4, 3/4, 6/8, 2/4, 5/4, 7/8 自动检测
- ✅ **长音频分段处理** — 超过90秒音频自动分段（5秒 overlap），合并结果
- ✅ **吉他指法图增强** — 60+ 和弦库（含爵士/变化和弦），SVG 渐变美化
- ✅ **Freemium 商业模式** — 免费试用3次，Pro 会员解锁无限扒谱
- ✅ **分享功能** — 一键复制结果链接
- ⚠️ GPU 模式（Demucs 音频分离 + CREPE 音高检测）需自行安装 torch
- 🔄 Guitar Pro .gp5 二进制文件（MusicXML 生成已支持，纯二进制 GP5 暂无可靠 Python 库）'''

content = content.replace(old_status, new_status)

# Add a screenshot description section
old_route_map = '''| GET | `/api/download/{task_id}/gta` | 下载 GTA 文本谱 |'''

new_route_map = '''| GET | `/api/download/{task_id}/gta` | 下载 GTA 文本谱 |

---

## 📸 功能截图说明

**Home 页 Freemium Banner**
- 顶部显示剩余免费试用次数（默认 3 次）
- 点击「升级 Pro」弹出订阅说明弹窗
- localStorage 持久化试用次数，重启不丢失

**Result 页吉他指法图**
- 鼠标悬停任意和弦块，自动弹出该和弦的吉他指法 SVG 图
- 支持 60+ 和弦（含爵士变化和弦：Gm7, Bmaj7, Dmaj7 等）
- 指法圆点带手指编号①②③④，横按和弦高亮弧线

**分享功能**
- 结果页顶部导航栏新增「分享」按钮
- 点击自动复制当前 URL 到剪贴板，2.5秒内显示"已复制"状态
'''

content = content.replace(old_route_map, new_route_map)

# Update roadmap
old_roadmap = '''| v0.4.0 | Guitar Pro .gp5 文件生成 |
| v1.0.0 | GPU 优化 + 完整 pipeline |'''

new_roadmap = '''| v0.4.0 | Freemium + 长音频分段处理 + 指法图增强 |
| v0.5.0 | Guitar Pro .gp5 文件生成 |
| v1.0.0 | GPU 优化 + 完整 pipeline |'''

content = content.replace(old_roadmap, new_roadmap)

# Add changelog section
changelog = '''

---

## 📋 更新日志（v0.4.0）

### ✨ 新功能

- **长音频分段处理**：音频超过 90 秒自动分段处理（每段 90 秒，5 秒 overlap 避免边界遗漏），最终合并所有片段的和弦/Bass 结果
- **吉他指法图增强**：和弦库从 24 种扩展至 60+ 种，新增 B7, Bdim, Bmaj7, Dmaj7, Gm7, Gmaj7, Cm7, F7 等爵士/变化和弦；SVG 指法图增加渐变圆点、横按弧线高亮、琴头木纹装饰
- **Freemium 模式**：前端新增「免费试用 3 次」Banner，localStorage 计数；次数用完后弹出 Pro 订阅说明弹窗（¥9.9/月）
- **分享功能**：结果页顶部导航栏新增「分享」按钮，点击一键复制链接并显示「已复制 ✓」反馈

### 🐛 Bug 修复

- 修复 Result 页面音频播放可能失败的问题

### 📝 文档

- 更新 README.md，新增功能截图说明、更新日志章节
'''

content = content.replace('\n*Built with FastAPI', changelog + '\n*Built with FastAPI')

with open('/workspace/AI-music-score-featch/README.md', 'w') as f:
    f.write(content)

print("README.md updated successfully")
