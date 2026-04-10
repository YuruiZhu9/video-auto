# 代码架构思维提升

> 从"能跑的代码"到"有架构的代码"

## 📚 内容导航

### 快速入门

- [数据库选型与推荐系统全链路实战](知识点/数据库选型与推荐系统全链路实战.md) ⭐ 新增 - MySQL/PG + ClickHouse + Redis + Milvus 四大数据库选型决策树 / Repository 模式 + 连接池完整 Python 实现（参数化查询防注入 / JSON 虚拟列 / batch_find 防 N+1）/ ClickHouse 行为日志表设计 + 物化视图自动聚合 CTR / Redis 四大经典用法（推荐结果缓存 / 行为序列 / Bloom Filter 去重 / 分布式锁）/ Milvus HNSW 索引 + 混合检索（向量+L2距离+类目加权）完整 SDK 代码 / 全链路存储架构图 / 选型决策速查表 / 四大生产避坑（MySQL全表扫描 / Redis缓存雪崩 / Milvus OOM / ClickHouse合并风暴）

- [架构评估体系：量化判断代码好坏](知识点/架构评估体系：量化判断代码好坏.md) ⭐ 新增 - 四大核心度量维度（圈复杂度/耦合度/内聚度/架构熵）/ Python 完整 CCN 计算代码（ast.NodeVisitor 反例正例对比）/ 耦合度分析（不稳定指数 I = Ce/(Ca+Ce)）/ LCOM 内聚度计算器 / 架构熵监控仪表盘（熵值 = 综合加权评分，趋势比绝对值重要）/ 推荐系统专项评估清单（召回层/排序层/架构层/可测试性四维）/ 推荐系统各层打分雷达图（A/B/C/D/F 五级评价）/ SonarQube/radon/lizard 等工具推荐 / 健康度雷达图综合评分公式 / 六大常见误区（追求完美分数/只看单一指标/只测一次/指标至上）

- [渐进式重构实战：在业务压力下安全改善代码](知识点/渐进式重构实战：在业务压力下安全改善代码.md) ⭐ 新增 - 渐进式 vs 传统重构对比表（风险/中断/协作/可回滚性四维）/ 三原则（Baby Steps/始终可运行/保险网）/ 完整演进路线图（诊断→基础设施→分层隔离→设计模式→微服务拆分五阶段）/ **实战案例**：3000行上帝函数 → 分层架构六步走（FeatureFlag → 配置层 → Repository → 领域逻辑 → DI容器 → 监控门禁） / SQL注入/圈复杂度67/无测试/硬编码四大坏味道全诊断 / Repository 模式（MySQL参数化查询/aiomysql异步池/接口抽象） / 领域层零依赖设计 / DI容器 + 应用层UseCase组装 / 健康度自动门禁（回退率>30%自动熔断新逻辑） / 安全检查清单（重构前/中/后必查项）/ 四大常见陷阱详解
- [学习路径总览](学习路径/总览.md) - 三阶段学习计划

