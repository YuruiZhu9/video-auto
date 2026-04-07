# 字节跳动 Vidi2 / Vidi2.5 多模态视频理解模型

> 🤖 视频解析方法总结Agent（小M）
> 📅 更新日期：2026-04-02
> 📁 文档路径：`/workspace/reports/video-parser/通用工具/Vidi2-Vidi2.5视频理解模型解析.md`

---

## 核心工具/API

- **Vidi2（Vidi2.5）**：字节跳动开源的 120 亿参数多模态视频理解大模型
  - 官网：https://www.vidi2.app/zh
  - GitHub：https://bytedance.github.io/vidi-website/
  - 参数量：约 1200 亿参数
  - 支持：视频/图像/文本统一输入
  - 特点：分解注意力机制降低计算复杂度，支持数小时长视频

- **Vidi2 核心 API**：
  - 多模态时间检索（TR）：给定文本查询，精确定位视频中对应时间段
  - 时空定位（STG）：在视频中定位特定物体/人物出现的空间位置
  - 视频问答（Video QA）：对视频内容进行自由形式问答
  - 智能剪辑：根据指令自动生成剪辑脚本和叙事结构

- **Vidi2.5 升级**（2025 年底/2026 年初）：
  - 强化学习训练后 STG 能力显著提升
  - 新增 Vidi2.5-Think 推理模型，支持深度思考链

---

## 步骤流程

### 方式一：在线体验（Vidi2 官网）

```
Step 1 → 访问 https://www.vidi2.app/zh
Step 2 → 上传本地视频或粘贴 URL
Step 3 → 选择任务类型（TR/STG/Video QA）
Step 4 → 输入文本查询（如"产品展示部分在第几分钟？"）
Step 5 → 获取结果：时间戳 + 空间标注 + 文字回答
```

### 方式二：本地部署（GitHub 开源）

```
Step 1 → git clone https://github.com/bytedance/vidi
Step 2 → conda create -n vidi python=3.10 && conda activate vidi
Step 3 → pip install -r requirements.txt
Step 4 → 下载预训练权重（需要申请）
Step 5 → python inference.py --video_path "demo.mp4" --task "qa"
Step 6 → 查看输出结果（JSON 格式，含时间戳和回答）
```

### 方式三：API 集成（剪映/Jianying 插件）

```
Step 1 → 剪映专业版接入 Vidi2 API
Step 2 → 上传原始素材（支持数小时长）
Step 3 → AI 自动生成完整剪辑脚本和叙事结构
Step 4 → 一键应用到剪辑时间线
```

---

## 适用场景

- **开源项目演示**：Vidi2 可精确定位演示中的关键代码片段时间段（如"功能演示在第2分30秒"）
- **技术教程深度理解**：问答式查询（如"这个参数的作用是什么？"），无需完整观看
- **产品发布会分析**：快速定位某个功能介绍的时间点，提取关键卖点
- **直播回放切分**：自动将长直播分解为不同话题段落
- **视频素材管理**：通过文本搜索快速找到素材库中的特定镜头
- **自动剪辑**：根据脚本描述自动生成剪辑版本，适用于视频再创作

---

## 避坑指南

- **申请权重较慢**：字节跳动模型权重需要申请，审核周期约 1-2 周，建议提前申请
- **显存要求高**：120B 参数模型推理需要 80GB+ 显存，建议使用 A100 或 H100
- **长视频分段处理**：虽然模型支持数小时视频，但建议超过 2 小时先粗切分以提高定位精度
- **时空定位精度**：Vidi2.5 比 Vidi2 在 STG 任务上有明显提升，有条件优先使用 2.5 版本
- **中文理解弱于英文**：对中文技术术语的理解偶有偏差，建议用英文描述或双语对照查询
- **API 费用**：在线 API 为付费服务，高频使用建议本地部署

---

## 参考链接

- Vidi2 官网：https://www.vidi2.app/zh
- Vidi2.5 官方页面：https://bytedance.github.io/vidi-website/
- GitHub：https://github.com/bytedance/vidi
- 知乎解读：https://zhuanlan.zhihu.com/p/1983672899572369263
- CSDN 实战教程：https://blog.csdn.net/Code1994/article/details/155821261
- 腾讯新闻报道：https://news.qq.com/rain/a/20251204A04KXG00

---

## 与 OpenClaw 集成建议

Vidi2 可作为 `videos_understand` 的补充工具，尤其适合：
1. **精确定位**（`videos_understand` 提供语义理解，Vidi2 提供时间戳精确定位）
2. **长视频切片**（Vidi2 分析全局结构，`videos_understand` 分析局部内容）
3. **自动化剪辑**（Vidi2 生成剪辑脚本，`FFmpeg` 执行实际剪辑）

```
集成示例：
1. videos_understand → 整体理解 + 知识点列表
2. Vidi2(TR) → 精确定位每个知识点的起止时间
3. FFmpeg → 按时间戳分段输出独立片段
4. images_understand → 逐段关键帧分析
```
