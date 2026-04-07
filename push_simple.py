#!/usr/bin/env python3
"""
GitHub 直接文件更新 API（PUT /repos/{owner}/contents/{path}）
一条 API 调用直接创建 commit，无需手动创建 blob/tree
"""
import json, base64, subprocess, os

TOKEN = "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"
REPO = "YuruiZhu9/AI-music-score-featch"
BASE = f"https://api.github.com/repos/{REPO}"
WORKDIR = "/workspace/AI-music-score-featch"

def curl(method, path, data=None):
    body = json.dumps(data, ensure_ascii=False) if data is not None else None
    args = ["curl", "-s", "-X", method,
            "-H", f"Authorization: token {TOKEN}",
            "-H", "Accept: application/vnd.github.v3+json",
            "-H", "Content-Type: application/json; charset=utf-8"]
    if body:
        with open("/tmp/gh_api_req.json", "w", encoding="utf-8") as f:
            f.write(body)
        args += ["-d", "@/tmp/gh_api_req.json"]
    r = subprocess.run(args + [f"{BASE}{path}"],
                        capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout)
    except:
        print(f"非JSON响应: {r.stdout[:200]}")
        return {}

def get_sha(path_in_repo):
    """获取仓库中现有文件的 SHA（用于更新）"""
    r = curl("GET", f"/contents/{path_in_repo}")
    return r.get("sha")

def upsert_file(repo_path, local_path, message):
    """直接写入/更新文件到 GitHub"""
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")

    data = {
        "message": message,
        "content": content,
    }
    # 如果文件存在，需要 sha
    sha = get_sha(repo_path)
    if sha:
        data["sha"] = sha
        action = "更新"
    else:
        action = "创建"

    result = curl("PUT", f"/contents/{repo_path}", data)
    if "commit" in result:
        print(f"  ✅ {action}: {repo_path} → {result['commit']['sha'][:8]}")
    else:
        print(f"  ❌ 失败: {repo_path}: {result.get('message', '')[:100]}")

files = [
    ("ai-guitar-tab-frontend/src/api/client.ts",
     f"{WORKDIR}/ai-guitar-tab-frontend/src/api/client.ts",
     "feat: 新增 analyzeUrl() 视频URL分析API"),
    ("ai-guitar-tab-frontend/src/pages/Home.tsx",
     f"{WORKDIR}/ai-guitar-tab-frontend/src/pages/Home.tsx",
     "feat: 启用视频URL提交（Home.tsx URL入口已激活）"),
    ("backend/core/pipeline.py",
     f"{WORKDIR}/backend/core/pipeline.py",
     "feat: pipeline新增Demo CPU降级模式（无GPU自动fallback）"),
    ("backend/main.py",
     f"{WORKDIR}/backend/main.py",
     "fix: /api/download路径修复 + analyze-url端点完善"),
]

print("=== GitHub 直接文件写入 ===")
for repo_path, local_path, msg in files:
    if not os.path.exists(local_path):
        print(f"  跳过: {local_path} 不存在")
        continue
    upsert_file(repo_path, local_path, msg)

print("\n=== 验证 ===")
ref = curl("GET", "/git/refs/heads/main")
print(f"远程 HEAD: {ref.get('object',{}).get('sha','')[:12]}")
