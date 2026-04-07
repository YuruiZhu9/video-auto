# -*- coding: utf-8 -*-
"""
Step 2: 生成 HTML Slide
根据 content/2026-04-04.md 生成10张精美网页幻灯片
"""
import os

# 幻灯片数据：10张
slides = [
    {
        "num": 1,
        "type": "cover",
        "title": "2026年AI视频工具最新进展",
        "subtitle": "从可灵到PixVerse V6",
        "tagline": "🤖 科技前沿 · 内容创作 · 工具盘点",
    },
    {
        "num": 2,
        "type": "toc",
        "title": "内容概览",
        "items": [
            ("可灵AI 3.0", "780万月活，全球第一"),
            ("PixVerse V6", "物理真实感最强"),
            ("Veo 3.1 Lite", "Google性价比之王"),
            ("Kokoro-82M", "TTS开源最强"),
        ],
    },
    {
        "num": 3,
        "type": "content",
        "title": "可灵AI 3.0",
        "subtitle": "国产之光 · 全球AI视频工具榜首",
        "icon": "🇨🇳",
        "points": [
            "月活突破780万，超越Sora、Runway Gen-3",
            "运动笔刷全面升级，精准控制任意物体运动",
            "中文语义理解最强，中文prompt契合度最高",
            "分图层运动控制，专业级导演体验",
        ],
    },
    {
        "num": 4,
        "type": "highlight",
        "title": "可灵3.0：核心突破",
        "highlight": "780万",
        "highlight_label": "月活用户",
        "sub": "2026年1月发布3.0版本，彻底改变AI视频格局",
        "points": [
            "✅ 运动笔刷：指挥画面中每个元素的走位",
            "✅ 分图层控制：人物+背景互不干扰",
            "✅ 中文优化：中描景，契合度超越英文",
            "✅ 国产骄傲：快手出品，免费额度充足",
        ],
    },
    {
        "num": 5,
        "type": "content",
        "title": "PixVerse V6",
        "subtitle": "物理真实感的天花板",
        "icon": "🎬",
        "points": [
            "全新物理引擎架构，肢体动作零穿帮",
            "骨骼点实时计算重力与碰撞关系",
            "落地冲击、衣角飞扬等细节真实呈现",
            "镜头运动预设库：希区柯克、斯坦尼康、轨道推进",
        ],
    },
    {
        "num": 6,
        "type": "content",
        "title": "Veo 3.1 Lite",
        "subtitle": "Google出品 · 性价比之王",
        "icon": "🔍",
        "points": [
            "API价格仅为Veo 3.0的30%，成本降低70%",
            "单次最长60秒连续视频，超越市场30秒上限",
            "人物角色一致性极高，不中途换脸",
            "与YouTube Studio深度整合，一站式创作",
        ],
    },
    {
        "num": 7,
        "type": "content",
        "title": "Kokoro-82M",
        "subtitle": "TTS开源最强黑马 · 声音逼近真人",
        "icon": "🎙️",
        "points": [
            "82M参数，超越百亿参数模型的声音自然度",
            "情感控制层：兴奋、悲伤、平静、调侃自动调整",
            "完全开源：免费商用、本地部署、数据不上传",
            "打破TTS领域商业垄断，隐私友好",
        ],
    },
    {
        "num": 8,
        "type": "compare",
        "title": "2026年AI视频工具全景对比",
        "items": [
            ("可灵AI 3.0", "🇨🇳 快手", "780万月活", "★★★★★", "中文最强"),
            ("PixVerse V6", "🇺🇸 PixVerse", "物理真实感", "★★★★★", "肢体动作"),
            ("Veo 3.1 Lite", "🏷️ Google", "性价比最高", "★★★★☆", "超长视频"),
            ("Kokoro-82M", "🟢 开源", "82M参数", "★★★★★", "情感TTS"),
        ],
    },
    {
        "num": 9,
        "type": "content",
        "title": "趋势与展望",
        "subtitle": "AI视频工具民主化革命正在进行",
        "icon": "🔮",
        "points": [
            "2026年：AI视频工具进入爆发期，质量大幅提升",
            "门槛降低：一个人+一台电脑=专业级视频",
            "未来1-2年：门槛进一步降低，创意成为唯一瓶颈",
            "真正限制你的，不再是工具，而是你的创意",
        ],
    },
    {
        "num": 10,
        "type": "end",
        "title": "感谢观看",
        "subtitle": "我们下期见！",
        "tagline": "🤖 我是小M · AI工具爱好者 · 持续关注AIGC前沿",
    },
]

