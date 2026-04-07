#!/usr/bin/env python3
import re

with open('/workspace/AI-music-score-featch/frontend/src/components/ChordViewer.tsx', 'r') as f:
    content = f.read()

# Add more chord shapes to CHORD_SHAPES
# Find the closing brace of CHORD_SHAPES and add new chords

old_shapes_end = '''  // 六和弦
  A6: { positions: [-1, 0, 2, 2, 2, 2], finger: [0, 1, 2, 3, 4, 4] },
  Am6: { positions: [0, 1, 2, 2, 1, 2], finger: [0, 1, 2, 3, 1, 4] },
};'''

new_shapes_end = '''  // 六和弦
  A6: { positions: [-1, 0, 2, 2, 2, 2], finger: [0, 1, 2, 3, 4, 4] },
  Am6: { positions: [0, 1, 2, 2, 1, 2], finger: [0, 1, 2, 3, 1, 4] },

  // ─── 更多常用和弦（扩展库）──────────────────────────────
  // B 系
  B7:   { positions: [-1, 2, 1, 2, 0, 2], finger: [0, 2, 1, 3, 0, 4] },
  Bdim: { positions: [-1, 2, 3, 1, 3, -1], finger: [0, 1, 3, 0, 2, 0] },
  Bm7:  { positions: [-1, 2, 4, 2, 3, -1], barre: 2, finger: [0, 1, 4, 0, 2, 0] },
  Bmaj7:{ positions: [-1, 2, 4, 3, 4, -1], finger: [0, 1, 3, 2, 4, 0] },

  // D 系
  Dm7:  { positions: [-1, -1, 0, 2, 1, 1], finger: [0, 0, 0, 2, 1, 1] },
  Dmaj7:{ positions: [-1, -1, 0, 2, 2, 2], finger: [0, 0, 0, 1, 3, 4] },

  // E 系扩展
  Em7:  { positions: [0, 2, 0, 0, 0, 0], finger: [0, 1, 0, 0, 0, 0] },
  Edim: { positions: [0, 1, 2, 1, 0, -1], finger: [0, 1, 2, 1, 0, 0] },

  // F 系扩展
  Fm:   { positions: [1, 3, 3, 3, 1, 1], barre: 1, finger: [1, 3, 4, 4, 1, 1] },
  F7:   { positions: [1, 3, 1, 2, 1, 1], barre: 1, finger: [1, 3, 0, 2, 1, 1] },
  Fm7:  { positions: [1, 3, 1, 1, 1, 1], barre: 1, finger: [1, 3, 0, 0, 0, 0] },

  // G 系扩展
  Gm:   { positions: [3, 5, 5, 3, 3, 3], barre: 3, finger: [1, 4, 4, 1, 1, 1] },
  Gm7:  { positions: [3, 5, 3, 3, 3, 3], barre: 3, finger: [1, 4, 0, 0, 0, 0] },
  Gmaj7:{ positions: [3, 2, 0, 0, 0, 2], finger: [2, 1, 0, 0, 0, 1] },

  // A 系扩展
  Aaug: { positions: [-1, 0, 3, 2, 2, 1], finger: [0, 1, 4, 2, 2, 1] },
  Adim: { positions: [-1, 0, 1, 2, 1, -1], finger: [0, 1, 2, 3, 1, 0] },
  A7sus4:{ positions: [-1, 0, 2, 0, 3, 0], finger: [0, 1, 2, 0, 3, 0] },

  // C 系扩展
  Cm:   { positions: [-1, 3, 5, 5, 4, -1], barre: 3 },
  Cm7:  { positions: [-1, 3, 5, 3, 4, -1], barre: 3, finger: [0, 1, 4, 0, 2, 0] },
  Cmaj9:{ positions: [-1, 3, 2, 0, 0, 0], finger: [0, 1, 2, 0, 0, 0] },

  // 爵士常用
  Ab:   { positions: [-1, 1, 3, 3, 3, 1], barre: 1 },
  Abm7: { positions: [-1, 1, 3, 1, 2, -1], barre: 1 },
  Db:   { positions: [-1, -1, 0, 3, 4, 3], barre: 1, finger: [0, 0, 0, 1, 3, 1] },
  Eb:   { positions: [-1, 3, 3, 1, 3, -1], barre: 3 },
  Ebm:  { positions: [1, 3, 3, 2, 1, 1], barre: 1, finger: [1, 3, 4, 2, 1, 1] },
  Bb:   { positions: [-1, 1, 3, 3, 3, 1], barre: 1 },
  Bbm:  { positions: [-1, 2, 4, 4, 3, -1], barre: 2 },
};'''

content = content.replace(old_shapes_end, new_shapes_end)

# Add visual enhancements to GuitarDiagram SVG
# Replace the SVG with improved version (add gradient defs, better colors)
old_svg_start = '''  return (
    <div className="flex flex-col items-center">
      <svg
        width={svgWidth}
        height={svgHeight}
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="overflow-visible"
      >
        {/* 琴头（左侧装饰） */}
        <rect'''

new_svg_start = '''  return (
    <div className="flex flex-col items-center">
      <svg
        width={svgWidth}
        height={svgHeight}
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="overflow-visible drop-shadow-sm"
      >
        {/* SVG 渐变定义 */}
        <defs>
          <radialGradient id={`fret-grad-${chordName}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#2563EB" stopOpacity="0.8" />
          </radialGradient>
          <filter id={`glow-${chordName}`}>
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* 琴头（左侧装饰） */}
        <rect'''

content = content.replace(old_svg_start, new_svg_start)

# Improve finger dot rendering - add glow effect and gradient
old_finger_render = '''            const color = shape.finger?.[strIdx]
              ? fingerColors[shape.finger[strIdx]]
              : '#3B82F6';
            const label = shape.finger?.[strIdx]
              ? fingerLabels[shape.finger[strIdx]]
              : '';'''

new_finger_render = '''            const color = shape.finger?.[strIdx]
              ? fingerColors[shape.finger[strIdx]]
              : '#3B82F6';
            const label = shape.finger?.[strIdx]
              ? fingerLabels[shape.finger[strIdx]]
              : '';
            const dotId = `dot-${chordName}-${strIdx}`;'''

content = content.replace(old_finger_render, new_finger_render)

# Improve the chord name label - add a pill badge style
old_label_div = '''      {/* 和弦名标注 */}
      <div className="text-xs font-bold text-gray-600 dark:text-gray-300 mt-1 font-mono">
        {chordName}
      </div>'''

new_label_div = '''      {/* 和弦名标注（带渐变背景） */}
      <div className="mt-1 px-2.5 py-0.5 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-xs font-bold font-mono shadow-sm">
        {chordName}
      </div>'''

content = content.replace(old_label_div, new_label_div)

with open('/workspace/AI-music-score-featch/frontend/src/components/ChordViewer.tsx', 'w') as f:
    f.write(content)

print("ChordViewer.tsx enhanced successfully")

# Verify
with open('/workspace/AI-music-score-featch/frontend/src/components/ChordViewer.tsx', 'r') as f:
    c = f.read()
print("B7 chord added:", 'B7:' in c)
print("Jazz chords added:", 'Gm7:' in c)
print("Gradient label:", 'bg-gradient-to-r from-blue-500 to-indigo-600' in c)
print("SVG glow:", 'glow' in c)
