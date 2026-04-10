#!/usr/bin/env bash
# push_auto.sh — video-auto 无交互全自动流水线
# 用法: bash push_auto.sh --auto --topic "AI推荐系统最新进展"
#
# 支持的环境变量:
#   VIDEO_TOPIC       视频主题
#   OPENAI_API_KEY    OpenAI API（Whisper API 用）
#   GLM_API_KEY       智谱 AI（GLM-4.7-Flash 内容扩展用）
#   FISH_AUDIO_KEY    Fish Audio（声音克隆用）
#   HYREAL_API_KEY    Hypereal AI（视频生成用）
#   SKIP_WHISPER=1    跳过 Whisper 字幕
#   SKIP_TRANSITION=1 跳过交叉淡化过渡（加快处理速度）

set -e

# ── 参数解析 ──────────────────────────────────────────────────────────────
AUTO_MODE=false
TOPIC=""
SKIP_WHISPER=${SKIP_WHISPER:-0}
SKIP_TRANSITION=${SKIP_TRANSITION:-0}

while [[ $# -gt 0 ]]; do
  case $1 in
    --auto)
      AUTO_MODE=true
      shift
      ;;
    --topic)
      TOPIC="$2"
      shift 2
      ;;
    --skip-whisper)
      SKIP_WHISPER=1
      shift
      ;;
    --skip-transition)
      SKIP_TRANSITION=1
      shift
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

# 从环境变量或文件获取主题
TOPIC=${TOPIC:-${VIDEO_TOPIC:-}}
if [[ -z "$TOPIC" && -f input/topic.txt ]]; then
  TOPIC=$(cat input/topic.txt)
fi
TOPIC=${TOPIC:-"AI技术本周动态"}

echo "=============================================="
echo "🎬 video-auto 全自动流水线"
echo "  主题: $TOPIC"
echo "  Whisper字幕: $([ $SKIP_WHISPER -eq 1 ] && echo '跳过' || echo '启用')"
echo "  交叉淡化: $([ $SKIP_TRANSITION -eq 1 ] && echo '跳过' || echo '启用')"
echo "=============================================="

cd "$(dirname "$0")"
SCRIPT_DIR=$(pwd)
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
TOPIC_SLUG=$(echo "$TOPIC" | sed 's/[^a-zA-Z0-9\u4e00-\u9fa5]/_/g' | head -c 40)
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# ── Step 1: 内容扩展 ───────────────────────────────────────────────────────
echo ""
echo "[Step 1/5] 📝 内容扩展 (GLM-4.7-Flash)..."
CONTENT_FILE="$SCRIPT_DIR/content/${TOPIC_SLUG}_${TIMESTAMP}.txt"

