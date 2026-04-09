# MLOps 端到端流水线实战：推荐系统从训练到上线

> 推荐系统上线容易，持续稳定地迭代模型难。MLOps 就是解决这个问题的工程实践。

---

## 概念解释

### 什么是 MLOps？

MLOps = Machine Learning + Operations。把 DevOps 的"持续集成/持续部署"思想应用到机器学习系统：

```
DevOps:  代码 → 构建 → 测试 → 部署 → 监控
MLOps:   数据 → 特征 → 训练 → 评估 → 部署 → 监控
              ↑__________________↑（数据闭环）
```

**推荐系统 MLOps 的特殊性**：
- 数据即产品：用户行为每天变化，模型需定期/持续更新
- 线上线下一致性：训练特征和推理特征必须一致（Skew 是最大敌人）
- 多阶段流水线：召回→排序→重排，每个阶段都可能独立迭代
- 业务指标敏感：CTR/CVR 直接影响 GMV，上线有压力

### MLOps 三级别（Google 分类）

| 级别 | 描述 | 适用场景 | 推荐系统 |
|------|------|---------|---------|
| **Level 0：手工** | 手动训练+手动部署，脚本驱动 | PoC 项目 | 早期验证 |
| **Level 1：自动化训练** | 训练流程自动化，触发式部署 | 成熟业务 | 定期批量训练 |
| **Level 2：CI/CD 自动化** | 代码+数据双触发，持续部署模型 | 大规模推荐系统 | ✅ 推荐系统目标 |

---

## 推荐系统 MLOps 完整架构图

```
┌─────────────────────────────────────────────────────────┐
│                    推荐系统 MLOps 全景                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  【数据层】          【特征层】         【模型层】          │
│  MySQL行为数据  →  Feature Store  →  模型训练（JOB）      │
│  Kafka实时事件       (Feast)            │               │
│  Hive历史数据        Redis缓存         ↓               │
│                          ↑         Model Registry     │
│                          │              │             │
│  【触发层】           【服务层】         ↓               │
│  Cron定时任务    ←  Recall→Rank→Rerank  ←  K8s Deployment│
│  Kafka事件触发    Flask/FastAPI       Triton/vLLM     │
│  手动触发                                          │      │
│                                    【监控层】            │
│                              Prometheus ← Metrics     │
│                              Grafana ← 看板            │
│                              告警 → 钉钉/企微            │
└─────────────────────────────────────────────────────────┘
```

---

## 一、ML 流水线框架选型

### 主流框架对比

| 框架 | 定位 | 优点 | 缺点 | 推荐场景 |
|------|------|------|------|---------|
| **MLflow** | 实验跟踪 + 模型注册 | 轻量、易上手、模型版本管理强 | Pipeline 功能弱 | 中小型推荐系统 |
| **Kubeflow Pipelines** | 云原生流水线 | 与 K8s 深度集成、可视化强 | 部署复杂 | 大规模生产环境 |
| **Metaflow** | 数据科学家友好 | Python 优先，Netflix 出品 | 社区较小 | 快速迭代团队 |
| **Airflow** | 通用调度 | 成熟、生态丰富 | 不是为 ML 设计 | 已有 Airflow 的团队 |
| **ZenML** | MLOps 框架 | 开源、Pipeline 可移植 | 较新 | 想标准化 MLOps 的团队 |

**推荐系统选型建议**：
- 0→1 阶段：**MLflow**（轻量，先跑通流程）
- 1→10 阶段：**MLflow + Airflow**（实验管理 + 调度）
- 10→100 阶段：**Kubeflow Pipelines**（大规模训练 + 云原生）

---

## 二、模型训练流水线实战

### Level 1：自动化训练流水线（Python + MLflow）

**目录结构**：
```
recommendation-ml/
├── ml_pipeline/
│   ├── __init__.py
│   ├── config.py          # 训练配置
│   ├── data_loader.py     # 数据加载
│   ├── feature_engineering.py  # 特征工程
│   ├── trainer.py         # 训练器
│   ├── evaluator.py       # 评估器
│   └── pipeline.py        # 流水线编排
├── train.py               # 入口脚本
└── requirements.txt
```

