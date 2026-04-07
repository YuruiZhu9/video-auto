# 数据质量监控与 ML 流水线可靠性实战

> 推荐系统算法工程师必读：从"训练跑通"到"数据可信"的生产级实践

## 概念解释

### 什么是数据质量？

机器学习模型的效果上限由数据质量决定，而不是模型本身。研究表明，推荐系统中 80% 的效果问题源于数据质量问题，而非算法问题。

数据质量不是"数据有没有"，而是"数据对不对、稳不稳、全不全"。

### 推荐系统数据质量四维度

| 维度 | 定义 | 推荐系统典型问题 | 监控指标 |
|------|------|-----------------|---------|
| **准确性（Accuracy）** | 数据与真实情况的符合程度 | 用户行为打点丢失，导致标签错误 | 标签准确率、召回率 |
| **完整性（Completeness）** | 缺失值、空值的比例 | 画像字段缺失，新用户无行为导致冷启动 | 字段覆盖率、用户画像完整率 |
| **一致性（Consistency）** | 跨系统、跨时间的数据一致性 | 训练特征与服务特征分布不一致（Skew） | 特征分布 PSI、均值偏移 |
| **时效性（Timeliness）** | 数据从产生到可用的延迟 | 实时特征更新延迟，推荐结果过期 | 数据延迟 P99、新内容上线到可推荐时间 |
| **唯一性（Uniqueness）** | 重复数据比例 | 行为日志重复计数，曝光数据去重失效 | 重复率、UV vs PV 比率 |
| **有效性（Validity）** | 数据符合定义的格式/范围 | 评分字段超出 [0,5] 范围、异常大值 | 异常值比例、Schema 违规率 |

### 数据质量 vs 模型质量的区别

```
模型质量：我的模型预测准不准？
  ↓ 这个问题背后往往是 ↓
数据质量：我的训练数据/特征是不是对的？

"模型效果下降"最常见原因：
1. 数据分布变化（用户行为随季节/热点变化）
2. 特征 Skew（训练时和推理时特征不一致）
3. 标签噪声（用户点击不代表真实偏好）
4. 数据泄漏（future information 泄漏到特征中）
```

---

## 代码示例

### 一、数据质量检查框架

#### 反例：裸奔的流水线

```python
# ❌ 问题代码：没有任何数据质量检查
def train_model():
    # 直接读取特征文件，没有任何校验
    features = pd.read_parquet("s3://ml/features/today.parquet")
    labels = pd.read_parquet("s3://ml/labels/today.parquet")
    
    # 缺失值没有检查，可能导致 NaN 传播到模型
    model = xgb.train(features, labels)
    
    # 特征分布变了也不知道，模型可能训偏了
    model.save_model("s3://ml/models/latest")
```

#### 正例：带完整质量门禁的流水线