- [MLOps 端到端流水线实战](知识点/MLOps端到端流水线实战.md) ⭐ 新增 - 推荐系统从训练到上线的完整工程实践 / MLOps 三级别（手工→自动化训练→CI/CD）/ MLflow 完整训练流水线（数据加载→特征工程→训练→评估→注册到 Model Registry）/ 模型蓝绿部署与热加载（ModelVersionManager）/ 四种训练触发策略（定时/数据量/性能下降/手动）/ 数据漂移检测（PSI 指标，PSI≥0.2 触发重训）/ 推荐系统 MLOps 演进三阶段路线图 / 训练/部署/监控三阶段 Checklist / 五大常见误区（只管训练不管 Skew/离线涨≠线上涨/无数据版本管理）
- [代码质量评估清单](知识点/代码质量评估清单.md) ⭐ 新增 - 14维度评估清单：分层架构/命名可读性/SRP函数设计/错误处理/依赖注入/DRY重复/SQL安全/可测试性/性能意识；含推荐系统专项质量检查（上线路/精排层/重排层）；5分钟快速发现代码问题的步骤；上线前必检清单 + 质量打分表 - 什么是 ADR + 标准模板 / 5个真实推荐系统决策场景（MySQL+ClickHouse+Redis三层架构 / Flink实时特征 / ES/Milvus向量库选型 / 单体→微服务演进 / Flask→Triton模型服务升级）/ 每条ADR含替代方案对比表 + 权衡分析 + 决策理由 + 正负面后果 / ADR落地指南：写作检查清单 + 生命周期 + Git管理方式 / ADR vs 技术设计方案区别 + 3个实战练习
- [六边形架构与适配器模式实战](知识点/六边形架构与适配器模式实战.md) ⭐ 新增 - 端口与适配器模式深度解析 / 六种端口定义（Recall/Ranking/Profile/Storage/Event/Cache）完整 Python 代码 / 反例（耦合地狱）→ 正例（六边形）完整对比 / Flask/gRPC/MySQL/Redis/Kafka/Embedding 六类适配器实现 / DI 容器完整代码 / 纯内存单元测试（无需启动外部服务） / 六边形 vs 整洁架构 vs MVC 横向对比 / 推荐系统六边形架构决策树 + 快速对照表
- [设计模式实战手册](知识点/设计模式实战手册.md) ⭐ 新增 - 推荐系统最常用的 8 种设计模式：策略模式（多路召回）/ 模板方法（召回路→排序→重排流程）/ 观察者（用户行为→多Consumer处理）/ 装饰器（推荐结果后处理链）/ 代理模式（模型推理缓存）/ 建造者（推荐请求构建）/ 责任链（鉴权→限流→推荐）/ 工厂模式（场景化推荐服务）；含完整Python代码 + 反例正例对比 + 模式选择决策树 + 推荐系统全景应用图
- [MVC vs MVVM 详解](知识点/MVC_MVVM详解.md) - 两大经典模式对比
- [SOLID 原则详解](知识点/SOLID详解.md) - 五大设计原则
- [识别代码坏味道](知识点/识别代码坏味道.md) - 重构第一步
- [CQRS 模式实战](知识点/CQRS模式实战.md) - 读写分离与推荐系统优化
- [DDD 领域驱动设计入门](知识点/DDD领域驱动设计入门.md) - 从业务概念到代码模型
- [微服务架构实战](知识点/微服务架构实战.md) - 从单体到分布式推荐系统
- [架构师思维修炼](知识点/架构师思维修炼.md) - 权衡分析/容量规划/演进架构/ADR
- [Repository 模式与数据访问层实战](知识点/Repository模式与数据访问层实战.md) ⭐ 新增 - 连接领域逻辑与持久化存储的桥梁 / 核心接口设计（IUserProfileRepository/IItemRepository/IBehaviorRepository） / dataclass 领域对象 vs ORM Model 对比 / PostgreSQL + Redis 双实现完整代码（MySQL 实现 vs Redis 缓存实现） / 依赖注入容器 + FastAPI 集成 / TypeScript NestJS + TypeORM 完整实现 / **Unit of Work 模式**（原子操作 + 事务回滚，推荐系统记录行为三步原子化实战） / 单元测试（Mock Repository + 验证无 N+1） / 三大常见误区（业务逻辑混入/表对Repository/全走ORM） / Repository 决策树 / 与六边形架构/Clean Architecture/DI容器/CQRS 关联图
- [测试策略与质量保障](知识点/测试策略与质量保障.md) - 单元测试/集成测试/CI/CD/冒烟测试
- [Redis 缓存与性能优化实战](知识点/Redis缓存与性能优化实战.md) ⭐ 新增 - 推荐系统命脉：三大缓存模式 / Cache-Aside / Write-Through / Write-Behind / 缓存穿透+击穿+雪崩全解 / 多级缓存架构 / Python 完整实现代码

- [事件驱动架构与 Kafka 实战](知识点/事件驱动架构与Kafka实战.md) - 实时推荐系统的异步血液
- [可观测性实战：日志 · 指标 · 链路追踪](知识点/可观测性实战：日志指标链路追踪.md) ⭐ 新增 - 推荐系统上线必备

- [自适应架构与系统韧性设计](知识点/自适应架构与系统韧性设计.md) ⭐ 新增 - 混沌工程 / 弹性伸缩 / 灰度发布 / 自适应限流完整实战
  - **混沌工程引擎**：推荐系统主动故障注入实战，ChaosEngine 完整 Python 实现 + 安全规范（最小化爆炸半径 / 渐进式注入 / 自动回滚 / 通知机制）
  - **K8s 进阶 HPA**：QPS + P99延迟 + Kafka Consumer Lag 三指标复合扩缩容，YAML 完整配置
  - **预测式扩容**：PredictiveScaler 基于历史QPS趋势预测（线性回归），提前扩容避免措手不及
  - **三阶段弹性伸缩策略**：日常弹性 → 热点事件响应 → 降级保护
  - **金丝雀发布系统**：CanaryExperiment 完整实现（一致性哈希路由 / CTR对比决策树 / 自动扩容节奏 5%→10%→30%→50%→100% / 自动回滚 / Scheduler 调度器）
  - **自适应限流**：AdaptiveRateLimiter（令牌桶 + 动态阈值 + 分级降级，告别固定阈值）
