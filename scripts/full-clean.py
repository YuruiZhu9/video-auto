#!/usr/bin/env python3
import subprocess, os, re

TOKEN_OLD = os.environ.get("TOKEN_OLD", "")
TOKEN_REPL = "[TOKEN_REMOVED]"
os.chdir("/workspace")

# 1. 清理当前工作区文件中的旧 token
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
    for fn in files:
        if fn.endswith(".md") or fn.endswith(".sh") or fn.endswith(".json"):
            fp = os.path.join(root, fn)
            try:
                with open(fp, "r") as f:
                    content = f.read()
                if TOKEN_OLD in content:
                    new_content = content.replace(TOKEN_OLD, TOKEN_REPL)
                    with open(fp, "w") as f:
                        f.write(new_content)
                    print(f"Cleaned: {fp}")
            except Exception as e:
                print(f"Skip {fp}: {e}")

# 2. git add + commit
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "chore: remove old token from workspace files"], check=True)
print("Committed all changes")

# 3. 清理历史中所有 .md/.sh/.json 里的旧 token
env = os.environ.copy()
env["FILTER_BRANCH_SQUELCH_WARNING"] = "1"

# 找到所有含旧 token 的 commit，对每个 commit 做 tree-filter 替换
filter_cmd = (
    f"find . -type f \\( -name '*.md' -o -name '*.sh' -o -name '*.json' \\) "
    f"-exec sed -i 's/{TOKEN_OLD}/{TOKEN_REPL}/g' {{}} \\; 2>/dev/null || true"
)

proc = subprocess.Popen(
    ["git", "filter-branch", "--force", "--tree-filter", filter_cmd,
     "--prune-empty", "--tag-name-filter", "cat", "--", "--all"],
    env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)
output, _ = proc.communicate()
print("filter-branch output (last 2000 chars):")
print(output.decode()[-2000:])
print("filter-branch rc:", proc.returncode)

# 4. 强制 push
r1 = subprocess.run(["git", "push", "origin", "master", "--force", "--quiet"])
print("origin push:", "OK" if r1.returncode == 0 else f"FAIL (rc={r1.returncode})")
r2 = subprocess.run(["git", "push", "maxclaw-", "master", "--force", "--quiet"])
print("maxclaw- push:", "OK" if r2.returncode == 0 else f"FAIL (rc={r2.returncode})")
print("=== ALL DONE ===")
