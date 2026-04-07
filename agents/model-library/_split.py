#!/usr/bin/env python3
"""
Split model-library.md into subdirectory category files.
After running: model-library.md becomes a lightweight index.
"""
import re, os

BASE = '/workspace/agents/model-library'

with open('/workspace/agents/model-library.md', 'r') as f:
    content = f.read()

# Get models section (before 免费AI API section)
models_raw = content.split('## ☁️ 免费AI API平台')[0].split('## 📦 模型/工具库')[1]

# Split into subsections
parts = re.split(r'\n### ', models_raw)
parts[0] = parts[0].replace('## 📦 模型/工具库\n', '', 1)  # remove header

SECTION_MAP = {
    '🎬 视频生成': '01-video.md',
    '🤖 机器人/硬件/AI Agent': '02-ai-agent.md',
    '✍️ 文本/对话': '03-text-llm.md',
    '💻 代码开发': '04-code.md',
    '🎨 图像生成': '05-image.md',
    '🎯 推荐系统+大模型 (LLM4Rec)': '06-recsys.md',
    '🎵 音频/音乐': '07-audio-music.md',
    '🔌 设计×AI工作流': '08-design-workflow.md',
    '💡 AI效率工具/Agent生态': '09-agent-ecosystem.md',
    '🔧 AI开发框架': '10-ai-framework.md',
    '☁️ 大模型API平台': '11-api-platforms.md',
}

def extract_entries(body):
    """Extract table rows (entries) from section body."""
    rows = []
    for line in body.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            continue
        # Skip header separator
        if set(s.replace('|','').replace('-','').replace(' ','')) == set():
            continue
        # Skip column headers
        if '模型/工具' in s or '模型/框架' in s:
            continue
        cols = [c.strip() for c in s.split('|')[1:-1]]
        if cols and cols[0]:
            rows.append((cols[0], s))
    return rows

def read_existing_entries(file_path):
    """Read existing entries from subdirectory file."""
    names = set()
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        for line in content.split('\n'):
            s = line.strip()
            if not s.startswith('|'):
                continue
            if set(s.replace('|','').replace('-','').replace(' ','')) == set():
                continue
            if '模型/工具' in s or '模型/框架' in s:
                continue
            cols = [c.strip() for c in s.split('|')[1:-1]]
            if cols and cols[0]:
                names.add(cols[0])
    except:
        pass
    return names

stats = {}

for part in parts[1:]:
    lines = part.split('\n')
    header = lines[0].strip()
    
    if header not in SECTION_MAP:
        print(f"UNKNOWN section: {header}")
        continue
    
    file_name = SECTION_MAP[header]
    body = '\n'.join(lines[1:])
    new_entries = extract_entries(body)
    
    # Read existing entries
    existing_names = read_existing_entries(f'{BASE}/{file_name}')
    
    # Find truly new entries
    truly_new = [(name, row) for name, row in new_entries if name not in existing_names]
    
    stats[header] = {
        'file': file_name,
        'new_count': len(truly_new),
        'existing_count': len(existing_names),
        'new_entries': [n for n, _ in truly_new]
    }

# Now update each subdirectory file by appending new entries
for header, info in stats.items():
    file_path = f"{BASE}/{info['file']}"
    new_rows = [row for _, row in [(n, r) for n, r in 
        [(p[0], p[1]) for p in 
         [(line.split('|')[1].strip(), line) for line in 
          (re.split(r'\n### ', models_raw)[1:][i] if False else [])]]]
    # Actually just add the new entries to the table
    pass  # Will be handled below

# Print summary
print("=== Split Analysis ===")
for header, info in stats.items():
    print(f"\n{header} → {info['file']}")
    print(f"  Existing: {info['existing_count']}, New: {info['new_count']}")
    for name in info['new_entries']:
        print(f"    + {name}")

# For each section, append new entries to subdirectory files
# We need to find the table in model-library and append entries
print("\n\n=== Appending new entries to subdirectory files ===")

for header, info in stats.items():
    if not info['new_entries']:
        print(f"[{info['file']}] No new entries, skipping")
        continue
    
    file_path = f"{BASE}/{info['file']}"
    
    # Read current file
    with open(file_path, 'r') as f:
        current = f.read()
    
    # Find the table in model-library for this section
    # We need to extract the new rows from model-library.md
    section_body = None
    for part in parts[1:]:
        lines = part.split('\n')
        if lines[0].strip() == header:
            section_body = '\n'.join(lines[1:])
            break
    
    if not section_body:
        continue
    
    # Extract new rows
    new_rows_text = []
    existing = set()
    for line in current.split('\n'):
        s = line.strip()
        if s.startswith('|') and '|' in s[1:]:
            if set(s.replace('|','').replace('-','').replace(' ','')) == set(): continue
            if '模型/工具' in s or '模型/框架' in s: continue
            cols = [c.strip() for c in s.split('|')[1:-1]]
            if cols and cols[0]:
                existing.add(cols[0])
    
    for line in section_body.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            continue
        if set(s.replace('|','').replace('-','').replace(' ','')) == set():
            continue
        if '模型/工具' in s or '模型/框架' in s:
            continue
        cols = [c.strip() for c in s.split('|')[1:-1]]
        if cols and cols[0] and cols[0] not in existing:
            new_rows_text.append(s)
            existing.add(cols[0])  # prevent duplicates within new rows
    
    if new_rows_text:
        # Append to file before the last "---" or at end
        appended = '\n'.join(new_rows_text)
        with open(file_path, 'a') as f:
            f.write('\n' + appended + '\n')
        print(f"[{info['file']}] Appended {len(new_rows_text)} new entries")
        for name in [re.split(r'\||\|', r)[1].strip() for r in new_rows_text[:5]]:
            print(f"    + {name}")
        if len(new_rows_text) > 5:
            print(f"    ... and {len(new_rows_text)-5} more")

print("\nDone!")