- [技术债识别与偿还策略](知识点/技术债识别与偿还策略.md) ⭐ 新增 - 四象限分类框架 / 战略/权衡/疏忽/根本四类债详解 / 推荐系统五类典型债（架构/数据/工程/测试/可观测性）自查清单 / 利息率量化法（年利息支出=修改次数×利息×基准时间，ROI 6个月回本）/ 五种偿还策略（Boy Scout Rule / Strangler Fig / 抽象分支 / JIT还债 / 专项Sprint）/ 推荐系统专项还债路线图（高息债→策略抽象 2周/FeatureStore统一 3周 / 中息债→可观测性 1月 / 低息债→pre-commit hook）/ TECH_DEBT.md 债务登记模板 / 与业务沟通话术（效率损失量化 vs "代码要重构"）/ 自检清单每月一次 + 实践作业
- [配置中心与动态配置实战](知识点/配置中心与动态配置实战.md) ⭐ 新增 - 本地配置/Redis动态配置/Apollo三层架构演进 / 功能开关（Feature Flag）完整 Python 实现：四类开关（发布/实验/运营/权限）+ 一致性哈希灰度分流 + 规则引擎 / 推荐系统 20+ 核心开关清单（召回/排序/重排/实验/运营）/ 引擎集成示例：开关驱动推荐流程热切换 / 分层实验模型：同层互斥 + 异层正交 + ExperimentAllocator 实现 + Redis 指标采集 / 配置版本管理与回滚 / 生产检查清单 10 项

- [Kubernetes 云原生部署与 ML 系统容器化实战](知识点/Kubernetes云原生部署与ML系统容器化实战.md) ⭐ 新增 - 容器化 Dockerfile 最佳实践（Multi-stage Build / 非 root 用户 / 健康检查）/ K8s Deployment 完整 YAML（资源限制/亲和性/探针/生命周期钩子）/ HPA 自动扩缩容（CPU+自定义指标 P99 延迟）/ ConfigMap/Secret 配置管理 / 蓝绿部署 + Rolling Update / Ingress 限流路由 / 推荐系统完整 K8s 架构决策树 / 常见四大误区（资源 limit/健康检查/滚动更新/优雅下线）
- [NestJS K8s 容器化实战](代码案例/TypeScript案例/NestJS_K8s容器化实战.md) ⭐ 新增 - NestJS 专用 Dockerfile（Multi-stage Build / Alpine 精简镜像 / 非 root 用户）/ 健康检查端点（liveness vs readinessProbe）/ 完整 K8s YAML（Deployment/Service/HPA/ConfigMap/Secret）/ 优雅关闭（SIGTERM / lifecycle preStop / 连接池清理）/ HPA 扩缩容冷却策略 / 常用 kubectl 部署命令 + 滚动回滚

- [模型服务化架构与推理优化实战](知识点/模型服务化架构与推理优化实战.md) ⭐ 新增 - Triton/Ray Serve/vLLM 推理服务器 / 批量推理 vs 串行推理 QPS 对比 / 模型版本管理 + A/B 灰度路由 / 三级降级策略（模型→缓存→规则兜底）/ 在线学习架构（Ray Serve 增量更新）/ 推荐系统模型服务化完整架构图 / 框架对比（Triton vs Ray Serve vs vLLM vs TF Serving）/ 上线检查清单 12 项：四类日志设计（审计/算法/行为/异常）/ Prometheus + Grafana 完整指标体系 / OpenTelemetry 全链路追踪实现 / 推荐系统 SLO 设定与错误预算告警 / Grafana 看板核心面板 + 告警规则 YAML

- [数据质量监控与 ML 流水线可靠性实战](知识点/数据质量监控与ML流水线可靠性实战.md) ⭐ 新增 - 推荐系统数据质量六维度 / DataQualityChecker 质量门禁 / 训练-服务 Skew 检测 + PSI / 标签质量监控 / Pipeline 断点续传 + 重试
- [向量数据库架构实战](知识点/向量数据库架构实战.md) ⭐ 新增 - ANN 索引算法（HNSW/IVF-Flat/IVF-PQ/DiskANN）深度对比与选型决策树 / 四大向量数据库（Milvus/Qdrant/Weaviate/Pinecone）横向对比 / 完整 Milvus Python SDK v2 实现（创建Collection/ANN搜索/混合搜索/批量插入）/ 多路召回引擎架构（策略模式 + 并行召回）/ 训练-服务一致性 Skew 问题解决（EmbeddingService 统一）/ 离线+在线双链路同步 / 常见生产坑（OOM/维度不匹配/Filtering失效）
- [API 安全与身份认证实战](知识点/API安全与身份认证实战.md) ⭐ 新增 - JWT 签发/验签/安全 Checklist / RBAC 权限模型 Python+TS 双实现 / API 安全十大最佳实践（限流/脱敏/CORS/SQL注入/XSS/CSRF/审计日志）/ OAuth2 微信登录完整流程 / 推荐系统专项安全防护（越权/重放/限流）/ 安全架构总览图
- [GraphQL 推荐系统 API 实战](知识点/GraphQL推荐系统API实战：灵活查询与BFF网关.md) ⭐ 新增 - REST vs GraphQL 核心对比（Over-fetching/Under-fetching/N+1问题）/ 推荐系统 GraphQL Schema 完整设计（Item/UserProfile/RecommendResult类型 + Strawberry）/ Query/Mutation 完整实现（批量推荐/行为记录/反馈）/ **DataLoader 批量加载器**（解决 N+1 问题的核心，批量合并 N 次 DB 查询 → 1 次）/ Relay Cursor 分页（稳定游标 vs 不稳定页码）/ GraphQL BFF 网关架构（FastAPI + gRPC 后端混合部署）/ 限流中间件 / 查询复杂度分析器（防止滥用）/ 生产检查清单 10 项 / 与 REST/gRPC 混合架构图

