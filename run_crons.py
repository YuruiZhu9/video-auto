#!/usr/bin/env python3
"""Run both cron jobs and wait for completion."""
import subprocess
import time
import json

JOBS = [
    ("d4a0ebf8-49bf-4e73-b225-91eacbfca493", "免费语音克隆方案Agent"),
    ("f5afdfd6-068f-4518-80f8-fdf5f8741c1b", "AI协作视频制作Agent"),
]

results = []
for job_id, name in JOBS:
    print(f"\n{'='*60}")
    print(f"Running: {name} ({job_id})")
    print('='*60)
    result = subprocess.run(
        ["openclaw", "cron", "run", job_id],
        capture_output=True, text=True, timeout=900
    )
    output = result.stdout + result.stderr
    print(output)
    
    # Check if it started or was already-running
    try:
        data = json.loads(result.stdout)
        results.append({"name": name, "result": data})
    except:
        results.append({"name": name, "raw": output[:200]})

print("\n\n=== FINAL SUMMARY ===")
for r in results:
    print(f"{r['name']}: {r.get('result', r.get('raw', 'unknown'))[:100]}")