**配置管理（config.py）**：
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TrainingConfig:
    """训练配置：所有超参数集中管理"""
    # 数据源
    train_data_path: str = "/data/hive/behavior/train.parquet"
    val_data_path: str = "/data/hive/behavior/val.parquet"

    # 特征配置
    user_features: list[str] = None
    item_features: list[str] = None
    context_features: list[str] = None

    # 模型超参数
    model_type: str = "deepfm"  # deepfm / din / mmoe
    embedding_dim: int = 64
    learning_rate: float = 0.001
    batch_size: int = 4096
    epochs: int = 10
    early_stop_patience: int = 3

    # 训练资源
    gpus: int = 1
    workers: int = 8

    # 评估指标
    metrics: list[str] = None  # ["auc", "ctr", "stay_time"]

    def __post_init__(self):
        if self.user_features is None:
            self.user_features = ["age", "gender", "city_level", "user_level"]
        if self.item_features is None:
            self.item_features = ["category_id", "brand_id", "price_level"]
        if self.context_features is None:
            self.context_features = ["hour", "day_of_week", "is_weekend"]
        if self.metrics is None:
            self.metrics = ["auc", "ctr"]


config = TrainingConfig()
```

**特征工程（feature_engineering.py）**：
```python
import pandas as pd
import numpy as np
from typing import Optional
from pyspark.sql import DataFrame


class FeatureEngineering:
    """推荐系统特征工程：用户/物品/上下文/交叉特征"""

    def __init__(self, config: TrainingConfig):
        self.config = config

    def build_user_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """用户基础特征 + 统计特征"""
        user_stats = df.groupby("user_id").agg(
            click_cnt=("behavior", lambda x: (x == "click").sum()),
            cart_cnt=("behavior", lambda x: (x == "cart").sum()),
            buy_cnt=("behavior", lambda x: (x == "buy").sum()),
            avg_stay_time=("stay_seconds", "mean"),
            last_visit_gap=("timestamp", lambda x: x.diff().mean()),
        ).reset_index()

        # 行为比率特征（推荐系统核心）
        user_stats["ctr"] = user_stats["click_cnt"] / (user_stats["click_cnt"] + 1)
        user_stats["cvr"] = user_stats["buy_cnt"] / (user_stats["click_cnt"] + 1)

        return user_stats

    def build_context_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """上下文特征：时间节假日等"""
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        df["is_night"] = ((df["hour"] >= 22) | (df["hour"] <= 7)).astype(int)
        return df

    def build_cross_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """交叉特征：用户×类目偏好"""
        # 用户-类目点击交叉统计
        user_category = df.groupby(["user_id", "category_id"]).agg(
            user_cat_click=("behavior", lambda x: (x == "click").sum())
        ).reset_index()

        # 拼接回原表
        df = df.merge(user_category, on=["user_id", "category_id"], how="left")
        df["user_cat_click"] = df["user_cat_click"].fillna(0)
        return df
```

**训练器（trainer.py）**：
```python
import mlflow
import torch
from pathlib import Path
from typing import Optional