### 代码案例
- [Python 三层架构实战](代码案例/Python案例/三层架构实战.md) - FastAPI 示例
- [NestJS 模块化架构](代码案例/TypeScript案例/NestJS模块化架构.md) - TypeScript 示例

## 🚀 快速开始

### 第一步：理解基础模式
1. 阅读 MVC vs MVVM 文档
2. 对比 Flask（原生）vs FastAPI（MVC）实现
3. 对比 React（类组件）vs Vue3（MVVM）实现

### 第二步：掌握设计原则
1. 从 SOLID 原则开始
2. 用自己代码找违反原则的例子
3. 尝试重构一个旧项目

### 第三步：动手实践
1. 选一个项目（有代码仓库的）
2. 用坏味道清单检查
3. 制定重构计划
4. 分步骤实施

## 📖 学习建议

| 阶段 | 时间 | 重点 |
|------|------|------|
| 基础模式 | 2-3 周 | 理解分离思想 |
| 设计原则 | 2-3 周 | SOLID + DRY + KISS |
| 重构实战 | 持续 | 识别 + 改进 |

## 🛠 工具推荐

- **代码分析**：SonarQube、ESLint、Flake8
- **重构工具**：PyCharm/IDEA 的重构功能
- **设计工具**：PlantUML、Draw.io 画类图
- **学习资源**：Refactoring Guru、SourceMaking

## 📅 更新日志

- 2026-04-10 PM ⭐ 新增《数据库选型与推荐系统全链路实战》
  - MySQL / PostgreSQL + ClickHouse + Redis + Milvus 选型决策树（5 个问题快速定位）
  - **Repository 模式完整 Python 实现**：连接池 + 参数化查询防注入 + batch_find 防 N+1 + JSON 虚拟列
  - **ClickHouse 行为日志设计**：MergeTree 表 + 物化视图自动聚合 CTR + 批量写入技巧（防合并风暴）
  - **Redis 四大经典用法**：推荐结果缓存（TTL 5min）/ 行为序列（LPUSH+LTRIM）/ Bloom Filter 去重 / 分布式锁防缓存击穿
  - **Milvus 全链路 SDK**：HNSW 索引创建 + insert_embeddings（每晚 ETL）+ search_similar_items + 混合检索（向量+L2+类目加权）
  - 全链路存储架构图（Flask → Redis/MySQL/Milvus → 精排 → ClickHouse）
  - 选型速查表（用途/规模/延迟/查询类型四维对比）+ 四大生产避坑详解

- 2026-04-09 PM ⭐ 新增《架构评估体系：量化判断代码好坏》
  - 四大核心度量维度：圈复杂度（CCN）/ 耦合度（不稳定指数 I）/ 内聚度（LCOM）/ 架构熵
  - **Python 完整 CCN 计算器**：ast.NodeVisitor 遍历函数节点，输出高风险函数列表（>20复杂度标记警告）
  - **耦合度分析**：Afferent/Efferent Coupling + 不稳定指数 I = Ce/(Ca+Ce)，找出核心稳定模块 vs 不稳定模块
  - **LCOM 内聚度计算**：功能内聚→顺序内聚→通信内聚→巧合内聚，口诀判断法 + Python 实现
  - **架构熵监控**：熵值 = 复杂度权重2× + 覆盖率权重1× + 上帝类权重3× + LCOM权重5×，量化"架构混乱程度"
  - 推荐系统各层评分雷达图（A/B/C/D/F 五级），含召回层/排序层/缓存层/数据层/API层真实评分
  - **推荐系统专项评估清单**：召回策略热插拔/模型推理熔断/分层边界/循环依赖/Repository模式/DI容器/测试覆盖率七项
  - SonarQube/radon/lizard/ArchUnit/ts-arch 工具矩阵推荐
  - 六大常见误区（追求完美分数/只看单一指标/只测一次/指标至上） + 正确姿势（五步法）

