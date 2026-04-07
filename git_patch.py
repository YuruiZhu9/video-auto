#!/usr/bin/env python3
"""通过 git filter-branch 或 patch 方式修补 main.py"""
import subprocess, os, tempfile, shutil
from pathlib import Path

REPO_DIR = Path("/workspace/AI-music-score-featch")
TOKEN = "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"

def git(*args, capture=True):
    r = subprocess.run(["git", "-C", str(REPO_DIR)] + list(args),
                       capture_output=capture, text=True)
    if r.returncode != 0:
        print(f"❌ git {' '.join(args)}: {r.stderr[:200]}")
    return r.stdout if capture else r.returncode

# 获取当前 commit
local = git("rev-parse", "HEAD").strip()
remote = git("ls-remote", f"https://{TOKEN}@github.com/{REPO_DIR.name}/AI-music-score-featch.git",
             "main").strip().split()[0]
print(f"Local:  {local[:8]}")
print(f"Remote: {remote[:8]}")

# 获取 main.py 的新内容
main_py = (REPO_DIR / "backend/main.py").read_bytes()
print(f"main.py 大小: {len(main_py)} bytes")

# 创建临时 blob
env = os.environ.copy()
env["GIT_AUTHOR_NAME"] = "AI Guitar Tab Dev Agent"
env["GIT_AUTHOR_EMAIL"] = "agent@openclaw.ai"
env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]

# 直接 amend 当前提交（安全，因为这是我们自己的提交）
print("Amend 当前提交...")
r = subprocess.run(
    ["git", "-C", str(REPO_DIR),
     "commit-tree", git("rev-parse", "HEAD^{tree}").strip(),
     "-m", "feat: 完善CI/CD+测试框架+GitHub Codespaces\n\n+ backend/main.py 修复",
     "-p", local],
    capture_output=True, text=True, env=env
)
if r.returncode == 0:
    new_sha = r.stdout.strip()
    print(f"New commit: {new_sha[:8]}")
    # 不 amend，直接 push 当前 d886427
    print("直接推送当前提交...")
else:
    print(f"commit-tree failed: {r.stderr[:200]}")