```python
# ✅ 改进后的代码：每个环节都有质量检查
from dataclasses import dataclass
from typing import Optional
import great_expectations as gx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@dataclass
class DataQualityReport:
    """数据质量报告：所有检查结果汇总"""
    passed: bool
    total_checks: int
    failed_checks: list[str]
    metrics: dict[str, float]
    warnings: list[str]
    timestamp: datetime

class DataQualityChecker:
    """推荐系统数据质量检查器"""
    
    def __init__(self, threshold_config: dict):
        self.threshold = threshold_config
    
    def check_features(self, df: pd.DataFrame, context: str) -> DataQualityReport:
        """检查特征表质量，返回报告"""
        failed_checks = []
        warnings = []
        metrics = {}
        
        # 1. 基础完整性检查
        null_counts = df.isnull().sum()
        null_ratio = null_counts / len(df)
        metrics["null_ratio_max"] = null_ratio.max()
        
        for col, ratio in null_ratio.items():
            if ratio > self.threshold.get("null_ratio_max", 0.1):
                failed_checks.append(f"列 [{col}] 缺失率 {ratio:.2%} 超过阈值 {self.threshold['null_ratio_max']:.2%}")
        
        # 2. 特征值范围检查（防止异常值污染模型）
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ["user_age", "item_price", "exposure_count"]:
                lower = df[col].quantile(0.001)  # 极端分位数
                upper = df[col].quantile(0.999)
                outliers = ((df[col] < lower) | (df[col] > upper)).sum()
                outlier_ratio = outliers / len(df)
                metrics[f"{col}_outlier_ratio"] = outlier_ratio
                
                if outlier_ratio > self.threshold.get("outlier_ratio_max", 0.005):
                    failed_checks.append(f"[{col}] 极端值比例 {outlier_ratio:.2%} 超过阈值")
                    warnings.append(f"[{col}] 建议人工排查异常来源（爬虫/系统错误）")
        
        # 3. 数据延迟检查（时效性）
        if "timestamp" in df.columns:
            latest_ts = pd.to_datetime(df["timestamp"]).max()
            now = datetime.now()
            lag = (now - latest_ts).total_seconds() / 60  # 分钟
            metrics["data_lag_minutes"] = lag
            
            if lag > self.threshold.get("max_lag_minutes", 60):
                failed_checks.append(f"数据延迟 {lag:.1f} 分钟，超过阈值 {self.threshold['max_lag_minutes']} 分钟")
        
        # 4. 数据量突变检查（同比/环比）
        if "date" in df.columns:
            today_count = len(df[df["date"] == df["date"].max()])
            yesterday_count = len(df[df["date"] == df["date"].max() - timedelta(days=1)])
            
            if yesterday_count > 0:
                change_ratio = abs(today_count - yesterday_count) / yesterday_count
                metrics["daily_change_ratio"] = change_ratio
                
                if change_ratio > self.threshold.get("max_daily_change_ratio", 0.5):
                    failed_checks.append(f"数据量日环比变化 {change_ratio:.1%}，可能存在数据问题")
        
        # 5. 重复记录检查（唯一性）
        dup_ratio = df.duplicated().mean()
        metrics["duplicate_ratio"] = dup_ratio
        
        if dup_ratio > self.threshold.get("duplicate_ratio_max", 0.01):
            failed_checks.append(f"重复记录比例 {dup_ratio:.2%} 超过阈值")
        
        passed = len(failed_checks) == 0
        return DataQualityReport(
            passed=passed,
            total_checks=len(failed_checks) + len(warnings) + 5,
            failed_checks=failed_checks,
            metrics=metrics,
            warnings=warnings,
            timestamp=datetime.now()
        )


class MLDataPipeline:
    """带质量门禁的 ML 数据流水线"""
    
    def __init__(self):
        self.quality_checker = DataQualityChecker({
            "null_ratio_max": 0.1,
            "outlier_ratio_max": 0.005,
            "max_lag_minutes": 60,
            "max_daily_change_ratio": 0.5,
            "duplicate_ratio_max": 0.01,
        })
    
    def train_model(self, feature_path: str, label_path: str) -> bool:
        """带质量门禁的模型训练流程"""
        features = pd.read_parquet(feature_path)
        labels = pd.read_parquet(label_path)
        
        # 质量检查
        report = self.quality_checker.check_features(features, "training_features")
        
        # 发送报告到监控系统
        self._report_to_monitoring(report, "training_features")
        
        if not report.passed:
            # 严重问题：阻塞流水线，发送告警
            self._send_alert(report)
            raise DataQualityError(f"数据质量检查失败: {report.failed_checks}")
        
        if report.warnings:
            # 警告：记录但不阻塞，通知算法工程师
            self._send_warning(report)
        
        # 质量通过后，再进行模型训练
        model = self._train(features, labels)
        
        # 记录本次质量指标（供下次对比）
        self._save_quality_metrics(report)
        
        return True


class DataQualityError(Exception):
    """数据质量异常：流水线必须停止"""
    pass
```

---

### 二、训练-服务一致性 Skew 检测

Skew 是推荐系统最隐蔽的数据质量问题：模型在训练时用的特征分布和在线服务时不一样，导致模型学到的规律在服务时失效。

#### 反例：不知道存在 Skew