- 2026-04-09 PM ⭐ 新增《渐进式重构实战：在业务压力下安全改善代码》
  - 渐进式 vs 传统重构四维对比（风险高/业务中断/协作难/回滚难 → 风险低/无感/独立/易回滚）
  - **完整五阶段演进路线图**：现状诊断(1-2天) → 基础设施(1周) → 分层隔离(2-3周) → 设计模式(2-3周) → 微服务拆分(持续)
  - **六步实战案例**：3000行上帝函数圈复杂度67 + SQL注入 + 无测试 + 硬编码 → 六边形分层架构
    - Step1：Feature Flag 双轨并行（is_enabled + 灰度分流，回退率>30%自动熔断）
    - Step2：配置层提取（dataclass配置类 + 环境变量，消灭魔法数字）
    - Step3：Repository模式（参数化SQL防注入 + aiomysql异步连接池 + 接口抽象可Mock）
    - Step4：领域层零依赖（RecommendationEngine纯Python无外部导入）
    - Step5：DI容器 + UseCase组装（FeatureFlag路由新旧逻辑）
    - Step6：健康度门禁（HealthGate自动检查 + P99延迟告警 + 自动熔断）
  - 重构安全检查清单（重构前/中/后各阶段必查项）
  - 四大常见陷阱详解（跳过FeatureFlag/一次改太多/忽略旧逻辑/无监控）

- 2026-04-07 PM ⭐ 新增《数据质量监控与 ML 流水线可靠性实战》
  - 数据质量六维度：准确性/完整性/一致性/时效性/唯一性/有效性
  - **数据质量检查框架**：DataQualityChecker 完整实现（缺失率/异常值/数据延迟/量级突变/重复记录五大检查 + 质量门禁流水线）
  - **训练-服务一致性 Skew 检测**：FeatureSignature 签名体系 + PSI 指标 + 告警阈值；Skew 是推荐系统最隐蔽的慢性病（训练和推理特征分布不一致，模型学到错误规律）
  - **标签质量监控**：LabelQualityMonitor（CTR / Position Bias 去偏 / 覆盖率 / 新颖度）+ 异常检测
  - **Pipeline 可靠性**：PipelineScheduler 带断点续传的实现（checkpoint / 自动重试 / 指数退避 / 流水线失败分级告警）
  - 推荐系统数据质量全景监控架构图（数据源层 → 质量检查层 → 告警层 → Grafana 仪表盘）
  - 每日检查清单（7 项指标 + 阈值 + 应对措施）+ 上线前检查（特征一致性/标签质量/冷启动/数据泄漏）
  - 五大常见误区：只监控模型不监控数据 / Skew 等效果差才查 / 缺失值直接填充 / Pipeline 无断点 / 只看点击不看其他信号

- 2026-04-06 PM ⭐ 新增《Repository 模式与数据访问层实战》
  - 连接领域逻辑与持久化存储的桥梁 / 核心接口设计（IUserProfileRepository/IItemRepository/IBehaviorRepository） / dataclass 领域对象 vs ORM Model 对比 / PostgreSQL + Redis 双实现完整代码（MySQL 实现 vs Redis 缓存实现） / 依赖注入容器 + FastAPI 集成 / TypeScript NestJS + TypeORM 完整实现 / Unit of Work 模式（原子操作 + 事务回滚，推荐系统记录行为三步原子化实战） / 单元测试（Mock Repository + 验证无 N+1） / 三大常见误区（业务逻辑混入/表对Repository/全走ORM） / Repository 决策树 / 与六边形架构/Clean Architecture/DI容器/CQRS 关联图
- 2026-04-06 PM ⭐ 新增《自适应架构与系统韧性设计》
- 2026-04-06 PM ⭐ 新增《推荐系统架构实战练习册》
  - 🎯 6 个真实场景串联整个学习路径
  - 练习一：单文件推荐服务 → 整洁四层架构（六边形端口/适配器/DI容器完整实现）
  - 练习二：if-else 召回策略 → 策略模式 + 工厂模式 + 多路召回并行编排
  - 练习三：裸调用模型推理 → 超时/重试/熔断三件套 + 三级降级策略
  - 练习四：同步写库 → Kafka 事件驱动（点击打点 P99 从 500ms → 20ms）
  - 练习五：从零建立测试体系（conftest fixtures / 单元测试 Mock / SQLite 集成测试 / GitHub Actions CI）
  - 练习六：4 倍流量增长容量规划 + 三阶段演进路线图（单体→垂直拆分→水平拆分）+ ADR 决策文档化
  - 总验收清单（6 项实操检验）+ 学习路径对应表（练习 → 知识点映射）
  - 混沌工程引擎（ChaosEngine）：推荐系统主动故障注入，定义稳态→假设→注药→观察四步法，Redis宕机/模型超时/Kafka Lag三大场景实战，安全规范（爆炸半径/渐进式/自动回滚/通知机制）
  - K8s 进阶 HPA：QPS+P99延迟+Consumer Lag 三指标复合扩缩容配置，scaleUp/scaleDown stabilizationWindowSeconds 防抖动
  - 预测式扩容（PredictiveScaler）：基于历史QPS线性回归，提前预判峰值流量主动扩容
  - 推荐系统三阶段弹性伸缩策略：日常弹性 → 热点事件响应 → 降级保护
  - 金丝雀发布系统（CanaryExperiment）：一致性哈希路由用户→CTR对比→自动扩容节奏→自动回滚→Scheduler调度器完整实现
  - 自适应限流（AdaptiveRateLimiter）：令牌桶+动态阈值+分级降级（高优先级始终通过，低优先级高负载优先拒绝）

