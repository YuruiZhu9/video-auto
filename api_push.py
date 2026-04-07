#!/usr/bin/env python3
"""
GitHub API Push — 绕过 git 协议直接通过 REST API 推送 commit
解决服务器到 GitHub git 端口连接不稳定的问题
"""
import os
import base64
import requests
import subprocess
import json
from pathlib import Path

TOKEN = "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"
REPO = "YuruiZhu9/AI-music-score-featch"
BRANCH = "main"
BASE_URL = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "AI-GT-Push/1.0"
}

REPO_DIR = Path("/workspace/AI-music-score-featch")


def api(path, method="GET", data=None, params=None):
    resp = requests.request(method, f"{BASE_URL}{path}",
                           headers=HEADERS, json=data, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_local_files():
    """获取本地有变化的文件（相对于 HEAD commit）"""
    # 获取远程 HEAD commit SHA
    ref = api(f"/git/refs/heads/{BRANCH}")
    remote_sha = ref["object"]["sha"]

    # 获取当前 HEAD commit
    result = subprocess.run(
        ["git", "-C", str(REPO_DIR), "rev-parse", "HEAD"],
        capture_output=True, text=True
    )
    local_sha = result.stdout.strip()

    print(f"Remote HEAD: {remote_sha}")
    print(f"Local HEAD:  {local_sha}")

    if remote_sha == local_sha:
        print("✅ 已经同步，无需推送")
        return None

    # 获取本地 commit 中的文件变更
    result = subprocess.run(
        ["git", "-C", str(REPO_DIR), "diff-tree", "--no-commit-id",
         "--name-status", "-r", local_sha],
        capture_output=True, text=True
    )
    files = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split("\t")
            if len(parts) >= 2:
                mode = parts[0]  # A=add, M=modify, D=delete
                filepath = parts[1]
                files.append((mode, filepath))
    return files, local_sha, remote_sha


def push_via_api():
    """通过 GitHub API 推送 commit"""
    result = api(f"/git/refs/heads/{BRANCH}")
    remote_sha = result["object"]["sha"]

    result = subprocess.run(
        ["git", "-C", str(REPO_DIR), "rev-parse", "HEAD"],
        capture_output=True, text=True
    )
    local_sha = result.stdout.strip()

    if remote_sha == local_sha:
        print("✅ 已经同步，无需推送")
        return True

    # 获取本地 commit 的 tree
    commit = api(f"/gitcommits/{local_sha}")
    local_tree_sha = commit["tree"]["sha"]

    # 获取需要推送的文件内容
    changed_files, _ = get_local_files()
    if not changed_files:
        return True

    new_tree_items = []
    for mode, filepath in changed_files:
        if mode == "D":
            new_tree_items.append({"path": filepath, "mode": "100644", "sha": None})
            continue

        full_path = REPO_DIR / filepath
        if not full_path.exists():
            print(f"  ⚠️ 跳过不存在的文件: {filepath}")
            continue

        content = full_path.read_bytes()
        encoded = base64.b64encode(content).decode()
        blob = api("/git/blobs", "POST", {
            "content": encoded,
            "encoding": "base64"
        })
        new_tree_items.append({
            "path": filepath,
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"]
        })
        print(f"  ✅ {filepath}")

    # 创建新 tree
    new_tree = api("/git/trees", "POST", {
        "base_tree": remote_sha,
        "tree": new_tree_items
    })

    # 获取 commit message
    result = subprocess.run(
        ["git", "-C", str(REPO_DIR), "log", "-1", "--format=%s%n%b", local_sha],
        capture_output=True, text=True
    )
    message = result.stdout.strip() or "更新"

    # 创建 commit
    new_commit = api("/git/commits", "POST", {
        "message": message,
        "tree": new_tree["sha"],
        "parents": [remote_sha]
    })

    # 更新 ref
    api(f"/git/refs/heads/{BRANCH}", "PATCH", {
        "sha": new_commit["sha"],
        "force": False
    })

    print(f"\n🎉 推送成功！commit: {new_commit['sha'][:8]}")
    return True


if __name__ == "__main__":
    print("=== GitHub API Push ===")
    try:
        push_via_api()
    except Exception as e:
        print(f"❌ 失败: {e}")
        exit(1)