class ModelTrainer:
    """模型训练器：支持 DeepFM/DIN/MMoE，自动记录 MLflow"""

    def __init__(self, config, experiment_name: str = "recommendation"):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        mlflow.set_experiment(experiment_name)

    def train(self, model, train_loader, val_loader) -> dict:
        """完整训练流程 + MLflow 自动记录"""
        mlflow.start_run(run_name=f"{self.config.model_type}_{self._timestamp()}")

        try:
            # 记录超参数
            mlflow.log_params({
                "model_type": self.config.model_type,
                "embedding_dim": self.config.embedding_dim,
                "learning_rate": self.config.learning_rate,
                "batch_size": self.config.batch_size,
                "epochs": self.config.epochs,
            })

            optimizer = torch.optim.Adam(model.parameters(), lr=self.config.learning_rate)
            criterion = torch.nn.BCEWithLogitsLoss()

            best_auc = 0.0
            patience_counter = 0
            best_model_state = None

            for epoch in range(self.config.epochs):
                # 训练
                model.train()
                train_loss = 0.0
                for batch in train_loader:
                    optimizer.zero_grad()
                    inputs, labels = batch
                    outputs = model(inputs.to(self.device))
                    loss = criterion(outputs, labels.to(self.device))
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()

                # 验证
                model.eval()
                val_metrics = self._evaluate(model, val_loader)

                # 记录指标
                mlflow.log_metrics({
                    "train_loss": train_loss / len(train_loader),
                    "val_auc": val_metrics["auc"],
                    "val_ctr": val_metrics["ctr"],
                    "epoch": epoch,
                })

                # Early stopping
                if val_metrics["auc"] > best_auc:
                    best_auc = val_metrics["auc"]
                    best_model_state = model.state_dict().copy()
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= self.config.early_stop_patience:
                        print(f"Early stop at epoch {epoch}")
                        break

            # 保存最优模型到 MLflow
            if best_model_state:
                model.load_state_dict(best_model_state)
            mlflow.pytorch.log_model(model, "model")

            return {"best_auc": best_auc}

        finally:
            mlflow.end_run()

    def _evaluate(self, model, val_loader) -> dict:
        model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in val_loader:
                inputs, labels = batch
                preds = model(inputs.to(self.device))
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.numpy())

        from sklearn.metrics import roc_auc_score
        auc = roc_auc_score(all_labels, all_preds)

        # CTR 预估指标
        ctr_pred = (torch.sigmoid(torch.tensor(all_preds)) > 0.5).float()
        ctr_acc = (ctr_pred == torch.tensor(all_labels)).float().mean()

        return {"auc": auc, "ctr": ctr_acc.item()}
```

### Level 2：完整流水线（pipeline.py + MLflow Projects）

```python
"""ML 流水线：数据加载 → 特征工程 → 训练 → 评估 → 注册"""
from pathlib import Path
import mlflow
from mlflow.tracking import MlflowClient


def run_pipeline(config: TrainingConfig):
    """端到端训练流水线"""
    mlflow.set_experiment("recommendation_pipeline")

    with mlflow.start_run(run_name="daily_training_v1") as run:
        pipeline_run_id = run.info.run_id

        # Step 1: 数据加载
        print("📥 Step 1: 加载数据...")
        train_df = pd.read_parquet(config.train_data_path)
        val_df = pd.read_parquet(config.val_data_path)
        mlflow.log_param("train_size", len(train_df))
        mlflow.log_param("val_size", len(val_df))

        # Step 2: 特征工程
        print("⚙️ Step 2: 特征工程...")
        fe = FeatureEngineering(config)
        train_df = fe.build_user_features(train_df)
        train_df = fe.build_context_features(train_df)
        train_df = fe.build_cross_features(train_df)
        # ... val_df 同理

        # Step 3: 训练
        print("🚀 Step 3: 训练模型...")
        trainer = ModelTrainer(config)
        model = trainer.build_model(config.model_type)
        metrics = trainer.train(model, train_loader, val_loader)

        # Step 4: 注册模型（推送到 Model Registry）
        print("📦 Step 4: 注册模型...")
        model_uri = f"runs:/{pipeline_run_id}/model"
        model_version = mlflow.register_model(model_uri, "recommendation_model")

        # 更新模型描述（打标签）
        client = MlflowClient()
        client.update_model_version(
            name="recommendation_model",
            version=model_version.version,
            description=f"AUC={metrics['best_auc']:.4f}, trained on {config.train_data_path}"
        )

        # 自动将新模型设为 Staging（而非直接 Production）
        client.transition_model_version_stage(
            name="recommendation_model",
            version=model_version.version,
            stage="Staging",
        )

        print(f"✅ 模型已注册: v{model_version.version}, AUC={metrics['best_auc']:.4f}")
        print(f"   下一步: 人工审批 → 部署到 Production")

        return model_version


# MLflow Project 定义（mlflow_project/MLproject）
# 用于 Airflow/Kubeflow 调用
"""
name: recommendation_training
entry_points:
  main:
    command: "python train.py"
  retrain:
    command: "python retrain.py --trigger {trigger_type}"
"""
```

---

## 三、模型服务化与蓝绿部署

### 模型服务三件套

```python
# 模型推理服务（model_serving.py）
import torch
import redis
from functools import lru_cache
from typing import Optional


