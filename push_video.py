#!/usr/bin/env python3
import os, time, json, base64, urllib.request, urllib.error

REPO = "YuruiZhu9/video-auto"
TOKEN = "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"
API = f"https://api.github.com/repos/{REPO}/contents"
VIDEO_DIR = "/workspace/agents/video-auto/video"
AGENTS_PATH = "/workspace/agents/video-auto/AGENTS.md"

headers_base = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def gh_get(path):
    req = urllib.request.Request(f"{API}/{path}", headers=headers_base)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, "NOT_FOUND"
        return None, f"HTTP_{e.code}"

def gh_put(path, content_b64, sha=None, msg=""):
    payload = {
        "message": msg,
        "content": content_b64
    }
    if sha:
        payload["sha"] = sha
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API}/{path}",
        data=data,
        headers={**headers_base, "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

results = []

# Push 9 MP4 files
video_files = [f"slide{i:02d}.mp4" for i in range(1, 10)]
for fname in video_files:
    local_path = os.path.join(VIDEO_DIR, fname)
    if not os.path.exists(local_path):
        results.append((fname, "SKIP", "本地文件不存在", None))
        continue

    print(f"处理: {fname}")
    obj, err = gh_get(f"video/{fname}")

    sha = obj["sha"] if obj else None
    if err == "NOT_FOUND":
        print(f"  → 新文件，无 SHA")
    elif err:
        print(f"  → GET 失败: {err}")
    else:
        print(f"  → 已有 SHA: {sha[:8]}...")

    with open(local_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    try:
        res = gh_put(f"video/{fname}", b64, sha=sha, msg=f"Add/update video: {fname}")
        commit_url = res.get("commit", {}).get("html_url", "unknown")
        results.append((fname, "SUCCESS", commit_url, None))
        print(f"  ✅ 成功: {commit_url}")
    except Exception as e:
        results.append((fname, "FAILED", None, str(e)))
        print(f"  ❌ 失败: {e}")

    time.sleep(1.2)

# Push AGENTS.md
print("\n处理: AGENTS.md")
with open(AGENTS_PATH, "rb") as f:
    b64_agents = base64.b64encode(f.read()).decode()

obj, err = gh_get("AGENTS.md")
sha_agents = obj["sha"] if obj else None
if err == "NOT_FOUND":
    print("  → 新文件，无 SHA")
elif err:
    print(f"  → GET 失败: {err}")
else:
    print(f"  → 已有 SHA: {sha_agents[:8]}...")

try:
    res = gh_put("AGENTS.md", b64_agents, sha=sha_agents, msg="Update AGENTS.md documentation")
    commit_url = res.get("commit", {}).get("html_url", "unknown")
    results.append(("AGENTS.md", "SUCCESS", commit_url, None))
    print(f"  ✅ 成功: {commit_url}")
except Exception as e:
    results.append(("AGENTS.md", "FAILED", None, str(e)))
    print(f"  ❌ 失败: {e}")

# Summary
print("\n" + "="*60)
print("推送结果汇总:")
print("="*60)
for name, status, url, err in results:
    if status == "SUCCESS":
        print(f"  ✅ {name} → {url}")
    elif status == "SKIP":
        print(f"  ⏭️  {name} → 跳过（{err}）")
    else:
        print(f"  ❌ {name} → 失败: {err}")
