#!/usr/bin/env python3
"""GitHub API push - 用临时文件传 JSON 避免 shell 转义"""
import json, base64, subprocess, os, tempfile

TOKEN = "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"
REPO = "YuruiZhu9/AI-music-score-featch"
BASE = f"https://api.github.com/repos/{REPO}"
WORKDIR = "/workspace/AI-music-score-featch"

def api(method, path, data=None):
    body = json.dumps(data, ensure_ascii=False) if data is not None else None
    args = ["curl", "-s", "-X", method,
            "-H", f"Authorization: token {TOKEN}",
            "-H", "Accept: application/vnd.github.v3+json",
            "-H", "Content-Type: application/json; charset=utf-8"]
    if body:
        # 写到临时文件，避免 shell 变量转义问题
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write(body)
            tmp = f.name
        args += ["-d", f"@{tmp}"]
    else:
        tmp = None
    r = subprocess.run(args + [f"{BASE}{path}"],
                       capture_output=True, text=True, timeout=30)
    if tmp:
        os.unlink(tmp)
    return json.loads(r.stdout)

print("=== 获取远程状态 ===")
ref = api("GET", "/git/refs/heads/main")
remote_sha = ref["object"]["sha"]
print(f"Remote: {remote_sha[:8]}")

base_tree = api("GET", f"/git/trees/{remote_sha}")["sha"]
print(f"Base tree: {base_tree[:8]}")

files = [
    "ai-guitar-tab-frontend/src/api/client.ts",
    "ai-guitar-tab-frontend/src/pages/Home.tsx",
    "backend/core/pipeline.py",
    "backend/main.py",
]

print("\n=== 上传文件 ===")
tree = []
for fp in files:
    full = os.path.join(WORKDIR, fp)
    if not os.path.exists(full):
        print(f"  跳过: {fp}"); continue
    raw = open(full,"rb").read()
    blob = api("POST", "/git/blobs", {
        "content": base64.b64encode(raw).decode("ascii"),
        "encoding": "base64"
    })
    sha = blob.get("sha","?")[:8]
    print(f"  ✅ {fp} ({len(raw)} bytes) → {sha}")
    tree.append({"path": fp, "mode": "100644", "type": "blob", "sha": blob["sha"]})

print("\n=== 创建 Tree ===")
new_tree = api("POST", "/git/trees", {"base_tree": base_tree, "tree": tree})
tree_sha = new_tree.get("sha","?")[:8]
print(f"Tree: {tree_sha}")

print("\n=== 创建 Commit ===")
msg = ("feat: 启用URL分析+Demo降级+下载路径修复\n\n"
       "- Home.tsx: 启用视频URL提交\n"
       "- api/client.ts: 新增 analyzeUrl()\n"
       "- pipeline.py: 新增 Demo CPU 模式\n"
       "- main.py: /api/download 路径修复")
nc = api("POST", "/git/commits",
         {"message": msg, "tree": new_tree["sha"], "parents": [remote_sha]})
nc_sha = nc.get("sha","?")[:8]
print(f"Commit: {nc_sha}")

print("\n=== 更新分支 ===")
result = api("PATCH", "/git/refs/heads/main", {"sha": nc["sha"]})
final = result.get("object",{}).get("sha","?")[:8]
print(f"\n🎉 完成! Remote HEAD: {final}")
