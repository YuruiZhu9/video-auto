# 开源大模型技术追踪报告索引

> 最后更新：2026-04-02 | 维护方式：每次更新深化已有内容

---

## 📁 目录结构

```
llm-tracker/
├── README.md              # 本文件（索引）
├── 2026年Q1开源大模型技术动态速览.md   # 🌟 本期综合速览
├── 基础层/
│   ├── Attention机制.md       # 待更新
│   ├── Transformer架构.md     # 待更新
│   ├── 位置编码.md            # 待更新
│   └── 激活函数.md            # 待更新
├── 优化层/
│   ├── GRPO_DAPO_RLVR.md     # ✅ v1.0 本期新增
│   ├── Mamba.md              # 待更新（指向 Mamba-3）
│   ├── Mamba-3深度技术解析.md  # ✅ v2.0 本期新增（替代旧版 Mamba.md）
│   ├── RWKV.md               # 待更新
│   ├── LoRA_QLoRA.md        # 待更新
│   ├── MoE.md                # 待更新
│   ├── 量化.md               # 待更新
│   └── 蒸馏.md               # 待更新
└── 应用层/
    ├── 微调部署.md            # 待更新
    ├── 推理优化.md            # 待更新
    ├── RAG架构.md            # 待更新
    ├── Agent设计.md          # 待更新
    └── 后训练革命：GRPO_DAPO_RLVR深度技术解析.md  # ✅ v1.0 本期新增
```

---

## 🆕 本期新增/重大更新（2026-04-02）

### ✅ 新增报告

1. **优化层 / 线性注意力.md**（新增章节）
   - **Stochastic Attention**（arXiv 2604.00754）：大脑连接组启发的随机路由线性注意力
   - Connectome随机路由数学框架、Gumbel-Softmax可微采样、SSM结合代码

2. **优化层 / MoE.md**（新增章节）
   - **Mistral Small 4**（2026-03-26）：119B总参/6.5B活跃/MoE/Apache 2.0许可证
   - "适度稀疏"策略（稀疏比1/18.3）vs Llama 4（1/235）vs DeepSeek-V3（1/11）
   - 可调节`reasoning_effort`参数工程实践

3. **2026-04-02 开源大模型技术深度追踪（下午版）.md**
   - Qwen3.5-Omni登顶HF总榜（TMRoPE/RVQ/ARIA三大技术创新）
   - Stochastic Attention完整代码解析
   - Mistral Small 4三合一整合策略
   - DeepSeek V4倒计时状态

### ✅ 本期前期新增（2026-04-01）

1. **优化层 / Mamba-3深度技术解析.md**（v2.0）
   - 指数-梯形离散化完整推导
   - 复数值 SSM + RoPE Trick 数学原理
   - MIMO 架构代码实现
   - 性能对比与演进历史

2. **应用层 / 后训练革命：GRPO_DAPO_RLVR深度技术解析.md**（v1.0）
   - GRPO vs PPO 数学对比
   - DAPO 四项技术伪代码
   - RLVR + DeepSeek-R1 涌现能力
   - 四阶段训练流水线

3. **2026年Q1开源大模型技术动态速览.md**
   - Mamba-3 发布详情
   - Qwen3 系列 8 款模型
   - GRPO 理论突破（U-统计量）
   - 量化技术新进展（TurboQuant）

---

## 📊 本期技术热度排行

| 排名 | 技术 | 热度 | 趋势 |
|------|------|------|------|
| 🥇 | Stochastic Attention | ⭐⭐⭐⭐⭐ | 🆕 arXiv新论文 |
| 🥈 | Qwen3.5-Omni | ⭐⭐⭐⭐⭐ | 🆕 HF霸榜 |
| 🥉 | Llama 4 MoE | ⭐⭐⭐⭐⭐ | 架构突破 |
| 4 | Mistral Small 4 | ⭐⭐⭐⭐ | 🆕 Apache 2.0 |
| 5 | Mamba-3 SSM | ⭐⭐⭐⭐ | 持续发酵 |
| 6 | DeepSeek V4 | ⭐⭐⭐⭐ | 倒计时中 |
| 7 | DAPO/GRPO | ⭐⭐⭐ | 实用化 |

---

## 🔧 更新计划

### 下一期（2026-05-01）重点追踪
1. DeepSeek V4 正式发布及技术规格
2. Mamba-3 规模化验证（更大参数版本）
3. Qwen3 衍生生态（HuggingFace 模型分析）
4. Agentic RL 最新论文（NeMo Gym）
5. Gated Linear Attention 新论文

### 待补全的基础文档
- [ ] Attention 机制（Flash Attention v3、Ring Attention）
- [ ] Transformer 架构演进（Llama 架构、Gemma 架构）
- [ ] 位置编码（RoPE、ALiBi、Kerple）
- [ ] LoRA/QLoRA 最新变体（DoRA、LoRA+）

---

## 📖 阅读建议

**初学者路线**：
1. 先读《2026年Q1速览》了解全景
2. 再读《GRPO/DAPO/RLVR》理解后训练革命
3. 最后读《Mamba-3》深入 SSM 架构

**进阶路线**：
1. 直接从《Mamba-3》开始（有 SSM 基础）
2. 深入论文原文（推荐阅读）
3. 复现关键代码实验
