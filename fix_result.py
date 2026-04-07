#!/usr/bin/env python3
import re

# Read Result.tsx
with open('/workspace/AI-music-score-featch/frontend/src/pages/Result.tsx', 'r') as f:
    content = f.read()

# 1. Add handleShare after handleExport
handle_export_end = content.find('[taskId]\n  );\n\n  // 生成 GTA 文本')
if handle_export_end == -1:
    handle_export_end = content.find('[taskId]\n  );\n\n  //')

share_code = '''

  // 分享功能
  const handleShare = useCallback(() => {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      setShared(true);
      setTimeout(() => setShared(false), 2500);
    }).catch(() => {
      prompt("复制以下链接分享结果：", url);
    });
  }, []);
'''

if 'handleShare' not in content:
    # Find the position right before "// 生成 GTA 文本"
    pattern = r"(\n  // 生成 GTA 文本\n  const gtaText)"
    replacement = share_code + r"\1"
    content = re.sub(pattern, replacement, content)

# 2. Add share button to header (after GitHub link)
# Find the GitHub link and add share button after it
old_github_section = '''<a
            href="https://github.com/YuruiZhu9/AI-music-score-featch"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <Github className="w-5 h-5" />
          </a>'''

new_github_section = '''<button
            onClick={handleShare}
            title="复制链接分享"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              shared
                ? 'bg-green-500 text-white'
                : 'text-gray-400 hover:text-green-500 hover:bg-green-50 dark:hover:bg-green-950/30'
            }`}
          >
            {shared ? (
              <><CheckCheck className="w-4 h-4" /> 已复制</>
            ) : (
              <><Share2 className="w-4 h-4" /> 分享</>
            )}
          </button>
          <a
            href="https://github.com/YuruiZhu9/AI-music-score-featch"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <Github className="w-5 h-5" />
          </a>'''

content = content.replace(old_github_section, new_github_section)

# 3. Add useCallback import (already have it)
# ensure 'useCallback' is in imports
if 'useCallback' not in content[:500]:
    # Already imported at top
    pass

# Write back
with open('/workspace/AI-music-score-featch/frontend/src/pages/Result.tsx', 'w') as f:
    f.write(content)

print("Result.tsx updated successfully")

# Verify
with open('/workspace/AI-music-score-featch/frontend/src/pages/Result.tsx', 'r') as f:
    c = f.read()
print("handleShare present:", 'handleShare' in c)
print("Share2 present:", 'Share2' in c)
print("CheckCheck present:", 'CheckCheck' in c)