class ModelServing:
    """模型推理服务：支持热加载、多版本、降级"""

    def __init__(self, model_path: str):
        self.model = None
        self.model_version = None
        self.load_model(model_path)

    def load_model(self, model_path: str):
        """热加载模型（新模型不影响正在处理的请求）"""
        import mlflow
        model_uri = f"models:/recommendation_model/{model_path}"
        self.model = mlflow.pytorch.load_model(model_uri)
        self.model.eval()
        self.model_version = model_path
        print(f"✅ 模型已加载: {model_path}")

    def predict(self, features: dict) -> dict:
        """推理入口：含降级兜底"""
        try:
            with torch.no_grad():
                inputs = self._prepare_inputs(features)
                outputs = self.model(inputs)
                probs = torch.sigmoid(outputs).numpy()
            return {"scores": probs.tolist(), "model_version": self.model_version}
        except Exception as e:
            # 降级策略：返回默认分
            return {"scores": [0.5] * len(features.get("item_ids", [])),
                    "model_version": "fallback",
                    "degraded": True}


class ModelVersionManager:
    """模型版本管理器：支持蓝绿切换"""

    BLUE_KEY = "model:blue"   # 当前生产模型
    GREEN_KEY = "model:green" # 待上线模型

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def deploy_new_model(self, model_version: str, weight: float = 0.0):
        """
        蓝绿部署策略：
        weight=0.0 → 新模型在 Green，待命
        weight=0.1 → 10% 流量切到 Green（金丝雀）
        weight=1.0 → 100% 流量切到 Green（完全切换）
        """
        self.redis.set(self.GREEN_KEY, model_version)
        self.redis.set("model:green_weight", str(weight))
        print(f"🌿 Green 模型已部署 v{model_version}，流量比例 {weight*100:.1f}%")

    def full_switch(self):
        """全量切换：Green → Blue"""
        green_version = self.redis.get(self.GREEN_KEY)
        self.redis.set(self.BLUE_KEY, green_version)
        self.redis.set("model:blue_weight", "1.0")
        print(f"🔵 全量切换到 Blue v{green_version}")

    def rollback(self):
        """回滚：从 Blue 恢复"""
        blue_version = self.redis.get(self.BLUE_KEY)
        self.redis.set(self.GREEN_KEY, blue_version)
        self.redis.set("model:green_weight", "1.0")
        print(f"↩️ 回滚到 Blue v{blue_version}")

    def get_active_model(self) -> str:
        """根据流量权重获取当前模型版本"""
        green_version = self.redis.get(self.GREEN_KEY) or ""
        weight = float(self.redis.get("model:green_weight") or 0.0)

        if weight >= 1.0:
            return green_version
        return self.redis.get(self.BLUE_KEY) or "v1.0"
```

---

## 四、持续训练触发策略

### 四种触发模式

```python
"""
推荐系统模型更新策略：
┌──────────────────┬────────────────────┬─────────────────────────────┐
│ 策略              │ 触发条件            │ 推荐场景                    │
├──────────────────┼────────────────────┼─────────────────────────────┤
│ 定时训练          │ Cron 表达式         │ 特征分布稳定，天级更新       │
│ 数据量阈值触发    │ 新增样本数 ≥ N      │ 新用户/新物品积累足够后训练  │
│ 性能下降监控触发  │ AUC < 基线 - δ      │ 自动应对数据漂移（Drift）   │
│ 手动触发          │ API 调用            │ 紧急上线 / 大促前集中优化   │
└──────────────────┴────────────────────┴─────────────────────────────┘
"""

from dataclasses import dataclass
from enum import Enum


class TriggerType(Enum):
    CRON = "cron"
    DATA_VOLUME = "data_volume"
    PERFORMANCE_DROP = "performance_drop"
    MANUAL = "manual"