```python
# ❌ 问题：训练和服务用不同特征，工程团队和算法团队各改各的
# training_pipeline.py
def extract_user_features(user_id: int) -> dict:
    # 训练时用 Spark/Hive 批处理，特征是 T-1 的快照
    user = spark.sql(f"SELECT * FROM user_features WHERE date = 'T-1'")
    return user.to_dict()

# serving_service.py  
def get_user_features(user_id: int) -> dict:
    # 服务时用 MySQL 在线查询，可能拿到实时更新的特征
    user = mysql.query("SELECT * FROM user_features WHERE user_id = ?", user_id)
    return user.to_dict()
    # ⚠️ T-1 的 batch 特征 vs 实时更新的在线特征，分布可能差很多！
```

#### 正例：训练-服务一致性保障

```python
from dataclasses import dataclass
from typing import Protocol
import numpy as np

@dataclass
class FeatureSignature:
    """特征签名：训练和服务用同一个签名，检测 Skew"""
    name: str
    dtype: str
    value_range: tuple[float, float]  # min, max
    null_ratio: float
    mean: float
    std: float
    distribution: str  # "normal" / "uniform" / "skewed"
    
    def equals(self, other: "FeatureSignature", tolerance: float = 0.1) -> bool:
        """两个签名对比，返回差异"""
        diff = {
            "mean_shift": abs(self.mean - other.mean) / (self.std + 1e-6),
            "std_ratio": max(self.std, other.std) / (min(self.std, other.std) + 1e-6),
            "range_change": (
                abs(self.value_range[0] - other.value_range[0]) +
                abs(self.value_range[1] - other.value_range[1])
            ) / (self.value_range[1] - self.value_range[0] + 1e-6),
            "null_ratio_change": abs(self.null_ratio - other.null_ratio),
        }
        return diff


class FeatureMonitor:
    """特征分布监控器：检测训练-服务 Skew"""
    
    def __init__(self, alert_threshold: float = 0.3):
        self.alert_threshold = alert_threshold
        self._training_signatures: dict[str, FeatureSignature] = {}
        self._serving_signatures: dict[str, FeatureSignature] = {}
    
    def record_training_distribution(self, df: pd.DataFrame):
        """记录训练时的特征分布"""
        for col in df.columns:
            self._training_signatures[col] = self._compute_signature(df[col])
    
    def record_serving_distribution(self, df: pd.DataFrame):
        """记录服务时的特征分布（在线采样）"""
        for col in df.columns:
            self._serving_signatures[col] = self._compute_signature(df[col])
    
    def _compute_signature(self, series: pd.Series) -> FeatureSignature:
        s = series.dropna()
        return FeatureSignature(
            name=series.name,
            dtype=str(s.dtype),
            value_range=(s.min(), s.max()),
            null_ratio=series.isnull().mean(),
            mean=s.mean(),
            std=s.std(),
            distribution=self._detect_distribution(s),
        )
    
    def _detect_distribution(self, s: pd.Series) -> str:
        """简单判断分布类型"""
        skewness = s.skew()
        if abs(skewness) < 0.5:
            return "normal"
        elif skewness > 1:
            return "right_skewed"
        else:
            return "left_skewed"
    
    def compute_skew_report(self) -> dict:
        """计算 Skew 报告"""
        report = {}
        all_features = set(self._training_signatures) | set(self._serving_signatures)
        
        for feat_name in all_features:
            train_sig = self._training_signatures.get(feat_name)
            serve_sig = self._serving_signatures.get(feat_name)
            
            if not train_sig or not serve_sig:
                report[feat_name] = {"status": "missing", "severity": "warning"}
                continue
            
            mean_shift = abs(train_sig.mean - serve_sig.mean) / (train_sig.std + 1e-6)
            std_ratio = max(train_sig.std, serve_sig.std) / (min(train_sig.std, serve_sig.std) + 1e-6)
            
            # PSI (Population Stability Index) - 业界标准
            psi = self._compute_psi(
                train_sig.mean, train_sig.std,
                serve_sig.mean, serve_sig.std
            )
            
            skew_score = max(mean_shift, std_ratio - 1, psi)
            
            report[feat_name] = {
                "status": "critical" if skew_score > self.alert_threshold else "ok",
                "severity": skew_score,
                "mean_shift": mean_shift,
                "std_ratio": std_ratio,
                "psi": psi,
                "train_mean": train_sig.mean,
                "serve_mean": serve_sig.mean,
            }
        
        return report
    
    def _compute_psi(self, train_mean: float, train_std: float,
                     serve_mean: float, serve_std: float) -> float:
        """简化 PSI 计算（实际应使用分桶方式）"""
        combined_std = (train_std + serve_std) / 2
        if combined_std < 1e-6:
            return 0.0
        
        # 简化为均值偏移的 PSI 类指标
        diff = abs(serve_mean - train_mean) / combined_std
        return min(diff / 10, 1.0)  # 归一化到 [0, 1]


# 使用示例
def skew_detection_pipeline():
    monitor = FeatureMonitor(alert_threshold=0.3)
    
    # 训练时记录特征分布
    train_features = pd.read_parquet("s3://ml/features/train.parquet")
    monitor.record_training_distribution(train_features)
    
    # 服务时（每分钟采样）记录特征分布
    serving_features = get_online_features_sample()  # 在线采样
    monitor.record_serving_distribution(serving_features)
    
    # 生成 Skew 报告
    report = monitor.compute_skew_report()
    
    for feat_name, result in report.items():
        if result["status"] == "critical":
            send_alert(f"⚠️ 特征 [{feat_name}] 存在严重 Skew: 均值偏移 {result['mean_shift']:.2f}σ")
    
    return report
```

