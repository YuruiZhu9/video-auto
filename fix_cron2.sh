#!/bin/bash
# Fix remaining cron job issues identified at 2026-03-27 13:00

fix_edit() {
  local id=$1; local name=$2; shift 2
  local result=$(timeout 25 openclaw cron edit "$id" "$@" 2>/dev/null)
  if echo "$result" | grep -q "updatedAtMs"; then
    echo "✅ $name: FIXED"
  else
    echo "❌ $name: FAILED"
    echo "   Raw: $(echo $result | head -1)"
  fi
}

echo "=== Fix 1: 技术前沿分析师 - 添加 delivery to ==="
fix_edit fc435f87-e84d-4647-84ed-094a642ace18 "技术前沿分析师" --to 03003745585526383319

echo ""
echo "=== Fix 2: 信息抓取助手 - timeout 900→1200 ==="
fix_edit b663647c-6013-4ebb-a8d4-385454a46e03 "信息抓取助手" --timeout-seconds 1200

echo ""
echo "=== Fix 3: LeetCode刷题 - timeout 600→900 ==="
fix_edit 2dbd0716-91ca-48e4-a937-bb1c450083e7 "LeetCode刷题" --timeout-seconds 900

echo ""
echo "=== Fix 4: OpenClaw配置专家 - timeout 600→900 ==="
fix_edit 2e4adb92-e1d3-4c63-aaad-87f81198cb6c "OpenClaw配置" --timeout-seconds 900

echo ""
echo "=== Fix 5: AI-Coding-Workflow - 添加 best-effort ==="
fix_edit 350348c3-0215-4b78-98a5-65b2ed594f14 "AI-Coding" --best-effort-deliver

echo ""
echo "=== Creating missing memory file ==="
touch /workspace/memory/openclaw-insights.md 2>/dev/null && echo "✅ created" || echo "⚠️  touch failed"

echo ""
echo "=== Done ==="