# 生成HTML
html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026年AI视频工具最新进展</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --bg: #0a0a1a;
    --card: #12122a;
    --accent: #6c5ce7;
    --accent2: #00cec9;
    --accent3: #fd79a8;
    --text: #ffffff;
    --text2: #b0b8d0;
    --gradient: linear-gradient(135deg, #6c5ce7 0%, #00cec9 100%);
  }
  body {
    font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
    background: var(--bg);
    color: var(--text);
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }

  /* ── 幻灯片 ── */
  .slides { width: 100%; height: 100vh; position: relative; }

  .slide {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 60px 80px;
    opacity: 0;
    transform: translateX(100%);
    transition: opacity 0.5s ease, transform 0.5s ease;
    pointer-events: none;
    background: var(--bg);
  }
  .slide.active {
    opacity: 1;
    transform: translateX(0);
    pointer-events: auto;
  }
  .slide.exit-left {
    opacity: 0;
    transform: translateX(-100%);
  }

  /* 装饰圆 */
  .slide::before {
    content: '';
    position: absolute;
    width: 600px; height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(108,92,231,0.15) 0%, transparent 70%);
    top: -200px; right: -200px;
    pointer-events: none;
  }
  .slide::after {
    content: '';
    position: absolute;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,206,201,0.1) 0%, transparent 70%);
    bottom: -100px; left: -100px;
    pointer-events: none;
  }

  /* ── 封面 ── */
  .slide-cover {
    text-align: center;
  }
  .slide-cover .tagline {
    font-size: 0.9rem;
    color: var(--accent2);
    letter-spacing: 3px;
    margin-bottom: 30px;
    text-transform: uppercase;
  }
  .slide-cover h1 {
    font-size: 3.8rem;
    font-weight: 800;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
    line-height: 1.2;
  }
  .slide-cover .subtitle {
    font-size: 2rem;
    color: var(--text2);
    font-weight: 300;
    margin-bottom: 40px;
  }
  .slide-cover .date {
    font-size: 0.9rem;
    color: var(--accent);
    letter-spacing: 2px;
  }
  .cover-icon {
    font-size: 5rem;
    margin-bottom: 20px;
    display: block;
  }

  /* ── 目录 ── */
  .slide-toc { }
  .slide-toc h2 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 50px;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .toc-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    width: 100%;
    max-width: 900px;
  }
  .toc-item {
    background: var(--card);
    border-radius: 16px;
    padding: 24px 28px;
    border-left: 4px solid var(--accent);
    transition: transform 0.3s, box-shadow 0.3s;
  }
  .toc-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 40px rgba(108,92,231,0.3);
  }
  .toc-item h3 { font-size: 1.3rem; color: var(--text); margin-bottom: 6px; }
  .toc-item p { font-size: 0.9rem; color: var(--text2); }

  /* ── 内容页 ── */
  .slide-content { width: 100%; }
  .slide-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 40px;
  }
  .slide-icon { font-size: 3rem; }
  .slide-header h2 {
    font-size: 2.6rem;
    font-weight: 800;
    color: var(--text);
  }
  .slide-header .sub {
    font-size: 1.1rem;
    color: var(--accent2);
    margin-top: 4px;
  }
  .points {
    display: flex;
    flex-direction: column;
    gap: 18px;
    max-width: 900px;
  }
  .point {
    background: var(--card);
    border-radius: 14px;
    padding: 18px 24px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    font-size: 1.1rem;
    line-height: 1.6;
    transition: transform 0.2s;
    border: 1px solid rgba(108,92,231,0.2);
  }
  .point:hover { transform: translateX(8px); border-color: rgba(108,92,231,0.5); }
  .point-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }
  .point span { color: var(--text2); }

  /* ── 高亮页 ── */
  .slide-highlight { text-align: center; }
  .highlight-num {
    font-size: 8rem;
    font-weight: 900;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
  }
  .highlight-label {
    font-size: 1.8rem;
    color: var(--text2);
    margin-bottom: 20px;
  }
  .highlight-sub {
    font-size: 1.1rem;
    color: var(--accent2);
    margin-bottom: 50px;
    max-width: 700px;
  }

  /* ── 对比表 ── */
  .compare-table {
    width: 100%;
    max-width: 960px;
    border-collapse: separate;
    border-spacing: 0 10px;
  }
  .compare-table th {
    text-align: left;
    padding: 12px 20px;
    color: var(--accent2);
    font-size: 0.85rem;
    letter-spacing: 1px;
    border-bottom: 2px solid rgba(0,206,201,0.3);
  }
  .compare-table td {
    background: var(--card);
    padding: 16px 20px;
    border-radius: 0;
    font-size: 1rem;
  }
  .compare-table tr td:first-child { border-radius: 10px 0 0 10px; }
  .compare-table tr td:last-child { border-radius: 0 10px 10px 0; }
  .compare-table tr:hover td { background: rgba(108,92,231,0.15); }
  .stars { color: #f9ca24; letter-spacing: 1px; }
  .brand-tag {
    display: inline-block;
    background: rgba(108,92,231,0.3);
    color: var(--accent);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
  }

  /* ── 结尾 ── */
  .slide-end { text-align: center; }
  .slide-end .big-icon { font-size: 6rem; margin-bottom: 20px; display: block; }
  .slide-end h2 {
    font-size: 4rem;
    font-weight: 900;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
  }
  .slide-end .subtitle { font-size: 2rem; color: var(--accent2); margin-bottom: 40px; }
  .slide-end .tagline { font-size: 0.9rem; color: var(--text2); }

  /* ── 导航 ── */
  .nav {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
    z-index: 100;
  }
  .dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: rgba(255,255,255,0.3);
    cursor: pointer;
    transition: all 0.3s;
  }
  .dot.active { background: var(--accent2); width: 30px; border-radius: 5px; }
  .dot:hover { background: var(--accent); }

  .progress {
    position: fixed;
    bottom: 0; left: 0;
    height: 3px;
    background: var(--gradient);
    transition: width 0.3s;
    z-index: 100;
  }

  .page-num {
    position: fixed;
    bottom: 28px;
    right: 40px;
    font-size: 0.85rem;
    color: var(--text2);
    z-index: 100;
  }

  .nav-arrows {
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
    z-index: 100;
    pointer-events: none;
  }
  .arrow {
    width: 50px; height: 50px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    cursor: pointer;
    transition: all 0.3s;
    pointer-events: auto;
    color: var(--text);
    backdrop-filter: blur(10px);
  }
  .arrow:hover { background: rgba(108,92,231,0.5); border-color: var(--accent); }

  /* 动画入场 */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .slide.active .animate { animation: fadeUp 0.6s ease forwards; }
  .slide.active .animate:nth-child(1) { animation-delay: 0.1s; }
  .slide.active .animate:nth-child(2) { animation-delay: 0.2s; }
  .slide.active .animate:nth-child(3) { animation-delay: 0.3s; }
  .slide.active .animate:nth-child(4) { animation-delay: 0.4s; }
  .slide.active .animate:nth-child(5) { animation-delay: 0.5s; }

  .animate { opacity: 0; }
