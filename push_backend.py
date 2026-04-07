#!/usr/bin/env python3
"""分别上传 backend 文件"""
import json, base64, subprocess, os

TOKEN = "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"
REPO = "YuruiZhu9/AI-music-score-featch"
BASE = f"https://api.github.com/repos/{REPO}"
WORKDIR = "/workspace/AI-music-score-featch"

def curl_put(path, data):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    with open("/tmp/gh_req.json", "wb") as f:
        f.write(body)
    r = subprocess.run(
        ["curl", "-s", "-X", "PUT",
         "-H", f"Authorization: token {TOKEN}",
         "-H", "Accept: application/vnd.github.v3+json",
         "-H", "Content-Type: application/json; charset=utf-8",
         "-d", f"@{'/tmp/gh_req.json'}",
         f"{BASE}{path}"],
        capture_output=True, text=True, timeout=60
    )
    try:
        return json.loads(r.stdout)
    except:
        return {"error": r.stdout[:300]}

def get_sha(path):
    r = subprocess.run(
        ["curl", "-s", "-X", "GET",
         "-H", f"Authorization: token {TOKEN}",
         "-H", "Accept: application/vnd.github.v3+json",
         f"{BASE}/contents/{path}"],
        capture_output=True, text=True, timeout=30
    )
    try:
        d = json.loads(r.stdout)
        return d.get("sha", "")
    except:
        return ""

files = [
    ("backend/core/pipeline.py", "feat: pipeline新增Demo CPU降级模式（无GPU自动fallback）"),
    ("backend/main.py", "fix: /api/download路径修复 + analyze-url端点完善"),
]

for repo_path, msg in files:
    local = os.path.join(WORKDIR, repo_path)
    if not os.path.exists(local):
        print(f"跳过: {repo_path} 不存在"); continue

    with open(local, "rb") as f:
        raw = f.read()
    encoded = base64.b64encode(raw).decode("ascii")
    print(f"  {repo_path} ({len(raw)} bytes)...")

    sha = get_sha(repo_path)
    data = {"message": msg, "content": encoded}
    if sha:
        data["sha"] = sha

    result = curl_put(f"/contents/{repo_path}", data)
    if "commit" in result:
        print(f"  ✅ → {result['commit']['sha'][:8]}")
    else:
        print(f"  ❌ {result.get('message', result.get('error',''))[:100]}")