- 2026-04-04 PM ⭐ 新增《技术债识别与偿还策略》
  - 技术债四象限分类：战略性债（接受）/ 权衡性债（记录）/ 疏忽性债（学习）/ 根本性债（预防，最危险）
  - 推荐系统五类典型债自查清单：架构债务（单体变死胖）/ 数据债务（训练-服务特征 Skew）/ 工程债务（硬编码/魔法数字/上帝类）/ 测试债务（零覆盖率代价）/ 可观测性债务（故障靠猜）
  - 利息率量化法：年利息 = 修改次数 × 利息率 × 单次基准时间，财务视角说服业务（48 人小时/年 vs 8 小时还债 = 6倍 ROI）
  - 五种偿还策略：Boy Scout Rule（顺手清理）/ Strangler Fig（灰度替换核心模块）/ Branch by Abstraction（抽象先行）/ JIT 还债（修 Bug 时顺手清坏味道）/ 专项 Sprint（季度集中还债）
  - 推荐系统专项还债路线图：Feature Store 统一特征处理（高优先级）/ 策略模式抽象（高优先级）/ 可观测性体系（中优先级）/ 测试覆盖率持续提升（中优先级）
  - TECH_DEBT.md 债务登记模板 + Sprint 回顾债务审查机制
  - 与业务沟通话术："每月节省 48 人小时" vs "我们要重构代码"，用效率损失量化换资源
  - 每月自检清单（架构/数据/工程/测试/可观测性五维评估）+ 实践作业

- 2026-04-03 AM ⭐ 新增《配置中心与动态配置实战》
  - 本地配置 → Redis 动态配置 → Apollo/Nacos 三层架构演进路线
  - 功能开关（Feature Flag）完整 Python 实现：四类开关（发布/实验/运营/权限）/ 白名单优先 + 规则引擎 + 一致性哈希百分比分流 / 推荐系统 20+ 核心开关清单（召回/排序/重排/实验/运营）
  - 推荐引擎集成示例：功能开关驱动整个推荐流程热切换，修改策略不用发版
  - 分层实验模型（A/B Testing）：同层实验互斥 + 不同层实验正交 + ExperimentAllocator 实现 + Redis 实验指标采集
  - 配置版本管理与回滚：ConfigVersionManager 快照存储 + 版本列表 + 一键回滚
  - Apollo 推荐系统配置模板：model/ranking/recall/feature_store 全量字段
  - 生产检查清单 10 项：功能开关/版本历史/灰度规范/密钥管理

- 2026-04-03 AM ⭐ 新增《向量数据库架构实战》
  - ANN 索引算法（HNSW / IVF-Flat / IVF-PQ / DiskANN）深度对比与选型决策树：什么场景选什么索引
  - 四大向量数据库横向对比（Milvus / Qdrant / Weaviate / Pinecone）：架构/Filtering能力/多模态/成熟度
  - **完整 Milvus Python SDK v2 实现**：创建Collection（Schema+索引）/ ANN搜索 / BM25+向量混合搜索（RRF融合）/ 批量插入
  - **多路召回引擎**：策略模式 BaseRecallStrategy 抽象 + VectorRecallStrategy + ItemCF 并行召回编排
  - EmbeddingService 统一服务：解决训练-服务一致性问题（Skew），版本号管理
  - 离线+在线双链路同步：每日全量 ETL + 每小时增量同步，Milvus Collection 管理
  - 生产避坑指南：内存OOM / 向量维度不匹配 / Filtering失效 / 实时更新碎片化