---

### 三、标签质量监控

推荐系统的标签（点击、购买、评分）往往充满噪声。用户在推荐页的点击不一定代表真实偏好，可能是因为位置靠前（位置偏差）、因为好奇点进来（好奇偏差）、或者误触。

#### 正例：标签质量监控系统

```python
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

@dataclass
class LabelQualityMetrics:
    """标签质量指标"""
    total_samples: int
    click_through_rate: float
    position_bias_score: float  # 位置偏差分数
    novelty_ratio: float         # 推荐新颖度
    coverage: float               # 覆盖率（新物品被推荐的比例）
    timestamp: datetime

class LabelQualityMonitor:
    """推荐系统标签质量监控"""
    
    def __init__(self):
        self._historical_ctr: dict[str, list[float]] = defaultdict(list)
    
    def compute_label_metrics(
        self,
        logs: pd.DataFrame,  # 含 user_id, item_id, click, position, recommend_time
    ) -> LabelQualityMetrics:
        
        total = len(logs)
        
        # 1. 基础 CTR
        ctr = logs["click"].mean()
        
        # 2. 位置偏差分析（Position Bias）
        # 理论：如果没有位置偏差，不同位置的 CTR 应该接近
        position_ctrs = logs.groupby("position")["click"].mean()
        
        # 计算第一位的 CTR vs 其他位置 CTR 的比值
        if 1 in position_ctrs.index and len(position_ctrs) > 1:
            first_pos_ctr = position_ctrs[1]
            other_pos_ctr = position_ctrs[position_ctrs.index > 1].mean()
            position_bias = first_pos_ctr / (other_pos_ctr + 1e-6)
        else:
            position_bias = 1.0
        
        # 3. 新颖度（Novelty）：推荐列表中有多少是用户历史未交互过的
        user_interacted = set(
            logs.groupby("user_id")["item_id"].apply(set)
        )
        
        novelty_scores = []
        for user_id, items in logs.groupby("user_id")["item_id"]:
            interacted = user_interacted.get(user_id, set())
            novelty = len([i for i in items if i not in interacted]) / len(items)
            novelty_scores.append(novelty)
        
        novelty_ratio = sum(novelty_scores) / len(novelty_scores)
        
        # 4. 覆盖率（Coverage）：多少比例的候选物品被推荐过
        all_items = logs["item_id"].nunique()
        recommended_items = logs["item_id"].nunique()
        coverage = recommended_items / all_items  # 理想值 > 0.1
        
        # 5. CTR 趋势监控（同比/环比）
        self._historical_ctr["global"].append(ctr)
        ctr_trend = "stable"
        if len(self._historical_ctr["global"]) >= 7:
            recent = self._historical_ctr["global"][-7:]
            if all(x > y * 1.5 for x, y in zip(recent[1:], recent[:-1])):
                ctr_trend = "spike"  # CTR 暴涨，可能刷量或作弊
            elif all(x < y * 0.5 for x, y in zip(recent[1:], recent[:-1])):
                ctr_trend = "drop"   # CTR 暴跌，可能是产品变化或数据问题
        
        return LabelQualityMetrics(
            total_samples=total,
            click_through_rate=ctr,
            position_bias_score=position_bias,
            novelty_ratio=novelty_ratio,
            coverage=coverage,
            timestamp=datetime.now()
        )
    
    def detect_label_anomalies(self, metrics: LabelQualityMetrics,
                                thresholds: dict) -> list[str]:
        """检测标签异常"""
        alerts = []
        
        # CTR 异常检测
        if metrics.position_bias_score > thresholds.get("position_bias_max", 3.0):
            alerts.append(
                f"🔴 位置偏差严重：第一坑 CTR 是其他位置的 {metrics.position_bias_score:.1f} 倍"
                " → 建议：使用 Position Debiasing 或 Causal Inference 校正"
            )
        
        if metrics.novelty_ratio < thresholds.get("novelty_min", 0.3):
            alerts.append(
                f"🟡 推荐新颖度偏低（{metrics.novelty_ratio:.1%}）："
                " 推荐结果过于集中，可能导致信息茧房"
            )
        
        if metrics.coverage < thresholds.get("coverage_min", 0.05):
            alerts.append(
                f"🟡 覆盖率偏低（{metrics.coverage:.1%}）："
                " 仅少量物品被推荐，冷门物品无法曝光"
            )
        
        return alerts
```

