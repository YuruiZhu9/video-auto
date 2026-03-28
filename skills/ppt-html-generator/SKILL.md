# PPT-HTML-Generator Skill

> 根据主题和内容，生成精美网页版 Slide（单 HTML 文件，浏览器直接打开即可演示）

## 触发条件
用户请求生成 PPT/Slide/演示文稿，或者需要将内容转化为网页版幻灯片时使用。

## 输入（由调用 Agent 提供）
- `topic`: 演示主题（字符串）
- `content`: 要展示的核心内容/文稿（字符串，可含多段）
- `style`: 风格偏好（可选，"科技" / "简约" / "商务"，默认"科技"）
- `slides_count`: 幻灯片数量（可选，默认 8 张）

## 输出
- 生成的 HTML 文件保存至 `/workspace/agents/video-auto/slides/output.html`
- 返回文件路径和访问 URL

## 工作流程

### Step 1：分析内容，规划 Slide 结构
将内容拆分为 N 张幻灯片，每张包含：
- 标题（标题醒目，大字体）
- 要点（3-5 条，每条简洁）
- 配色/图标点缀

### Step 2：生成 HTML
生成一个**完整的单文件 HTML**，包含：
- 内嵌 CSS（深色主题 + 渐变背景 + 动画）
- 内嵌 JavaScript（键盘/点击翻页 + 进度条 + 动画）
- 响应式布局（支持手机/电脑）
- 每张 Slide 平滑过渡动画（fade + slide）
- 导航指示器（底部圆点）
- 左右箭头导航 + 键盘支持

### Step 3：质量检查
- 确认所有 Slide 有内容（不空洞）
- 确认无乱码
- 确认导航功能正常

## HTML 设计规范

### 配色方案（科技风）
```css
--bg-primary: #0f0f1a;
--bg-slide: #1a1a2e;
--accent: #6c5ce7;
--accent-light: #a29bfe;
--text-primary: #ffffff;
--text-secondary: #b0b0d0;
--gradient-start: #6c5ce7;
--gradient-end: #00cec9;
```

### 结构要求
- 每张 Slide 居中显示，大标题 3rem+，正文 1.2rem+
- 代码块使用等宽字体 + 深色背景
- 要点使用图标前缀（✅ / 💡 / 🔥 / ⚠️）
- Slide 切换带平滑动画（0.5s ease）
- 底部进度条实时显示当前位置
- 右下角显示"第 X/N 张"

### 交互要求
- 键盘 ← → 翻页
- 点击屏幕左右区域翻页
- 底部圆点可点击跳转
- 按 F 全屏演示

## 示例 Slide 结构
```
Slide 1: 封面（主题 + 副标题 + 日期）
Slide 2: 目录/大纲
Slide 3-N: 内容页（每页一个核心观点）
Slide N+1: 总结
Slide N+2: 感谢/Q&A
```

## 调用示例
```
skill: ppt-html-generator
input:
  topic: "AI时代的推荐系统演进"
  content: "一、协同过滤的局限...\n二、深度学习的突破...\n三、大模型的未来..."
  style: "科技"
  slides_count: 10
```

## 注意事项
- 生成内容要有深度，不能只是列表罗列，要有小段落解释
- 每张 Slide 的文字量控制在 100 字以内（演讲节奏）
- 标题要有吸引力，避免平淡的"第一章"式标题
