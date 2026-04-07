---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 635187052c752dfb2867d04661285660
    PropagateID: 635187052c752dfb2867d04661285660
    ReservedCode1: 304402205358ab0c8c538acf9b5061ec91e7250bfec91bcf25d265324d568d7b95b7bc63022021cb1814004a755b174e231da4734880c299ec6b5ec24988377a676829ee3fd3
    ReservedCode2: 304502206a33ae15d8a6fd2111dda260d7b41f057fb8e4b012c6f7f84246a5fba3b5faad0221009278aa806cde8acc90954b0e6684498bea99c2be8fa701f2c70622ac89b6572c
---

# AI Guitar Tab — 调试总结报告

**日期**: 2026-03-27
**调试人**: 小M

---

## 一、修复的问题

### 1. `mido.bpm_to_ticktime` 错误 ✅
- **文件**: `backend/core/score_generator.py`
- **问题**: `mido` 库没有 `bpm_to_ticktime` 方法（这是项目代码的自创方法，不存在于 mido）
- **修复**: 改为 `int(60_000_000 / bpm)`（MIDI tempo 微秒值标准公式）
```python
# 修复前
t_track.append(MetaMessage("set_tempo", tempo=mido.bpm_to_ticktime(bpm, tpq, 500000)))
# 修复后
t_track.append(MetaMessage("set_tempo", tempo=int(60_000_000 / bpm)))
```

### 2. `name 'MetaMessage' is not defined` ✅
- **文件**: `backend/core/score_generator.py`
- **根因**: `MetaMessage` 在 `build_midi_file()` 函数内部 import，但全局辅助函数 `_add_chords_to_track()` 和 `_add_bass_notes_to_track()` 也调用了它 → Python 在全局作用域找不到该名称
- **修复**: 将 mido 相关 import 提升至模块顶层
```python
# 顶层
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
```
- **验证**: MIDI 文件结构完全正确，Guitar Pro 可打开：
  - 轨0: Tempo (120BPM, 4/4)
  - 轨1: Guitar (program 24 = 尼龙吉他音色)
  - 轨2: Bass (program 33 = 指弹贝司音色 + A2 音符)

---

## 二、测试音频验证

使用 `audios_understand` 模型对两个测试音频进行深度分析：

| 文件 | AI分析结果 | 结论 |
|------|-----------|------|
| `fb89949e-*.wav` | 清晰钢弦民谣吉他音阶练习录音 | ✅ 真实吉他 |
| `test_guitar.wav` | 专业级指弹独奏（含泛音、滑音、打板技巧） | ✅ 真实吉他 |

> 两个文件均为高质量真实吉他录音，非空信号或合成音色。

---

## 三、现有功能状态

| 模块 | 状态 | 说明 |
|------|------|------|
| GTA 文本谱 | ✅ 正常 | 生成 ASCII 六线谱，含 Bass 把位图 |
| MIDI 双轨 | ✅ 正常 | Guitar Pro / REAPER 可导入 |
| BPM 检测 | ⚠️ 有限 | 吉他音阶/练习曲节奏不规律，librosa 返回 0 → 降级为 120 |
| 和弦识别 | ⚠️ 有限 | librosa 对 solo 吉他音阶效果差，返回 0 个和弦 |
| Bass 识别 | ⚠️ 有限 | librosa 低频检测把吉他当 bass（吉他 E2-E6 在 bass 范围内）|
| Guitar 音符 | ❌ 需 GPU | basic_pitch 需要 torch，沙盒 CPU 环境无法安装 |

---

## 四、核心限制说明

**为什么吉他被识别为 bass？**
- 吉他的最低弦 E2（82Hz）与 bass 吉他最低音 E1（41Hz）频率有重叠
- librosa 的低频检测器没有乐器分类能力，看到低频能量就判定为 bass
- 音阶练习（单音，无和声）缺乏和弦特征，进一步降低识别准确性

**正确的使用场景：**
- 🎸 完整有节拍的吉他弹唱歌曲 → 和弦识别较好
- 🎸 节奏稳定的电吉他solo → BPM 检测可用
- 🎸 需要 GPU 算力 → 安装 `torch` + `basic-pitch` 后吉他音符识别可用

---

## 五、下一步建议

1. **GPU 环境**：安装 torch + basic-pitch，进行完整吉他音符识别测试
2. **测试曲选择**：用有清晰节拍、完整和弦的吉他弹唱曲目（而非练习音阶）
3. **BPM 改进**：可集成 `librosa.beat.beat_track` 的替代方案或 CREPE 音高检测
4. **Guitar Pro 输出**：当前 MIDI 兼容 Guitar Pro，可进一步生成 .gtp/.gpib 专有格式