---

### 四、Pipeline 可靠性：自动化重试 + 断点续传

推荐系统的每日训练 pipeline 通常依赖多个数据源，任何一个数据源延迟都会导致整个流水线失败。需要设计可靠的流水线架构。

#### 正例：带断点续传的数据流水线

```python
import asyncio
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime, timedelta
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class PipelineTask:
    """流水线任务：支持重试和断点续传"""
    task_id: str
    step: str
    input_path: str
    output_path: str
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    retry_delay_seconds: int = 300  # 5分钟
    error_message: str = ""
    completed_at: Optional[datetime] = None
    
    @property
    def can_retry(self) -> bool:
        return self.attempts < self.max_attempts and self.status == TaskStatus.FAILED


class PipelineScheduler:
    """推荐系统每日训练流水线调度器"""
    
    def __init__(self, checkpoint_dir: str = "/tmp/pipeline_checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def _load_checkpoint(self, date: str) -> dict[str, TaskStatus]:
        """加载断点：哪些步骤已经完成"""
        checkpoint_file = self.checkpoint_dir / f"{date}.json"
        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                return json.load(f)
        return {}
    
    def _save_checkpoint(self, date: str, status: dict):
        """保存断点"""
        checkpoint_file = self.checkpoint_dir / f"{date}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(status, f, indent=2, default=str)
    
    async def run_daily_pipeline(self, date: str):
        """每日训练流水线（带断点续传）"""
        pipeline_steps = [
            ("extract_features", self.extract_features),
            ("extract_labels", self.extract_labels),
            ("join_train_data", self.join_train_data),
            ("train_model", self.train_model),
            ("evaluate_model", self.evaluate_model),
            ("upload_model", self.upload_model),
        ]
        
        checkpoint = self._load_checkpoint(date)
        
        for step_name, step_func in pipeline_steps:
            if step_name in checkpoint and checkpoint[step_name] == "completed":
                print(f"⏭️  [{step_name}] 已完成，跳过")
                continue
            
            task = PipelineTask(
                task_id=f"{date}_{step_name}",
                step=step_name,
                input_path=f"s3://ml/{date}/{step_name}_input",
                output_path=f"s3://ml/{date}/{step_name}_output",
            )
            
            success = await self._run_step_with_retry(task, step_func)
            
            if success:
                checkpoint[step_name] = "completed"
                self._save_checkpoint(date, checkpoint)
            else:
                # 严重错误：发送告警，停止流水线
                await self._send_pipeline_failure_alert(task)
                raise PipelineError(f"步骤 [{step_name}] 多次重试后仍然失败")
    
    async def _run_step_with_retry(self, task: PipelineTask, step_func) -> bool:
        """带重试的任务执行"""
        while task.can_retry:
            try:
                task.status = TaskStatus.RUNNING
                task.attempts += 1
                
                print(f"▶️  执行 [{task.step}] 第 {task.attempts} 次尝试")
                result = await asyncio.wait_for(
                    step_func(task),
                    timeout=timedelta(hours=2)  # 单步超时2小时
                )
                
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                print(f"✅ [{task.step}] 完成")
                return True
                
            except asyncio.TimeoutError:
                task.error_message = f"执行超时（{task.attempts}/{task.max_attempts}）"
                print(f"⏰ [{task.step}] 超时，等待重试...")
                
            except DataQualityError as e:
                task.error_message = str(e)
                print(f"⚠️ [{task.step}] 数据质量错误，不重试，直接失败: {e}")
                task.status = TaskStatus.FAILED
                return False
                
            except Exception as e:
                task.error_message = str(e)
                task.status = TaskStatus.FAILED
                print(f"❌ [{task.step}] 失败: {e}")
            
            if task.can_retry:
                task.status = TaskStatus.RETRYING
                await asyncio.sleep(task.retry_delay_seconds)
        
        return False
    
    async def _send_pipeline_failure_alert(self, task: PipelineTask):
        """流水线失败告警"""
        print(f"🚨🚨🚨 流水线失败告警")
        print(f"  任务: {task.task_id}")
        print(f"  错误: {task.error_message}")
        print(f"  重试次数: {task.attempts}/{task.max_attempts}")


class PipelineError(Exception):
    """流水线执行异常"""
    pass
```

