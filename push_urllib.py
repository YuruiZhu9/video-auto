#!/usr/bin/env python3
"""使用 urllib 上传文件到 GitHub"""
import urllib.request, urllib.error, json, base64, os

TOKEN = "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"
REPO = "YuruiZhu9/AI-music-score-featch"
WORKDIR = "/workspace/AI-music-score-featch"

def api_put(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}{path}",
        data=body, method="PUT",
        headers={"Authorization": f"token {TOKEN}",
                 "Accept": "application/vnd.github.v3+json",
                 "Content-Type": "application/json; charset=utf-8"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get_sha(path):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{path}",
        headers={"Authorization": f"token {TOKEN}",
                 "Accept": "application/vnd.github.v3+json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get("sha", "")
    except:
        return ""

files = [
    ("backend/core/score_generator.py",
     "feat: 新增MIDI文件生成（Guitar Pro可导入MIDI）\n\nbuild_midi_file() 根据和弦+BPM生成标准MIDI文件，Guitar Pro可直接打开。"),
    ("backend/core/pipeline.py",
     "feat: pipeline集成MIDI生成（两套pipeline均支持）\n\n- Demo pipeline 和 Full pipeline 均调用 build_midi_file\n- score_files 新增 mid 字段"),
    ("backend/requirements.txt",
     "chore: 添加fpdf2依赖（PDF生成）\n\n- 新增 fpdf2==2.7.9（PDF乐谱生成）"),
]

for repo_path, msg in files:
    local = os.path.join(WORKDIR, repo_path)
    if not os.path.exists(local):
        print(f"跳过: {repo_path} 不存在")
        continue

    with open(local, "rb") as f:
        raw = f.read()
    encoded = base64.b64encode(raw).decode("ascii")

    print(f"上传 {repo_path} ({len(raw)} bytes)...", end=" ", flush=True)

    sha = get_sha(repo_path)
    data = {"message": msg, "content": encoded}
    if sha:
        data["sha"] = sha

    try:
        result = api_put(f"/contents/{repo_path}", data)
        commit_sha = result.get("commit", {}).get("sha", "?")[:8]
        print(f"✅ {commit_sha}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:150]
        print(f"❌ HTTP {e.code}: {body}")
    except Exception as e:
        print(f"❌ {e}")
