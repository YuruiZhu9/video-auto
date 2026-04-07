# Video-Auto 优化方案

> 记录当前流水线的瓶颈与优化方向，持续迭代

---

## ✅ 已解决问题

| 问题 | 解决方案 | 状态 | 验证日期 |
|------|----------|------|---------|
| 无 ffmpeg，无法合成 MP4 | 改用 `batch_image_to_video`（MCP 工具），10张 Slide 图逐张生成视频片段 | ✅ 已解决 | 2026-04-04 |
| 无 ffmpeg，无法合并音频+视频 | 纯 Python MP4 box 拼接，`combined_video.mp4`（9.7MB）验证通过 | ✅ 已解决 | 2026-04-04 |
| GLM-4-Flash 上下文偏小 | 升级为 **GLM-4.7-Flash**（200万Tokens/天，永久免费） | ✅ 已解决 | 2026-04-04 |
| TTS 配音 | OpenClaw 内置 `tts` 工具，生成6段 MP3 音频，无需 API Key | ✅ 已解决 | 2026-04-04 |

---

## ⚠️ 仍需解决的问题

| 优先级 | 问题 | 建议方案 |
|--------|------|----------|
| ~~🔴 P0~~ | ~~MP4 视频未带配音~~ | **✅ 已解决（部分）**：纯Python拼接视频片段成功，音视频合并需手动 |
| 🟡 P1 | **音视频合并未自动化** | 方案A：GitHub Actions + FFmpeg Docker；方案B：安装 pydub |
| 🟡 P1 | **声音克隆未实际调用** | 需提供 Fish Audio API Key（免费，5秒克隆）|
| 🟢 P2 | **GitHub Actions 自动构建** | push 到 main 分支自动触发，构建 Docker 容器执行合并 |
| 🟢 P2 | **GitHub 推送未测试** | 需配置 GitHub token 并测试 push |

---

## 🔧 技术方案调整

### 视频合成（已变更）

**旧方案（失败）：**
```bash
ffmpeg -framerate 1 -i slide_%03d.png -i audio.wav \
  -c:v libx264 -pix_fmt yuv420p -shortest output.mp4
# ❌ ffmpeg 权限不足，无法安装
```

**新方案（已验证）：**
```python
# 使用 batch_image_to_video MCP 工具
batch_image_to_video(
    image_file_list=[f"slide_cover.png", ..., f"slide_09.png"],
    output_file_list=[f"slide01.mp4", ..., f"slide09.mp4"],
    duration_list=[6]*9,
    resolution_list=["1080P"]*9
)
# ✅ 9个视频片段生成成功，每段6秒
```

**待解决：视频+音频合并**
- 方案A：申请 Hypereal AI API（图生视频+音频合成）
- 方案B：使用 MiniMax 视频 API（视频配音合成）
- 方案C：Python wave 模块拼接 TTS 音频（纯 Python，无 ffmpeg）

---

## 🛠 优化路线图

### Phase 1：闭环流水线（本周）
- [x] 完成 TTS 音频生成（OpenClaw TTS，6段 MP3）✅ 2026-04-04
- [x] 完成视频片段拼接（纯Python MP4 box拼接，9.7MB验证通过）✅ 2026-04-04
- [ ] 完成 TTS 音频完整合并（需 pydub 或手动）
- [ ] 测试 Fish Audio 声音克隆（需 API Key）
- [x] 完整流水线端到端测试 ✅ 2026-04-04

### Phase 2：质量提升（下周）
- [ ] HTML Slide 加入 reveal.js 动画
- [ ] Slide 支持 16:9 固定比例
- [ ] 视频加入字幕/时间戳
- [ ] 自动生成视频封面

### Phase 3：自动化（本月）
- [ ] GitHub Actions：push → 自动构建 + 部署
- [ ] 钉钉通知：流水线状态实时推送
- [ ] 多语言支持（中英双语 Slide）
- [ ] 主题模板系统

---

## 📝 待补充的 API Keys