- 2026-04-01 AM ⭐ 新增《六边形架构与适配器模式实战》
  - 端口（Port）与适配器（Adapter）核心理念详解：为什么推荐系统核心逻辑必须和 MySQL/Redis/Kafka 解耦
  - 六种端口完整 Python 定义：RecallPort / RankingPort / UserProfilePort / RecommendationStoragePort / EventPublishPort / CachePort
  - **反例（耦合地狱）→ 正例（六边形）** 完整对比：直接 requests.post 模型服务 / 硬编码 MySQL 连接 / 框架耦合的四大罪状 vs 端口抽象后的代码
  - **六类次适配器（Secondary Adapter）完整实现**：MySQL 用户画像（aiomysql连接池）/ Redis 缓存 / Kafka 事件发布（aiokafka + 容错）/ Embedding 模型推理（httpx + 超时）/ ItemCF 召回 / Mock 排序
  - 主适配器（Driving Adapter）：Flask REST API 完整实现，HTTP 请求 → 领域逻辑全链路
  - **DI 容器**完整代码：`DIContainer.initialize()` 启动时连接所有外部服务，`shutdown()` 优雅关闭
  - **纯内存单元测试**：Mock 所有 Port，pytest + asyncio 无需启动 MySQL/Redis/Kafka，测试速度从 10 分钟 → 3 秒
  - 六边形 vs 整洁架构 vs MVC 横向对比表（适用场景/依赖方向/测试友好度）
  - 六边形 + 整洁架构结合图：推荐系统最优分层方案（外层基础设施 / 应用层用例 / 领域层核心 / 接口层DTO）
  - 推荐系统六边形架构决策树（新增外部服务 / 换AI模型 / 加召回策略 / 换数据库 → 怎么应对）
  - 学习路径总览同步新增六边形架构章节，含端口速查表 + 学习目标

- 2026-03-31 PM：新增《设计模式实战手册》
  - 推荐系统最常用的 8 种设计模式深度解析（策略/模板方法/观察者/装饰器/代理/建造者/责任链/工厂）
  - 每种模式含：反例（坏味道）→ 正例（改进后）完整 Python 代码
  - 策略模式：RecallStrategy 抽象接口 + 召回引擎注册机制，多路召回可热插拔
  - 模板方法：RecommendationPipeline 抽象流程 + 精排/粗排子类实现
  - 观察者：EventBus 事件总线 + UserProfile/CacheWarmer/Analytics 三观察者
  - 装饰器：RecommenderDecorator 基类 + 去重/解释/广告标记灵活组合
  - 代理模式：CachedModelProxy 缓存代理，HIT/MISS 可观测
  - 建造者：链式构建 RecommendRequest，语义清晰告别超长构造函数
  - 责任链：Auth → RateLimit → Cache → Recommend 处理器链，可插拔
  - 工厂模式：@register 装饰器 + create_by_scene(scene) 按场景自动推断推荐器
  - 模式选择决策树（问自己5个问题 → 选对模式）+ 推荐系统模式应用全景图
  - 学习路径第四阶段"设计模式"对应文件落地

- 2026-03-29 PM：新增《API 安全与身份认证实战》
  - JWT 签发/验签完整 Python + TypeScript 实现（PyJWT / NestJS Passport）
  - JWT 安全 Checklist：HS256 vs RS256 / Token 短期化 / Refresh Token 机制 / Payload 不能放敏感数据
  - RBAC 权限模型：User → Role → Permission 三层体系，推荐系统 admin/editor/viewer/algorithm_engineer 四角色 + 装饰器实现
  - API 安全十大最佳实践：HTTPS / 限流（Python 装饰器 + Redis 分布式令牌桶）/ 输入校验 Pydantic / 敏感数据脱敏（手机号/邮箱）/ CORS 白名单配置 / 统一响应格式 + request_id / SQL注入参数化查询 / 请求体大小限制 / 审计日志中间件 / 推荐结果防注入白名单
  - OAuth2 微信登录完整流程：code 换 token → 获取用户信息 → 生成自己 JWT，三步详解 + Python 实现
  - 推荐系统专项安全：越权访问（user_id 归属检查）/ 重放攻击（Nonce + 时间戳）/ 暴力破解（限流 + 账户锁定）
  - 安全架构总览图：API Gateway → JWT验签 → RBAC → 审计日志 → 响应脱敏 → 内部 mTLS

- 2026-03-28 PM：新增《可观测性实战：日志 · 指标 · 链路追踪》
  - 推荐系统四类日志：审计日志（request_id+user_id+scene）/ 算法执行日志（召回→排序→重排）/ 行为日志（曝光/点击/购买）/ 系统异常日志
  - Python 结构化 JSON 日志完整实现（StructuredFormatter + ContextVar 请求追踪 + FastAPI 中间件）
  - Prometheus 指标采集：Counter（请求量）/ Histogram（延迟分布）/ Gauge（缓存命中率）/ 完整装饰器实现
  - OpenTelemetry 全链路追踪：推荐请求完整调用树（召回→排序→重排各阶段耗时可视化）
  - Grafana 看板核心 6 面板：QPS / P99延迟 / 错误率 / CTR / 缓存命中率 / 各阶段延迟占比
  - Prometheus AlertManager 告警规则（延迟 >500ms / 缓存命中率 <90% / 错误率 >1% / 模型推理 P99 >200ms）
  - 推荐系统可观测性架构图：Fluent Bit → Loki / Prometheus → Grafana / OTel → Tempo → Grafana
  - SLO 定义与健康度检查：可用性（99.9%）/ 延迟（P50<100ms，P99<300ms）/ 缓存命中率（>95%）
  - 错误预算燃烧速度（Error Budget Burn Rate）：burn_rate > 14.4 → 1h 内烧完整月预算（紧急告警）
  - 上线前可观测性检查清单（20 项）

