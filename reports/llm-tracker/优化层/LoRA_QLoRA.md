---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a28f6a2529702a31a55c61d651027b0a
    PropagateID: a28f6a2529702a31a55c61d651027b0a
    ReservedCode1: 304602210085ca0b97a1df0af78e69439f36a6fdcabe131464d84ca1c5d73b1283ee588a18022100a4ddbee9a3b1850c7f8589b2c3f9f3d25a30816e0a3b8acd958c478cc0f5df24
    ReservedCode2: 3045022100a393f587b6dcbd45f8e49692ca48043def90ea315b690e6868c43728ec7a840f022057f4014158a7517a459b0bb0188b91cfeb682033a65ae5fe993c6af8e5c0ccee
---

# LoRA / QLoRA

## 核心原理

LoRA（低秩适应）是一种"贴纸式"微调技术。想象给一个预训练好的大脑（基座模型）添加少量"便利贴"（低秩矩阵）来学习新知识，而不需要重新连接整个神经网络。

具体来说，LoRA在预训练模型的权重旁边添加两个小的低秩矩阵A和B，通过 BA 来近似权重变化 ΔW。训练时只更新A和B，原始权重保持冻结。推理时，可以将LoRA权重合并回原模型，几乎没有额外延迟。

QLoRA在LoRA基础上加入了量化技术，将基座模型量化到4-bit，显存需求大幅降低。

## 解决的痛点

- **训练成本高**：全参数微调需要大量GPU显存
- **资源门槛**：普通开发者难以微调大模型
- **灾难性遗忘**：全量微调可能损害原有能力

## 代表模型

- **各类微调模型**：几乎所有开源大模型的微调版本都使用LoRA/QLoRA
- **Alpaca、Vicuna**：最早的LoRA微调对话模型
- **QLoRA应用的各种金融、法律、医疗领域模型**

## 技术报告

- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [QLoRA: Efficient Finetuning of LLMs](https://arxiv.org/abs/2305.14314)
- [DoRA: Weight-Decomposed Low-Rank Adaptation](https://arxiv.org/abs/2402.09353)

## 开源实现

- [PEFT](https://github.com/huggingface/peft): Hugging Face的参数高效微调库
- [LLaMA-Factory](https://github.com/Kousnavaz/LLaMA-Factory): 简易微调框架
- [qlora](https://github.com/artidoro/qlora): QLoRA官方实现
- [LoRAX](https://github.com/Falseing/lorax): 多LoRA推理服务

## 最新进展

1. **DoRA (2025)**：将权重分解为幅度和方向两部分，提升LoRA效果
2. **LoRA+**：对LoRA学习率进行针对性优化
3. **多LoRA部署**：生产环境中同时运行多个LoRA适配器
4. **全参数微调新方法**：如Liger Kernel等进一步降低显存