---

## 推荐系统数据质量全景监控架构

```
┌──────────────────────────────────────────────────────────────────┐
│               推荐系统数据质量全景监控架构                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  数据源层                                                         │
│  ├── 用户行为日志（Kafka）→ 完整性检查 + 重复检测                   │
│  ├── 物品特征表（MySQL/Hive）→ 字段覆盖率 + 范围检查                  │
│  ├── 用户画像（Redis/MySQL）→ 实时性检查 + 一致性检查                 │
│  └── 训练特征表（Parquet/S3）→ Skew 检测 + 分布检查                  │
│           ↓                                                        │
│  质量检查层（Great Expectations + 自定义规则）                        │
│  ├── 准确性：标签质量、Skew 检测、异常值检测                         │
│  ├── 完整性：字段覆盖率、记录数基线                                 │
│  ├── 时效性：数据延迟监控（P99 < 30min）                            │
│  ├── 一致性：PSI 分布偏移告警（> 0.2 → 告警）                       │
│  └── 唯一性：重复记录检测                                          │
│           ↓                                                        │
│  告警层                                                           │
│  ├── Critical（阻止训练）：数据缺失超过阈值 / 严重 Skew              │
│  ├── Warning（通知人工）：轻微偏移 / 趋势异常                        │
│  └── Info（记录）：每日质量报告                                     │
│           ↓                                                        │
│  仪表盘（Grafana）                                                │
│  ├── 数据质量健康度仪表盘（综合得分 0-100）                         │
│  ├── 各特征分布趋势图（均值/标准差随时间变化）                        │
│  ├── Pipeline 执行状态看板（每日流水线进度）                         │
│  └── 标签质量看板（CTR / 位置偏差 / 覆盖率 / 新颖度）                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 推荐系统数据质量检查清单

### 每日检查（自动化 + 人工巡检）

| 检查项 | 指标 | 阈值 | 应对措施 |
|--------|------|------|---------|
| 行为日志数据量 | 日曝光/点击量 | 环比波动 < ±30% | 检查上游打点 SDK |
| 用户画像完整率 | 画像字段覆盖率 | > 90% | 触发画像补全任务 |
| 物品特征延迟 | T+1 特征更新延迟 | < 60min | 检查 ETL 任务 |
| 训练-服务 Skew | PSI | < 0.2 | 重新同步特征 |
| 标签 CTR | 实时 CTR | 同比波动 < ±50% | 检查推荐策略变更 |
| Pipeline 执行 | 每日训练成功率 | > 99% | 自动化重试 + 告警 |

### 上线前检查

| 检查项 | 操作 |
|--------|------|
| 特征一致性 | 训练时记录所有特征的 signature，服务时对比 |
| 标签质量 | 检查 CTR 是否异常（暴涨/暴跌） |
| 冷启动比例 | 新用户/物品占比是否正常 |
| 数据泄漏 | 检查特征中是否包含未来信息 |

---

## 常见误区

### 误区 1：只监控模型离线指标，不监控数据质量

**问题**：AUC 下降了，查算法改了啥，但最后发现是上游数据延迟导致某天训练数据缺失。

**正确做法**：模型离线指标和数据质量指标一起监控，出现波动时先排查数据。

### 误区 2：Skew 只在模型效果差时才开始查

**问题**：Skew 是慢性病，等发现时模型已经训歪了很久。

**正确做法**：建立 Skew 监控的日常巡检制度，PSI 超过阈值自动告警。

### 误区 3：缺失值直接用 0 或均值填充，不记录

**问题**：模型会学到"缺失 = 0"的规律，但实际缺失可能代表另一种含义（比如新用户没有历史行为）。

**正确做法**：用 Missing Indicator 特征显式标记缺失，让模型自己学。

### 误区 4：Pipeline 没有断点，失败后从头重跑

**问题**：数据量大时，从头重跑耗时长，可能导致模型发布延迟。

**正确做法**：每个步骤保存 checkpoint，支持断点续传。

### 误区 5：标签只看点击，不看其他信号

**问题**：点击不等于喜欢（Position Bias），只看点击可能导致推荐越来越极端。

**正确做法**：结合停留时长、收藏、分享等多信号综合评估标签质量。

---

## 适用场景

- **模型训练前**：必须进行数据质量检查，不合格则阻断流水线
- **日常监控**：建立数据质量仪表盘，及时发现数据问题
- **模型效果下降排查**：先查数据质量，再查算法问题（节省 80% 排查时间）
- **新特征上线**：监控新特征的质量（覆盖率、分布、与其他特征的相关性）
- **Pipeline 可靠性**：确保每日训练流水线稳定运行，支持断点续传

---

## 本章总结

```
数据质量监控的本质 = 三件事

1️⃣  知道"对"是什么 → 建立 Baseline（正常时的特征分布/数据量/质量指标）
2️⃣  知道"错"是什么 → 设置阈值（PSI > 0.2 / 缺失率 > 10% / 延迟 > 60min）
3️⃣  快速响应 → 自动化 + 告警 + 断点续传

推荐系统数据质量特殊性：
- 实时性要求高（用户行为 → 特征更新 → 推荐生效，越快越好）
- 标签噪声大（点击 ≠ 喜欢，需要去偏）
- 分布漂移快（热点事件、季节性导致用户行为变化）
- Skew 隐蔽（训练和服务特征分布不一致，模型习得错误规律）
```

---

**关联知识点**：

- [特征工程架构与 FeatureStore 实战](特征工程架构与FeatureStore实战.md) — 特征是数据质量的直接载体
- [可观测性实战：日志·指标·链路追踪](可观测性实战：日志指标链路追踪.md) — 数据质量监控是可观测性的核心应用
- [技术债识别与偿还策略](技术债识别与偿还策略.md) — 数据债务是技术债的重要组成部分