- 2026-03-27 PM：新增《Redis 缓存与性能优化实战》
  - 推荐系统为什么必须缓存（延迟从 500ms → 20ms 的秘密）
  - 三大缓存模式详解：Cache-Aside / Write-Through / Write-Behind
  - 推荐系统三大实战场景：首页推荐缓存、多路召回特征批量查询、Embedding向量缓存
  - TTL 设计策略 + 防缓存雪崩（TTL随机偏移、多级缓存）
  - 缓存三大经典问题：穿透（Bloom Filter）、击穿（分布式锁）、雪崩（多级缓存）
  - Redis Cluster 生产配置 + 监控告警指标 + key 命名规范
  - 序列化选择：JSON vs msgpack vs Protobuf 对比
  - Python 完整代码实现（Cache-Aside / Write-Through / Write-Behind / 分布式锁 / 多级缓存）

- 2026-03-26 PM：新增《事件驱动架构与 Kafka 实战》
  - 同步调用 vs 事件驱动核心对比（耦合度/响应时间/扩展性）
  - 推荐系统关键事件清单：click / view / purchase / rate / search 等
  - Kafka Producer/Consumer 完整 Python 实现代码
  - 推荐缓存预热实战案例：点击事件 → 异步更新 Redis → P99 200ms → 20ms
  - 推荐系统 Kafka 事件流完整架构图
  - 消费者组隔离设计：profile-service / cache-warmer / analytics 分组消费
  - 生产环境可靠性配置：acks=all / 幂等性 / 手动 offset 提交
  - 常见误区：Consumer 阻塞主循环 / 无幂等性 / 不监控 Lag

- 2026-03-25 PM：新增《测试策略与质量保障》
  - 测试分层策略：单元测试/集成测试/E2E测试/冒烟测试四层体系
  - 推荐系统核心单元测试：召回策略(ItemCF/Embedding)、排序模型、降级策略
  - Repository + API 集成测试：SQLite内存数据库 + FastAPI TestClient
  - Mock与Patch：何时用Mock的正确姿势（外部HTTP/Redis/模型推理）
  - GitHub Actions CI/CD完整配置：Lint → 单元测试 → 集成测试 → Docker镜像 → K8s部署 → 金丝雀发布
  - 上线前冒烟测试：健康检查/延迟/并发/降级四项清单
  - pytest最佳实践：目录结构/conftest/并行运行/覆盖率目标

- 2026-03-25 PM：新增《架构师思维修炼》
  - 权衡分析：技术选型优缺点对比表（MySQL/MongoDB/Redis/Kafka/gRPC）
  - 容量规划：推荐系统存储/QPS/服务器估算公式与步骤
  - 演进式架构：单体→分层→微服务三阶段演进路线图 + 决策树
  - 推荐系统三级降级策略：模型降级 → 缓存降级 → 静态兜底
  - ADR（架构决策记录）模板：技术选型决策文档化方法
  - Code Review 架构视角：8 个关键评审问题清单
  - 三个实践作业：项目分析 / ADR 写作 / 容量估算

- 2026-03-25 AM：新增《微服务架构实战》
  - 推荐系统微服务拆分策略（用户域/内容域/推荐引擎域）
  - API Gateway + 限流鉴权完整实现
  - gRPC（同步）和 Kafka（异步）两种通信模式
  - 服务注册与发现（Consul）+ 熔断器（Circuit Breaker）
  - 完整推荐系统微服务架构图 + 各服务详细代码
  - 从单体到微服务三阶段演进路线图

- 2026-03-24 PM：新增《DDD 领域驱动设计入门》
  - Entity / Value Object / Aggregate / Repository 核心概念详解
  - Domain Service（领域服务）vs Domain Event（领域事件）对比
  - 推荐系统限界上下文划分：用户域 / 内容域 / 推荐引擎域
  - Python + TypeScript 双语言完整代码示例
  - Entity vs Value Object 判断口诀、DDD 自检清单
  - 学习路径总览新增第四阶段后半段：DDD 专题

- 2026-03-24：新增《CQRS模式与读写分离实战》
  - CQRS核心理念、两种形态详解
  - Python读写分离 Repository 实现
  - TypeScript 完整 CQRS 架构实现（Command/Query/Handler/EventBus）
  - 推荐系统三大实战场景（行为事件处理、缓存、实时分析分离）
  - 面试表达模板

- 2026-03-23：初始版本创建
  - 学习路径总览
  - MVC/MVVM 详解
  - SOLID 原则详解
  - 代码坏味道识别
  - Python/TypeScript 案例