</style>
</head>
<body>

<div class="slides" id="slides">

"""

# 按类型生成各幻灯片
for i, sl in enumerate(slides):
    active_class = "active" if i == 0 else ""
    html += f'  <div class="slide slide-{sl["type"]} {active_class}" id="slide-{sl["num"]}">\n'

    if sl["type"] == "cover":
        html += f'''    <span class="cover-icon">🎬</span>
    <p class="tagline">{sl["tagline"]}</p>
    <h1 class="animate">{sl["title"]}</h1>
    <p class="subtitle animate">{sl["subtitle"]}</p>
    <p class="date animate">2026年4月 · AI前沿工具盘点</p>
'''

    elif sl["type"] == "toc":
        html += '    <h2 class="animate">📋 内容概览</h2>\n'
        html += '    <div class="toc-grid">\n'
        for j, (name, desc) in enumerate(sl["items"]):
            emoji = ["🇨🇳", "🎬", "🔍", "🎙️"][j]
            html += f'''      <div class="toc-item animate">
        <h3>{emoji} {name}</h3>
        <p>{desc}</p>
      </div>
'''
        html += '    </div>\n'

    elif sl["type"] == "content":
        html += f'''    <div class="slide-content">
      <div class="slide-header animate">
        <span class="slide-icon">{sl["icon"]}</span>
        <div>
          <h2>{sl["title"]}</h2>
          <p class="sub">{sl["subtitle"]}</p>
        </div>
      </div>
      <div class="points">
'''
        for pt in sl["points"]:
            html += f'        <div class="point animate"><span class="point-icon">▸</span>{pt}</div>\n'
        html += '      </div>\n    </div>\n'

    elif sl["type"] == "highlight":
        html += f'''    <div class="slide-highlight">
      <p class="animate">{sl["title"]}</p>
      <div class="highlight-num animate">{sl["highlight"]}</div>
      <div class="highlight-label animate">{sl["highlight_label"]}</div>
      <p class="highlight-sub animate">{sl["sub"]}</p>
      <div class="points">
'''
        for pt in sl["points"]:
            html += f'        <div class="point animate"><span class="point-icon">★</span>{pt}</div>\n'
        html += '      </div>\n    </div>\n'

    elif sl["type"] == "compare":
        html += f'''    <h2 class="animate" style="font-size:2.2rem;margin-bottom:30px;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📊 {sl["title"]}</h2>
    <table class="compare-table animate">
      <thead>
        <tr>
          <th>工具</th><th>厂商</th><th>核心优势</th><th>评分</th><th>亮点</th>
        </tr>
      </thead>
      <tbody>
'''
        for row in sl["items"]:
            name, brand, feat, stars, tag = row
            html += f'''        <tr>
          <td><strong>{name}</strong></td>
          <td><span class="brand-tag">{brand}</span></td>
          <td>{feat}</td>
          <td><span class="stars">{stars}</span></td>
          <td>{tag}</td>
        </tr>
'''
        html += '      </tbody>\n    </table>\n'

    elif sl["type"] == "end":
        html += f'''    <span class="big-icon animate">👋</span>
    <h2 class="animate">{sl["title"]}</h2>
    <p class="subtitle animate">{sl["subtitle"]}</p>
    <p class="tagline animate">{sl["tagline"]}</p>
'''

    html += '  </div>\n\n'

html += """</div>