@dataclass
class TriggerConfig:
    trigger_type: TriggerType

    # 定时触发配置
    cron_expression: str = "0 2 * * *"  # 每天凌晨2点

    # 数据量触发配置
    min_new_samples: int = 100_000  # 新增10万样本才触发

    # 性能监控配置
    baseline_auc: float = 0.78
    drop_threshold: float = 0.02  # AUC下降超过0.02触发


class TrainingTrigger:
    """训练触发器：根据条件决定是否触发训练"""

    def should_trigger(self, config: TriggerConfig) -> bool:
        if config.trigger_type == TriggerType.CRON:
            # 由 Airflow/Cron 调度器调用
            return True

        elif config.trigger_type == TriggerType.DATA_VOLUME:
            new_samples = self._count_new_samples()
            print(f"新增样本: {new_samples} / {config.min_new_samples}")
            return new_samples >= config.min_new_samples

        elif config.trigger_type == TriggerType.PERFORMANCE_DROP:
            current_auc = self._get_current_online_auc()
            drop = config.baseline_auc - current_auc
            if drop > config.drop_threshold:
                print(f"⚠️ AUC 下降 {drop:.4f}，触发重新训练")
                return True
            return False

        return False

    def _count_new_samples(self) -> int:
        # 从 Hive/Spark 统计新增行为数据量
        return 120_000  # 示例

    def _get_current_online_auc(self) -> float:
        # 从监控系统获取线上 AUC
        return 0.765  # 示例
```

### 数据漂移（Data Drift）检测

```python
"""
推荐系统数据漂移检测：
训练 vs 推理时的特征分布漂移，是模型效果下降的根本原因之一

PSI（Population Stability Index）是最常用的漂移检测指标
PSI < 0.1: 无显著变化
0.1 ≤ PSI < 0.2: 轻微变化，需关注
PSI ≥ 0.2: 显著变化，需重新训练
"""

import numpy as np
import pandas as pd


def calculate_psi(expected: np.array, actual: np.array, buckets: int = 10) -> float:
    """
    计算 PSI：衡量两个分布的差异
    推荐系统用于：特征漂移检测 / 线上线下分布一致性检测
    """
    def _psi_formula(expected_perc, actual_perc):
        # 避免除零
        expected_perc = np.where(expected_perc == 0, 1e-4, expected_perc)
        actual_perc = np.where(actual_perc == 0, 1e-4, actual_perc)
        return np.sum((actual_perc - expected_perc) * np.log(actual_perc / expected_perc))

    # 分箱
    breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
    expected_bins = np.digitize(expected, breakpoints) - 1
    actual_bins = np.digitize(actual, breakpoints) - 1

    expected_perc = np.bincount(expected_bins, minlength=buckets) / len(expected)
    actual_perc = np.bincount(actual_bins, minlength=buckets) / len(actual)

    psi = _psi_formula(expected_perc, actual_perc)
    return psi


class DataDriftDetector:
    """数据漂移检测器：监控推荐系统特征分布"""

    def __init__(self, baseline_df: pd.DataFrame):
        self.baseline = baseline_df
        self.feature_thresholds = {
            "ctr": 0.15,    # CTR 特征 PSI 阈值
            "user_age": 0.1,
            "item_price": 0.1,
            "category_dist": 0.2,
        }

    def check_drift(self, current_df: pd.DataFrame) -> dict:
        """检测所有关键特征的漂移情况"""
        drift_report = {}

        for feature in self.feature_thresholds:
            if feature not in current_df.columns:
                continue
            psi = calculate_psi(
                self.baseline[feature].values,
                current_df[feature].values
            )
            threshold = self.feature_thresholds[feature]
            drift_report[feature] = {
                "psi": psi,
                "status": "🚨 DRIFT" if psi >= threshold else "✅ OK",
                "action": "Retrain" if psi >= threshold else "Continue",
            }

        return drift_report

    def should_retrain(self, drift_report: dict) -> bool:
        """根据漂移报告决定是否触发重新训练"""
        drift_count = sum(1 for v in drift_report.values() if v["action"] == "Retrain")
        return drift_count >= 2  # 超过2个特征漂移 → 触发重训
