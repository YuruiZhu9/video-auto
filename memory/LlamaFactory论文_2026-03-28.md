# LlamaFactory 每日论文资源

**抓取时间**：2026-03-28  
**来源**：[https://llamafactory.cn/daily-paper/](https://llamafactory.cn/daily-paper/)  
**API来源**：api.llamafactory.cn/paper/list

---

## 📅 近期推荐论文（按发布日期排序）

---

### 1. PMT: Plain Mask Transformer for Image and Video Segmentation with Frozen Vision Encoders

- **arXiv ID**：2603.25398
- **日期**：2026-03-27
- **作者**：Niccolò Cavagnero, Narges Norouzi, Gijs Dubbelman, Daan de Geus
- **分类**：计算机视觉 | 机器学习
- **难度**：⭐⭐（中等）
- **关键词**：Vision Foundation Models, Plain Mask Transformer
- **一句话摘要**：该论文提出了Plain Mask Transformer (PMT)，一种基于Transformer的快速图像和视频分割解码器，它能够在保持冻结的Vision Foundation Model (VFM)编码器的同时，实现高效和准确的分割。
- **要点**：
  - ✅ 在冻结VFM编码器条件下实现快速分割
  - ✅ 兼顾效率和准确性
  - ✅ 同时支持图像和视频分割
- **论文链接**：https://arxiv.org/abs/2603.25398

---

### 2. Voxtral TTS

- **arXiv ID**：2603.25551
- **日期**：2026-03-27
- **作者**：Alexander H. Liu, Guillaume Lample, Patrick von Platen 等（共200+位作者，Meta团队）
- **分类**：计算机视觉 | 自然语言处理 | 机器学习
- **难度**：⭐⭐⭐（较难）
- **关键词**：multilingual, hybrid architecture, flow-matching, Voxtral Codec, voice cloning, text-to-speech
- **一句话摘要**：Voxtral TTS 是一种能够从3秒的参考音频中生成自然语音的多语言文本到语音模型，其混合架构结合了语义语音标记的自动回归生成和声学标记的流匹配，显著提升了语音的自然性和表现力。
- **要点**：
  - ✅ 仅需3秒参考音频即可克隆声音
  - ✅ 多语言支持
  - ✅ 混合架构：自回归 + 流匹配
  - ✅ Meta团队发布，性能领先
- **论文链接**：https://arxiv.org/abs/2603.25551

---

### 3. MuRF: Unlocking the Multi-Scale Potential of Vision Foundation Models

- **arXiv ID**：2603.25744
- **日期**：2026-03-27
- **作者**：Bocheng Zou, Mu Cai, Mark Stanley, Dingfu Lu, Yong Jae Lee
- **分类**：计算机视觉 | 机器学习
- **难度**：⭐⭐（中等）
- **关键词**：Vision Foundation Models, Multi-Resolution Fusion
- **一句话摘要**：MuRF通过在推理时融合不同分辨率的特征，为视觉基础模型提供了一种简单而有效的多尺度视觉表示方法。
- **要点**：
  - ✅ 推理时融合多分辨率特征
  - ✅ 无需额外训练
  - ✅ 提升VFM多尺度表示能力
- **论文链接**：https://arxiv.org/abs/2603.25744

---

### 4. Less Gaussians, Texture More: 4K Feed-Forward Textured Splatting（LGTM）

- **arXiv ID**：2603.25745
- **日期**：2026-03-27
- **作者**：Yixing Lao, Xuyang Bai, Xiaoyang Wu 等
- **分类**：计算机视觉 | 机器学习
- **难度**：⭐⭐⭐（较难）
- **关键词**：feed-forward, textured Gaussian splatting
- **一句话摘要**：LGTM通过预测紧凑的Gaussian基元和每个基元的纹理，实现了无需场景优化的4K高保真新视图合成，显著减少了基元数量，并克服了先前工作的分辨率限制。
- **要点**：
  - ✅ 前馈式（无需场景优化）
  - ✅ 4K高保真新视图合成
  - ✅ 显著减少基元数量，提升效率
  - ✅ 突破分辨率限制
- **论文链接**：https://arxiv.org/abs/2603.25745

---

### 5. ABot-PhysWorld: Interactive World Foundation Model for Robotic Manipulation with Physics Alignment

- **arXiv ID**：2603.23376
- **日期**：2026-03-25
- **作者**：Yuzhi Chen, Ronghan Chen, Dongjie Huo 等
- **分类**：计算机视觉 | 机器人
- **难度**：⭐⭐⭐（较难）
- **关键词**：Diffusion Transformer, World Foundation Model, Robotic Manipulation
- **一句话摘要**：本文提出了一种名为ABot-PhysWorld的交互式世界基础模型，用于机器人操作，该模型能够生成视觉真实、物理合理且可控的视频。
- **要点**：
  - ✅ 生成视觉真实、物理合理的视频
  - ✅ 面向机器人操作任务
  - ✅ 结合Diffusion Transformer架构
- **论文链接**：https://arxiv.org/abs/2603.23376

---

### 6. SIMART: Decomposing Monolithic Meshes into Sim-ready Articulated Assets via MLLM

- **arXiv ID**：2603.23386
- **日期**：2026-03-25
- **作者**：Chuanrui Zhang, Minghan Qin, Yuang Wang 等
- **分类**：计算机视觉 | 机器学习
- **难度**：⭐⭐⭐（较难）
- **关键词**：kinematic prediction, 3D VQ-VAE, MLLM
- **一句话摘要**：SIMART提出了一种基于统一的多模态语言模型（MLLM）框架，通过稀疏3D VQ-VAE和精确的动力学参数预测，将静态3D网格转换为功能性的、可模拟的关节资产。
- **要点**：
  - ✅ MLLM框架统一处理
  - ✅ 稀疏3D VQ-VAE编码
  - ✅ 精确动力学参数预测
  - ✅ 静态→可模拟关节资产
- **论文链接**：https://arxiv.org/abs/2603.23386

---

### 7. RealMaster: Lifting Rendered Scenes into Photorealistic Video

- **arXiv ID**：2603.23462
- **日期**：2026-03-25
- **作者**：Dana Cohen-Bar, Ido Sobol, Oran Gafni 等
- **分类**：计算机视觉 | 机器学习
- **难度**：⭐⭐⭐（较难）
- **关键词**：photorealistic video, IC-LoRA, rendered video, sim-to-real translation, video diffusion models
- **一句话摘要**：RealMaster通过结合视频扩散模型和3D引擎的精确控制，将渲染视频转换为具有真实感的视频，同时保持场景结构和动态。
- **要点**：
  - ✅ 渲染视频→真实感视频
  - ✅ 结合视频扩散模型 + 3D引擎
  - ✅ 保持场景结构和动态
  - ✅ IC-LoRA控制机制
- **论文链接**：https://arxiv.org/abs/2603.23462

---

### 8. daVinci-MagiHuman: Speed by Simplicity - A Single-Stream Architecture for Fast Audio-Video Generative Foundation Model

- **arXiv ID**：2603.21986
- **日期**：2026-03-24
- **作者**：SII-GAIR, Sand.ai, Pengfei Liu 等
- **分类**：计算机视觉 | 多模态 | 机器学习
- **难度**：⭐⭐⭐（较难）
- **关键词**：single-stream Transformer, multilingual support, audio-video generation
- **一句话摘要**：该论文提出了daVinci-MagiHuman，一个基于单流Transformer的音频-视频生成基础模型，它通过简化架构同时保持了生成质量和推理效率。
- **要点**：
  - ✅ 单流Transformer架构（简化设计）
  - ✅ 音频+视频联合生成
  - ✅ 兼顾质量和推理效率
  - ✅ 多语言支持
- **论文链接**：https://arxiv.org/abs/2603.21986

---

### 9. Memento-Skills: Let Agents Design Agents

- **arXiv ID**：2603.18743
- **日期**：2026-03-20
- **作者**：Huichi Zhou, Siyuan Guo, Anjie Liu 等
- **分类**：自然语言处理 | 机器学习
- **难度**：⭐⭐⭐（较难）
- **关键词**：offline RL, skill library, agent design
- **一句话摘要**：Memento-Skills提出了一种基于记忆的强化学习框架，通过自主构建、适应和改进任务特定代理，实现了持续学习，并在通用人工智能助手和人类最后考试基准测试中取得了显著的性能提升。
- **要点**：
  - ✅ 记忆驱动的RL框架
  - ✅ Agent自主设计Agent
  - ✅ 持续学习能力
  - ✅ 显著超越基线性能
- **论文链接**：https://arxiv.org/abs/2603.18743

---

### 10. ProRL Agent: Rollout-as-a-Service for RL Training of Multi-Turn LLM Agents

- **arXiv ID**：2603.18815
- **日期**：2026-03-20
- **作者**：Hao Zhang, Mingjie Liu, Yi Dong 等
- **分类**：自然语言处理 | 机器学习
- **难度**：⭐⭐⭐（较难）
- **关键词**：ProRL Agent, Rollout-as-a-Service, RL training
- **一句话摘要**：ProRL Agent 提出了一种基于"Rollout-as-a-Service"的 scalable infrastructure，用于多轮语言模型智能体在强化学习中的训练，通过解耦训练和 rollout 流程，提高了资源利用率和系统可维护性。
- **要点**：
  - ✅ Rollout-as-a-Service架构
  - ✅ 解耦训练和推理流程
  - ✅ 提高RL训练资源利用率
  - ✅ 面向多轮对话Agent
- **论文链接**：https://arxiv.org/abs/2603.18815

---

### 11. Matryoshka Gaussian Splatting

- **arXiv ID**：2603.19234
- **日期**：2026-03-20
- **作者**：Zhilin Guo, Boqiao Zhang, Cengiz Oztireli 等
- **分类**：计算机视觉 | 机器学习
- **难度**：⭐⭐（中等）
- **关键词**：3D Gaussian splatting, continuous level of detail, budgeted rendering, nested representations
- **一句话摘要**：Matryoshka Gaussian Splatting (MGS) 提出了一种新的训练框架，使得 3D Gaussian Splatting (3DGS) 能够实现连续的细节级别控制，同时保持全能力渲染质量。
- **要点**：
  - ✅ 3DGS连续LOD控制
  - ✅ 嵌套表示（俄罗斯套娃结构）
  - ✅ 随机训练策略
  - ✅ 保持高质量渲染
- **论文链接**：https://arxiv.org/abs/2603.19234

---

## 📊 论文主题分布

| 类别 | 数量 | 代表论文 |
|------|------|---------|
| 计算机视觉 | 9 | PMT, MuRF, LGTM, RealMaster |
| 多模态 | 1 | daVinci-MagiHuman |
| 自然语言处理 | 4 | Memento-Skills, ProRL Agent, OEL |
| 机器人 | 1 | ABot-PhysWorld |
| 机器学习（综合） | 11 | 以上全部 |

---

## 🔥 重点关注

### 最值得关注（强烈推荐）

1. **Voxtral TTS**（⭐⭐⭐）— Meta多语言TTS，支持3秒克隆，声音自然度高，大厂出品值得关注
2. **daVinci-MagiHuman**（⭐⭐⭐）— 单流音视频生成模型，效率与质量兼顾
3. **Memento-Skills**（⭐⭐⭐）— Agent设计Agent，持续学习框架，AI Agent方向前沿
4. **ProRL Agent**（⭐⭐⭐）— 多轮Agent的RL训练基础设施，工程价值高
5. **LGTM**（⭐⭐⭐）— 4K前馈式Gaussian Splatting，3D视觉前沿

### 推荐入门（难度适中）

1. **PMT**（⭐⭐）— 视觉基础模型 + 图像/视频分割，清晰简洁
2. **MuRF**（⭐⭐）— 多尺度VFM表示，推理友好
3. **Matryoshka GS**（⭐⭐）— 3DGS LOD控制，清晰易读

---

## 📚 完整论文列表（第一批共10篇）

| # | 论文标题 | 领域 | 难度 | 日期 |
|---|---------|------|------|------|
| 1 | PMT: Plain Mask Transformer | CV | ⭐⭐ | 03-27 |
| 2 | Voxtral TTS | NLP/Audio | ⭐⭐⭐ | 03-27 |
| 3 | Electrostatic Photoluminescence... | 物理 | ⭐⭐⭐ | 03-27 |
| 4 | MuRF | CV | ⭐⭐ | 03-27 |
| 5 | LGTM | CV | ⭐⭐⭐ | 03-27 |
| 6 | ABot-PhysWorld | 机器人 | ⭐⭐⭐ | 03-25 |
| 7 | SIMART | CV | ⭐⭐⭐ | 03-25 |
| 8 | RealMaster | CV | ⭐⭐⭐ | 03-25 |
| 9 | WildWorld | CV | ⭐⭐⭐ | 03-25 |
| 10 | Universal Normal Embedding | CV/NLP | ⭐⭐⭐ | 03-24 |

---

*由 AI Subagent 自动抓取生成 | 数据来源：api.llamafactory.cn*