<!-- 导航 -->
<div class="nav-arrows">
  <div class="arrow" id="prev">‹</div>
  <div class="arrow" id="next">›</div>
</div>
<div class="nav" id="nav"></div>
<div class="progress" id="progress"></div>
<div class="page-num" id="pageNum">1 / 10</div>

<script>
  const total = 10;
  let cur = 0;
  const slides = document.querySelectorAll('.slide');
  const nav = document.getElementById('nav');
  const progress = document.getElementById('progress');
  const pageNum = document.getElementById('pageNum');

  // 生成导航点
  for (let i = 0; i < total; i++) {
    const d = document.createElement('div');
    d.className = 'dot' + (i === 0 ? ' active' : '');
    d.onclick = () => goTo(i);
    nav.appendChild(d);
  }

  function goTo(idx) {
    if (idx < 0 || idx >= total) return;
    slides[cur].classList.remove('active');
    slides[cur].classList.add('exit-left');
    setTimeout(() => slides[cur < idx ? cur : idx]?.classList.remove('exit-left'), 500);
    cur = idx;
    slides[cur].classList.add('active');
    document.querySelectorAll('.dot').forEach((d, i) => {
      d.classList.toggle('active', i === cur);
    });
    progress.style.width = ((cur + 1) / total * 100) + '%';
    pageNum.textContent = (cur + 1) + ' / ' + total;
  }

  function next() { goTo((cur + 1) % total); }
  function prev() { goTo((cur - 1 + total) % total); }

  document.getElementById('next').onclick = next;
  document.getElementById('prev').onclick = prev;

  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') next();
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') prev();
    if (e.key === 'f' || e.key === 'F') {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen();
      else document.exitFullscreen();
    }
  });

  // 点击屏幕跳转
  document.addEventListener('click', e => {
    if (e.target.closest('.dot') || e.target.closest('.arrow')) return;
    const x = e.clientX / window.innerWidth;
    if (x < 0.3) prev();
    else if (x > 0.7) next();
  });

  // 触摸滑动
  let touchX = 0;
  document.addEventListener('touchstart', e => { touchX = e.touches[0].clientX; });
  document.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) { dx < 0 ? next() : prev(); }
  });
</script>
</body>
</html>
"""

out_path = "/workspace/agents/video-auto/slides/2026-04-04.html"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(out_path)
print(f"✅ HTML Slide 生成完成")
print(f"📄 文件：{out_path} ({size} bytes)")
print(f"📊 共 {len(slides)} 张幻灯片")
