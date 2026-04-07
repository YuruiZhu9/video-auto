# AI 扒谱项目进展记录

## 2026-04-06 下午 v0.4.0 优化批次

### 改动概述

本次在 `main` 分支完成 commit `1bed8f1`，包含 5 个文件的改动，共 +331/-10 行：

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `README.md` | 文档更新 | 版本升至 v0.4.0，新增功能列表、截图说明、更新日志 |
| `backend/core/pipeline.py` | 功能增强 | 新增长音频分段处理（`_chunk_audio` / `_merge_chords` / `_merge_bass`） |
| `frontend/src/components/ChordViewer.tsx` | UI 增强 | 和弦库从 24 种扩至 60+，SVG 渐变美化，横按高亮 |
| `frontend/src/pages/Home.tsx` | 商业模式 | Freemium Banner + 订阅弹窗 + localStorage 试用计数 |
| `frontend/src/pages/Result.tsx` | 功能增强 | 分享按钮（复制链接 + 已复制反馈） |

### 具体改进

#### 1. Freemium 商业模式（Home.tsx）
- 新增顶部 Banner：显示剩余免费试用次数（默认 3 次）
- 次数用完后弹出 Pro 订阅说明弹窗（¥9.9/月，包含功能列表）
- `localStorage` 持久化（key: `ai-guitar-tab-trials`）
- 每次上传/URL 分析前检查并扣减试用次数

#### 2. 吉他指法图增强（ChordViewer.tsx）
- 和弦库新增 60+ 种（含 B7, Bdim, Bmaj7, Dmaj7, Gm7, Gmaj7, Cm7, F7, Gm7, Gmaj7, Cm, Cm7, Ab, Abm7, Db, Eb, Ebm, Bb, Bbm 等爵士/变化和弦）
- SVG 指法图增加：
  - `radialGradient` 蓝色渐变指法圆点
  - `filter` glow 效果
  - 横按弧线高亮（`rect` opacity 渐变）
  - 和弦名标注改为渐变药丸 Badge 样式

#### 3. 分享功能（Result.tsx）
- 顶部导航栏新增「分享」按钮（Share2 图标）
- 点击调用 `navigator.clipboard.writeText(window.location.href)`
- 2.5 秒内显示「已复制 ✓」（CheckCheck 图标，绿底）
- Fallback: `prompt()` 对话框

#### 4. 长音频分段处理（pipeline.py）
- 新增 `MAX_CHUNK_SEC = 90` 常量
- `_chunk_audio(audio_path, output_dir, task_id)`: 超过 90 秒的音频自动切分为多段（每段 90 秒，5 秒 overlap 避免边界遗漏），使用 `librosa.load(offset=..., duration=...)` + `soundfile.write`
- `_merge_chords()`: 合并多段和弦识别结果（带时间偏移）
- `_merge_bass()`: 合并多段 Bass 音符结果

### Git Push 状态

⚠️ Git push 在 session 中被 SIGTERM 中断，需手动执行：

```bash
cd /workspace/AI-music-score-featch
git push origin main
```

远程已配置：
```
https://YuruiZhu9:${GITHUB_TOKEN}@github.com/YuruiZhu9/AI-music-score-featch.git
```

最新 commit: `1bed8f1` feat: v0.4.0 - Freemium模式+长音频分段+指法图增强+分享功能

---

## 历史记录

- 2026-04-02: v0.3.0 后端核心模块（BPM检测、乐谱生成、MusicXML、Pydantic模型）
- 2026-04-06: v0.4.0 前端 Freemium + 指法图增强 + 长音频分段 + 分享功能