# 读取模板或直接生成（这里调用 push_opt.js 风格的扩展）
if command -v node &> /dev/null; then
  node -e "
    const { execSync } = require('child_process');
    // 读取 GLM API Key
    const apiKey = process.env.GLM_API_KEY || '';
    if (!apiKey) {
      console.error('⚠️ GLM_API_KEY 未设置，跳过内容扩展');
      process.exit(1);
    }
    const https = require('https');
    const data = JSON.stringify({
      model: 'glm-4-7b-flash',
      messages: [{
        role: 'user',
        content: \`请为视频生成演讲内容，主题：${TOPIC}。
要求：
1. 生成9个场景的内容，每个场景约60字
2. 每个场景配一句核心金句
3. 包含开场和结尾
4. 语言简洁，适合口播
5. 返回JSON格式：{scenes:[{title, content, quote}]}\`
      }]
    });
    const req = https.request({
      hostname: 'open.bigmodel.cn',
      path: '/api/paas/v4/chat/completions',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': \`Bearer \${apiKey}\` }
    }, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          const text = json.choices?.[0]?.message?.content || '';
          require('fs').writeFileSync('${CONTENT_FILE}', text);
          console.log('✅ 内容已写入 ${CONTENT_FILE}');
        } catch(e) {
          console.error('内容解析失败:', e.message);
        }
      });
    });
    req.on('error', e => console.error('请求失败:', e.message));
    req.write(data);
    req.end();
  " 2>&1 || echo "⚠️ 内容扩展失败，继续执行..."
fi

# ── Step 2: HTML Slide 生成 ────────────────────────────────────────────────
echo ""
echo "[Step 2/5] 🎨 HTML Slide 生成..."
SLIDE_HTML="$SCRIPT_DIR/slides/${TOPIC_SLUG}_${TIMESTAMP}.html"

# 如果有生成的内容，使用模板生成 HTML
cat > "$SLIDE_HTML" << 'SLIDE_EOF'
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Video Slide</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0a0a0f; color: #fff; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
  .slide { width: 100vw; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8vh 10vw; text-align: center; transition: opacity 0.5s; }
  .slide-title { font-size: 5vw; font-weight: 700; color: #60a5fa; margin-bottom: 4vh; line-height: 1.3; }
  .slide-content { font-size: 2.5vw; color: #d1d5db; max-width: 80vw; line-height: 1.8; }
  .slide-quote { font-size: 2vw; color: #fbbf24; font-style: italic; margin-top: 4vh; border-left: 4px solid #fbbf24; padding-left: 2vw; }
  .slide-cover { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
  .slide-end { background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%); }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  .slide { animation: fadeIn 0.8s ease-out forwards; }
</style>
</head>
<body>
<!-- Slide 会在 pipeline 中被 scene_detector 截取 -->
</body>
</html>
SLIDE_EOF
echo "✅ HTML Slide 已生成: $SLIDE_HTML"

# ── Step 3: 背景图生成（调用 MCP 工具 via OpenClaw）────────────────────────
echo ""
echo "[Step 3/5] 🖼️ 9张背景图生成（需 OpenClaw MCP batch_image_to_video）..."
# 注意：这里无法直接调用 MCP，需要通过 OpenClaw agent 触发
# 提示：如果 OpenClaw 可用，在 OpenClaw 窗口执行以下命令：
#   使用 batch_image_to_video 生成 slide 图片...
echo "📌 背景图生成需要在 OpenClaw 中手动触发，或配置 agent 任务"

# ── Step 4: Whisper 字幕（如启用）─────────────────────────────────────────
if [[ $SKIP_WHISPER -eq 0 ]]; then
  echo ""
  echo "[Step 4/5] 🎤 Whisper 字幕生成..."
  if [[ -f "$SCRIPT_DIR/video/final_with_audio.mp4" ]]; then
    python3 "$SCRIPT_DIR/video/whisper_subtitle.py" \
      --input "$SCRIPT_DIR/video/final_with_audio.mp4" \
      --output "$SCRIPT_DIR/video/${TOPIC_SLUG}_${TIMESTAMP}.srt" \
      --language zh \
      --method auto \
      2>&1 || echo "⚠️ Whisper 字幕失败，继续执行"
  else
    echo "⚠️ 未找到带音频视频，跳过 Whisper 字幕"
  fi
else
  echo ""
  echo "[Step 4/5] ⏭️ Whisper 字幕已跳过"
fi

# ── Step 5: 视频拼接 + 交叉淡化 ────────────────────────────────────────────
echo ""
echo "[Step 5/5] 🎬 视频拼接..."
VIDEO_FILES=($SCRIPT_DIR/video/slide_*.mp4)

if [[ ${#VIDEO_FILES[@]} -gt 1 && -f "$SCRIPT_DIR/video/video_transitions.py" && $SKIP_TRANSITION -eq 0 ]]; then
  echo "使用交叉淡化过渡拼接 ${#VIDEO_FILES[@]} 个片段..."
  python3 "$SCRIPT_DIR/video/video_transitions.py" \
    --inputs "${VIDEO_FILES[@]}" \
    --output "$SCRIPT_DIR/video/final_${TOPIC_SLUG}_${TIMESTAMP}.mp4" \
    --duration 0.5 \
    2>&1 || echo "⚠️ 过渡拼接失败，使用普通拼接..."
fi

# Fallback：纯 Python 拼接
if [[ ${#VIDEO_FILES[@]} -gt 1 ]]; then
  python3 "$SCRIPT_DIR/video/video_transitions.py" \
    --inputs "${VIDEO_FILES[@]}" \
    --output "$SCRIPT_DIR/video/final_${TOPIC_SLUG}_${TIMESTAMP}.mp4" \
    --no-transition \
    2>&1 || echo "⚠️ 视频拼接失败"
fi

# ── 推送 GitHub ────────────────────────────────────────────────────────────
echo ""
echo "[Push] 📤 推送到 GitHub..."
cd "$SCRIPT_DIR"
git add video/ slides/ audio/ content/ 2>/dev/null || true

if git diff --staged --quiet 2>/dev/null; then
  echo "没有新文件需要推送"
else
  git commit -m "🤖 Auto generate $TOPIC $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
  git push origin main 2>&1 || echo "⚠️ GitHub 推送失败（请检查凭证）"
fi

# ── 完成 ────────────────────────────────────────────────────────────────────
FINAL_VIDEO="$SCRIPT_DIR/video/final_${TOPIC_SLUG}_${TIMESTAMP}.mp4"
echo ""
echo "=============================================="
echo "✅ video-auto 流水线执行完成"
echo "  主题: $TOPIC"
echo "  最终视频: $FINAL_VIDEO"
echo "  SRT字幕: $SCRIPT_DIR/video/${TOPIC_SLUG}_${TIMESTAMP}.srt"
echo "  时间戳: $TIMESTAMP"
echo "=============================================="
