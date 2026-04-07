# RWKV

## 核心原理

RWKV（Receptance Weighted Key Value）是一种"集大成者"的架构，结合了Transformer和RNN的优点。它可以理解为"带索引的笔记本"——既有Transformer的并行训练能力，又有RNN的高效推理特性。

RWKV的核心创新是将注意力机制重新表述为RNN形式：
- **Receptance (R)**：类似于"接受度"，决定接受多少历史信息
- **Weight (W)**：可训练的参数矩阵
- **Key (K) 和 Value (V)**：类似于传统注意力中的概念

推理时，RWKV只需维护一个隐状态，像RNN一样逐步计算，内存和计算量与序列长度无关。

## 解决的痛点

- **推理效率**：Transformer推理随上下文增长变慢，RWKV保持恒定
- **长上下文内存**：无需KV缓存，内存占用大幅降低
- **训练成本**：支持长上下文训练而不会OOM

## 代表模型

- **RWKV-7**：最新版本
- **RWKV-6 World**：多语言版本
- **Bunny-RWKV**：轻量版本

## 技术报告

- [RWKV: Reinventing RNNs for the Transformer Era](https://arxiv.org/abs/2305.13048)
- [Efficient Transformers: A Survey](https://arxiv.org/abs/2209.06798)

## 开源实现

- [RWKV官方仓库](https://github.com/BlinkDL/RWKV-LM): 官方实现
- [rwkv.cpp](https://github.com/saharNooby/rwkv.cpp): C++推理实现，支持CPU运行
- [ChatRWKV](https://github.com/BlinkDL/ChatRWKV): 对话模型

## 最新进展

1. **RWKV-7发布**：引入更强的表达能力
2. **多模态扩展**：探索将RWKV用于视觉任务
3. **量化优化**：INT8/INT4量化进一步降低部署门槛