```

---

## 五、MLOps 工程实践 Checklist

### 训练阶段 ✅

| 检查项 | 标准 | 工具 |
|--------|------|------|
| 数据版本管理 | 每次训练可复现，Hash 可追溯 | DVC / LakeFS |
| 特征一致性 | 训练/推理用同一套特征工程代码 | Feature Store |
| 超参数记录 | 所有超参数自动记录 MLflow | MLflow |
| 评估指标 | AUC/CTR/CVR 多指标评估，不单看一个 | MLflow Metrics |
| Early Stopping | 防止过拟合，Patience 2-3 epoch | PyTorch Lightning |
| 模型版本管理 | 训练完自动注册到 Model Registry | MLflow Registry |

### 部署阶段 ✅

| 检查项 | 标准 | 工具 |
|--------|------|------|
| 灰度发布 | 新模型 5% → 10% → 30% → 100% | 模型版本管理器 |
| 流量对比 | 金丝雀期间新/旧模型 CTR 同时记录 | A/B 测试框架 |
| 自动回滚 | 指标下降超过阈值自动回滚 | 监控系统 + 回滚脚本 |
| 模型热加载 | 不停服加载新模型 | ModelServing |
| 推理性能 | P99 延迟 < 200ms，QPS 满足业务需求 | 性能测试 |
| 降级兜底 | 模型不可用时返回默认策略 | 多级降级 |

### 监控阶段 ✅

| 检查项 | 标准 | 工具 |
|--------|------|------|
| 特征监控 | 每日 PSI 检测，>0.15 触发告警 | 自定义监控 |
| 模型性能监控 | 每日线上 AUC 统计，下降 >2% 告警 | Prometheus Alert |
| 数据质量监控 | 缺失率/异常值/延迟，阈值告警 | DataQualityChecker |
| 模型解释性 | Top-K 推荐有解释，异常case可查 | SHAP / Attention 可视化 |

---

## 六、推荐系统 MLOps 演进路线

```
阶段1（0→1）：手工 ML
  模型迭代靠脚本，训练-部署手动切换，没有监控
  → 用 MLflow 记录实验 + 手动部署脚本

阶段2（1→10）：自动训练
  引入 Airflow 定时调度训练 Job
  模型注册到 MLflow Model Registry
  API 通过环境变量切换模型版本
  → 目标：训练自动化，有基础监控

阶段3（10→100）：MLOps 成熟
  数据漂移自动检测 → 自动触发训练
  金丝雀发布 + 自动回滚
  Feature Store 统一管理特征
  A/B 测试框架 + 模型可解释性
  → 目标：无人值守的持续训练与部署
```

---

## 七、学习目标

- ✅ 能解释 MLOps 三级别，知道自己项目处于哪个阶段
- ✅ 能搭建基于 MLflow 的推荐系统训练流水线
- ✅ 能实现数据漂移检测（PSI 指标），防止模型效果暗降
- ✅ 能设计模型蓝绿部署策略（含灰度切换+自动回滚）
- ✅ 能区分四种训练触发策略，为业务选择合适方案
- ✅ 能制定推荐系统 MLOps Checklist（训练/部署/监控三阶段）

---

## 常见误区

- **误区1**：模型上线后就不管了 → 实际上数据漂移会让模型效果每周都在下降
- **误区2**：训练和推理用两套特征代码 → 导致 Skew，效果差不知道为什么
- **误区3**：每次都全量重训 → 增量训练/在线学习可以更快适应数据变化
- **误区4**：只看离线 AUC → 离线涨不代表线上涨，必须有 A/B 测试
- **误区5**：没有数据版本管理 → 数据变了但训练结果是旧的，无法复现

---

## 相关文档

- [模型服务化架构与推理优化实战](./模型服务化架构与推理优化实战.md) — 模型推理优化细节
- [数据质量监控与 ML 流水线可靠性实战](./数据质量监控与ML流水线可靠性实战.md) — 数据质量门禁
- [自适应架构与系统韧性设计](./自适应架构与系统韧性设计.md) — 自动扩缩容与混沌工程
- [技术债识别与偿还策略](./技术债识别与偿还策略.md) — 何时该重构 MLOps 流水线