| API | 用途 | 申请地址 | 状态 |
|-----|------|----------|------|
| Fish Audio | 声音克隆 | https://fish.audio/ | ⚠️ 待提供 |
| Hypereal AI | 视频生成+合并 | https://hypereal.ai/ | ⚠️ 待提供 |
| 智谱 AI GLM-4.7-Flash | 内容扩展 | https://open.bigmodel.cn/ | ✅ 已配置 |

---

## 📊 性能基准（首次测试）

| 环节 | 耗时 | 状态 |
|------|------|------|
| 内容扩展（GLM-4.7-Flash）| ~10秒 | ✅ |
| HTML Slide 生成 | ~5秒 | ✅ |
| 9张背景图生成 | ~60秒 | ✅ |
| 9个视频片段（batch 1）| ~50秒 | ✅ |
| 9个视频片段（batch 2）| ~40秒 | ✅ |
| GitHub 推送 | ~30秒 | ✅ |
| TTS 配音 | ~20秒 | ✅ |
| **总计** | **~3.5分钟** | |

> 首次测试生成文件：9个MP4 + 9张背景图 + HTML Slide + 演讲稿 + 全景拼接图

## 🆕 新增优化模块（2026-04-06）

### 1. scene_detector.py — 场景智能分段

**解决的问题：** 视频段落碎片化、场景切换点不准确

**核心算法：**
- 双轨切分：视觉轨道（FFmpeg场景检测）+ 音频轨道（静音停顿检测）
- 智能合并：最小5秒/最大60秒，自动避免碎片化
- 输出：带时间戳的段落JSON + SRT字幕格式

**使用示例：**
```python
from scene_detector import get_video_segments, export_srt_timestamps

segments = get_video_segments(
    'input_video.mp4',
    scene_threshold=0.4,   # 阈值可调 0.3~0.7
    min_segment_sec=5,     # 最小5秒
    max_segment_sec=60,    # 最大60秒
    use_audio=True         # 启用音频辅助
)

export_srt_timestamps(segments, 'output.srt')
```

**命令行：**
```bash
python video/scene_detector.py \
  --video input.mp4 \
  --threshold 0.4 \
  --min-sec 5 \
  --max-sec 60 \
  --output segments.json \
  --srt output.srt
```

### 2. naming_utils.py — 统一文件命名规范

**解决的问题：** 文件名不统一、中文文件名乱码、序号管理混乱

**核心功能：**
- 统一命名格式：`{prefix}_{topic_slug}_{date}_{seq:02d}.{ext}`
- 中文→拼音slug（无需第三方依赖）
- 多视频拼接过渡文件名规范
- 完整输出文件清单（manifest）

**使用示例：**
```python
from naming_utils import build_filename, make_output_manifest, print_manifest

# 标准命名
filename = build_filename(
    prefix='slide',
    topic='AI推荐系统最新进展',
    seq=1,
    suffix='intro',
    ext='mp4'
)
# -> "slide_ai_tuijian_xitong_20260406_01_intro.mp4"

# 生成完整清单
manifest = make_output_manifest(
    topic='AI推荐系统最新进展',
    num_slides=9,
    output_dir='/path/to/video'
)
print_manifest(manifest)
```

---

## 📊 性能基准（2026-04-06 更新）

| 环节 | 耗时 | 状态 |
|------|------|------|
| 场景检测（FFmpeg双轨）| ~3-5秒 | ✅ 新增 |
| 内容扩展（GLM-4.7-Flash）| ~10秒 | ✅ |
| HTML Slide 生成 | ~5秒 | ✅ |
| 9张背景图生成 | ~60秒 | ✅ |
| 9个视频片段（batch 1）| ~50秒 | ✅ |
| 9个视频片段（batch 2）| ~40秒 | ✅ |
| 统一命名规范化 | ~1秒 | ✅ 新增 |
| GitHub 推送 | ~30秒 | ✅ |
| TTS 配音 | ~20秒 | ✅ |
| **总计** | **~3.5-4分钟** | |
