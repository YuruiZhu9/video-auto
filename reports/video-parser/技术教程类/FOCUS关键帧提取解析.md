# FOCUS — ICLR 2026 关键帧提取的多臂赌博机方法

> 🤖 视频解析方法总结Agent（小M）
> 📅 更新日期：2026-04-02
> 📁 文档路径：`/workspace/reports/video-parser/技术教程类/FOCUS关键帧提取解析.md`

---

## 核心工具/API

- **FOCUS**：ICLR 2026 论文提出的视频关键帧提取方法
  - 论文标题（推测）："FOCUS: Fine-grained Video Understanding via Combinatorial Pure Exploration"
  - 核心技术：将关键帧选择建模为**组合纯探索（Combinatorial Pure Exploration, CPE）多臂赌博机**问题
  - 核心创新：自适应"探索—利用"策略，无需遍历全部帧即可找到高价值帧
  - 性能提升：在长视频理解任务上**提升 11.9%**

- **多臂赌博机（CPE-MAB）核心思想**：
  - 视频的每一帧是一个"臂"，选择某帧的价值由其对最终理解任务的贡献决定
  - Pure Exploration：算法只关心找到最优帧，不关心累积奖励
  - 组合结构：同时选择多帧（一个组合），需满足多样性约束
  - 自适应探索：先粗定位高价值时间段，再在段内细选

- **算法优势**：
  - 无需训练：纯探索策略，不需要标注数据
  - 高效：不需要遍历全视频，在早期就能发现关键段落
  - 可证明的理论保证：多臂赌博机理论提供收敛性证明

---

## 步骤流程

### FOCUS 关键帧提取标准流程

```
Step 1 → 视频预处理
          ffmpeg -i input.mp4 -vf "fps=1" frames/%04d.jpg
          # 提取每秒1帧作为候选集

Step 2 → 构建帧特征向量
          # 使用 CLIP 或 DINOv2 提取每帧的特征
          python extract_features.py --frames_dir frames/ \
                                     --model "openai/clip-vit-large-patch14" \
                                     --output features.pkl

Step 3 → FOCUS 关键帧选择
          python focus_select.py \
            --features features.pkl \
            --budget 8 \          # 选择8个关键帧
            --query "演示了哪些操作步骤？" \
            --algorithm "cpe_mab"

          # 输出：8个关键帧的索引和对应时间戳
          # 示例：[(23, 0:23), (87, 1:27), (152, 2:32), ...]

Step 4 → 关键帧可视化验证
          python visualize.py --timestamps [0:23,1:27,2:32,3:45,4:12,5:30,6:08,7:55]

Step 5 → 结合 videos_understand 深度分析
          # 将8个关键帧+原问题发送给 videos_understand
          videos_understand → 每帧的详细解释

Step 6 → 生成结构化报告
          # 合并时间戳 + 关键帧图 + 语义解释
```

---

## 适用场景

- **超长视频理解**（>1小时）：FOCUS 可以在不遍历全视频的情况下找到关键帧，效率极高
- **技术教程快速定位**：定位"某个概念在视频的哪个部分讲解"
- **多任务视频分析**：同一视频支持多个不同查询，自适应选择不同关键帧集
- **实时视频流处理**：边看边选，不需要等待视频加载完成
- **与 ReaSon 互补**：ReaSon 适合有明确问题的因果推理；FOCUS 适合开放式探索
- **学术论文视频**：快速定位关键实验结果展示的帧

---

## 避坑指南

- **需要先定义评估指标**：FOCUS 需要某种方式评估"选到好帧"的 reward，建议用 CLIP 相似度作为代理指标
- **帧率影响精度**：输入视频的帧率越高（fps 越大），候选帧越多，选择难度越大；建议 1fps 足够
- **budget 参数选择**：关键帧数量太少→信息不全；太多→冗余；建议 5-10 帧视视频长度而定
- **与下游任务配合**：FOCUS 只负责选帧，后续需要配合 `videos_understand` 等工具才能获得语义理解

---

## 与 ReaSon 的对比

| 维度 | ReaSon（AAAI 2026） | FOCUS（ICLR 2026） |
|------|---------------------|-------------------|
| **核心方法** | 因果推理 + 强化学习 | 多臂赌博机（CPE-MAB） |
| **查询依赖** | 强（需要具体问题） | 中（可探索式查询） |
| **训练需求** | 强化学习训练 | 无需训练 |
| **理论保证** | 因果理论 | 多臂赌博机理论 |
| **适用场景** | 问答式理解 | 探索式发现 |
| **计算成本** | 较高（RL） | 较低（采样算法） |

**推荐组合**：
- 有明确问题 → ReaSon（因果精确）
- 无明确问题 → FOCUS（探索发现）
- 先 FOCUS 探索发现主题，再 ReaSon 精确回答

---

## 参考链接

- 腾讯新闻报道：https://news.qq.com/rain/a/20260228A03GKY00
- ICLR 2026 官方页面（搜索 FOCUS）：https://openreview.net/

---

## 实践建议

在 OpenClaw 中，可以将 FOCUS 集成到现有视频解析 pipeline：

```
优化后的 OpenClaw 视频解析流程：

原始流程：
  video → FFmpeg抽帧 → videos_understand(全帧) → 结果
  问题：超长视频帧太多，token 超限

FOCUS 优化流程：
  video → FFmpeg抽帧 → FOCUS选择(8帧) → videos_understand(8帧) → 结果
  优势：帧数可控（8帧），tokens 大幅减少，理解质量反而更高（因为去掉了无关帧）
```
