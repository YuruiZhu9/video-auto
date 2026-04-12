# CI/CD 与自动化部署实战：推荐系统从代码到生产

> 🎯 **适用对象**：想把代码工程化能力提升到生产级别的推荐系统算法工程师
> 🎯 **目标**：掌握 GitHub Actions + Docker + K8s 自动化流水线，做到代码提交 → 自动测试 → 自动部署 → 自动监控

---

## 一、CI/CD 核心理念

### 什么是 CI/CD？

| 概念 | 说明 | 推荐系统中的例子 |
|------|------|----------------|
| **CI（持续集成）** | 每次代码提交自动构建、测试 | push 代码 → 自动运行 lint + 单元测试 + 集成测试 |
| **CD（持续交付）** | 自动化把代码送到预生产环境 | 测试通过后自动构建 Docker 镜像，推送到镜像仓库 |
| **持续部署** | 自动化把代码部署到生产环境 | 镜像推送后自动部署到 K8s，支持金丝雀/A/B 测试 |

### 为什么推荐系统需要 CI/CD？

```
手工部署的问题：
❌ 代码改了，测试忘了跑 → 上线后才发现 Bug
❌ 不同环境配置不同 → "在我机器上能跑"
❌ 回滚靠记忆 → 不知道上一个稳定版本是什么
❌ 模型更新需要运维人工操作 → 凌晨 3 点被叫醒

CI/CD 解决的问题：
✅ push 代码自动跑全量测试
✅ 配置随镜像走，环境一致
✅ 版本可追溯，一键回滚
✅ 模型更新自动化，值班告警驱动
```

### CI/CD 流水线全景图

```
代码提交
    ↓
GitHub Actions CI（代码质量门禁）
    ├─ lint（flake8/mypy/ESLint）
    ├─ 单元测试（pytest，Mock 外部依赖）
    ├─ 集成测试（启动真实 MySQL/Redis，测完整链路）
    ├─ 安全扫描（bandit/Trivy 漏洞扫描）
    └─ 构建 Docker 镜像
            ↓
    Docker 镜像推送到仓库（Harbor / ECR / GHCR）
            ↓
    GitHub Actions CD（部署流水线）
        ├─ 部署到 Staging 环境
        ├─ 运行冒烟测试
        ├─ 金丝雀发布（5% 流量）
        ├─ 监控指标对比（新 vs 旧）
        └─ 自动扩量 or 自动回滚
            ↓
    生产环境全量上线
            ↓
    Prometheus + Grafana 持续监控
```

---

## 二、GitHub Actions CI：代码质量门禁

### 基础 Workflow 模板

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Lint with Flake8
        run: |
          flake8 . --max-line-length=120 \
                   --ignore=E501,F401,W503 \
                   --exclude=tests,venv,.git
      
      - name: Type check with MyPy
        run: |
          pip install mypy
          mypy app/ --ignore-missing-imports --warn-unused-configs
      
      - name: Security scan with Bandit
        run: |
          pip install bandit
          bandit -r app/ -f json -o bandit_report.json
      
      - name: Upload Bandit report
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: bandit_report.json

  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test
          MYSQL_DATABASE: test_rec
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
        ports:
          - 3306:3306
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=5s
          --health-timeout=3s
          --health-retries=5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: mysql+aiomysql://root:test@127.0.0.1:3306/test_rec
          REDIS_URL: redis://127.0.0.1:6379/0
        run: |
          pytest tests/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=html \
            --cov-fail-under=70 \
            -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            GITHUB_SHA=${{ github.sha }}
            GITHUB_REF=${{ github.ref }}
```

### Python 依赖管理：`requirements.txt` 示例

```txt
# 推荐系统核心依赖（按环境分离）
# requirements.txt

# Web 框架
fastapi==0.110.0
uvicorn[standard]==0.27.1

# 数据层
sqlalchemy==2.0.27
aiomysql==0.2.0
redis==5.0.1
pymilvus==2.4.0

# ML
numpy==1.26.4
pandas==2.2.1
xgboost==2.0.3
joblib==1.3.2

# 工具
pydantic==2.6.1
pydantic-settings==2.1.0
structlog==24.1.0
httpx==0.27.0

# 测试
pytest==8.0.2
pytest-asyncio==0.23.5
pytest-cov==4.1.0
httpx==0.27.0
fakeredis==2.21.0

# 安全
bandit==1.7.8
safety==3.0.1
```

---

## 三、Docker 最佳实践：推荐系统镜像构建

### 反例：臃肿镜像

```dockerfile
# ❌ 反例：node:18 基础镜像 1.1GB，每次构建慢
FROM node:18

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt    # 混用pip和npm

CMD ["python", "app/main.py"]
```

### 正例：多阶段构建精简镜像

```dockerfile
# ✅ 正例：多阶段构建，最终镜像 ~200MB

# ===== 阶段1：构建阶段 =====
FROM python:3.11-slim AS builder

WORKDIR /build

# 安装构建依赖（不带入最终镜像）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 单独安装依赖（可缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ===== 阶段2：运行阶段 =====
FROM python:3.11-slim

# 安全：创建非 root 用户
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# 只复制必要文件
COPY --from=builder /root/.local /app/.local
COPY app/ ./app/
COPY config/ ./config/

# 设置环境变量
ENV PATH=/app/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安全：切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000

# 使用 uvicorn（支持 worker 管理）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### `.dockerignore`：减少构建上下文

```gitignore
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
.git
.gitignore
.env
.venv
venv/
tests/
docs/
*.md
.pytest_cache
.coverage
htmlcov/
*.log
Dockerfile
docker-compose.yml
.github/
```

---

## 四、GitHub Actions CD：自动化部署流水线

### 推荐系统完整 CD Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success'
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_branch }}
      
      - name: Pull image
        run: |
          docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
      
      - name: Deploy to Staging
        run: |
          kubectl config use-context staging
          
          # 使用 helm chart 部署（或直接 kubectl）
          helm upgrade --install rec-system-staging \
            ./k8s/rec-system \
            --namespace rec-staging \
            --set image.tag=${{ github.sha }} \
            --wait --timeout 5m \
            --rollback
      
      - name: Run smoke tests
        run: |
          sleep 10  # 等待 Pod 启动
          
          STAGING_URL="https://rec-staging.example.com"
          
          # 健康检查
          curl -sf "${STAGING_URL}/health" || exit 1
          
          # 功能冒烟测试
          curl -sf "${STAGING_URL}/api/v1/recommend?user_id=123&scene=home" \
            | jq -e '.items | length > 0' || exit 1
          
          echo "✅ Staging 冒烟测试通过"

  canary-deploy:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
      
      - name: Deploy Canary (5% 流量)
        run: |
          kubectl config use-context production
          
          # 金丝雀发布：同时运行新旧两个版本
          # 老版本：现有 Deployment，不变
          # 新版本：金丝雀 Deployment，5% 流量
          kubectl set image deployment/rec-system-canary \
            rec-system=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n rec-production
          
          # 更新 HPA，扩容金丝雀
          kubectl scale deployment rec-system-canary \
            --replicas=1 -n rec-production
          
          # 等待金丝雀 Pod ready
          kubectl wait --for=condition=available \
            --timeout=300s deployment/rec-system-canary -n rec-production
      
      - name: Monitor Canary metrics
        run: |
          echo "⏳ 等待 5 分钟，观察金丝雀指标..."
          sleep 300
          
          # 从 Prometheus 查询新版本错误率
          ERROR_RATE=$(curl -s \
            "http://prometheus:9090/api/v1/query" \
            --data-urlencode 'query=rate(http_requests_total{service="canary",status=~"5.."}[5m])' \
            | jq -r '.data.result[0].value[1] // "0"')
          
          echo "金丝雀 5xx 错误率: ${ERROR_RATE}"
          
          if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
            echo "❌ 错误率过高，自动回滚"
            kubectl rollout undo deployment/rec-system-canary -n rec-production
            exit 1
          fi
          
          echo "✅ 金丝雀指标正常，扩量到 30%"

  full-deploy:
    needs: canary-deploy
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Full rollout (100%)
        run: |
          kubectl config use-context production
          
          # 滚动更新主版本
          kubectl set image deployment/rec-system \
            rec-system=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n rec-production
          
          kubectl rollout status deployment/rec-system \
            -n rec-production --timeout=600s
          
          # 清理金丝雀
          kubectl delete deployment rec-system-canary -n rec-production
          
          echo "🎉 生产环境全量部署完成"

  notify:
    needs: [canary-deploy, full-deploy]
    runs-on: ubuntu-latest
    steps:
      - name: Notify on success
        if: needs.full-deploy.result == 'success'
        run: |
          echo "🎉 推荐系统已部署到生产环境，版本: ${{ github.sha }}"
          # 发送钉钉/飞书通知
          curl -X POST "${{ secrets.DINGTALK_WEBHOOK }}" \
            -H "Content-Type: application/json" \
            -d '{"msgtype":"text","text":{"content":"✅ 推荐系统已上线，版本: '${{ github.sha }}'"}}'
      
      - name: Notify on failure
        if: needs.full-deploy.result == 'failure'
        run: |
          echo "❌ 部署失败，已自动回滚"
          curl -X POST "${{ secrets.DINGTALK_WEBHOOK }}" \
            -H "Content-Type: application/json" \
            -d '{"msgtype":"text","text":{"content":"🚨 推荐系统部署失败，请检查！"}}'
```

---

## 五、K8s 部署配置：推荐系统生产级 YAML

```yaml
# k8s/rec-system/values.yaml（Helm values 示例）
# 完整 K8s 部署配置

replicaCount: 3

image:
  repository: ghcr.io/your-org/recommendation-system
  pullPolicy: IfNotPresent
  tag: "latest"  # 由 CI 流水线覆盖

service:
  type: ClusterIP
  port: 8000
  healthPort: 8001

resources:
  limits:
    cpu: "2"
    memory: "4Gi"
    nvidia.com/gpu: "1"        # 如果用 GPU 推理
  requests:
    cpu: "500m"
    memory: "1Gi"

# 健康检查
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3

# 滚动更新策略
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0   # 推荐系统不允许停机

# 亲和性：打散到不同节点
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: rec-system
          topologyKey: kubernetes.io/hostname

#  Tolerations（允许调度到特殊节点）
tolerations:
  - key: "gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"

# 环境变量（从 Secret/ConfigMap 注入）
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: rec-system-secret
        key: database-url
  - name: REDIS_URL
    valueFrom:
      secretKeyRef:
        name: rec-system-secret
        key: redis-url
  - name: ML_MODEL_PATH
    valueFrom:
      configMapKeyRef:
        name: rec-system-config
        key: model-path

# Pod Disruption Budget（保证更新/故障时最少 Pod 数量）
podDisruptionBudget:
  minAvailable: 2

# HPA 自动扩缩容
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
  # 推荐系统专项指标（HPA v2 支持自定义指标）
  customMetrics:
    - type: Pods
      pods:
        metric:
          name: recommendation_request_duration_p99
        target:
          type: AverageValue
          averageValue: "500m"  # P99 < 500ms

# 限流配置（ Ingress 层）
ingress:
  enabled: true
  annotations:
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/limit-connections: "50"
    nginx.ingress.kubernetes.kubernetes.io/rewrite-target: /
  hosts:
    - host: rec.example.com
      paths: [/]
```

---

## 六、推荐系统专项 CI/CD 注意事项

### 模型文件如何管理？

```yaml
# ❌ 错误：把大模型文件放入代码仓库
git add model.pkl   # 100MB+，仓库膨胀，CI 龟速

# ✅ 正确：模型文件存对象存储，CI 只拉取版本信息
# .github/workflows/model-deploy.yml
- name: Download model from MLflow
  run: |
    mlflow models download \
      --model-uri "models:/recommendation_ranker/Production" \
      --dst-path ./models/
    
    # 计算模型哈希，记录版本
    MODEL_HASH=$(sha256sum ./models/ranker.pkl | cut -d' ' -f1)
    echo "MODEL_HASH=${MODEL_HASH}" >> $GITHUB_ENV

- name: Build model image
  run: |
    # 把模型哈希嵌入镜像 tag
    docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:model-${MODEL_HASH} .
```

### 特征版本如何对齐？

```python
# app/core/feature_version.py
# 特征版本必须与模型版本严格对齐
from functools import lru_cache

class FeatureVersionManager:
    """确保训练时和推理时使用完全相同的特征处理逻辑"""
    
    CURRENT_VERSION = "v3.2.1"  # 必须与模型版本同步
    
    @classmethod
    def get_feature_signature(cls) -> str:
        """生成当前特征版本的签名（哈希）
        CI 流水线验证：训练镜像和推理镜像的签名必须一致
        """
        import hashlib
        import importlib
        
        # 获取所有特征处理模块的源码哈希
        modules = [
            "app.features.user_features",
            "app.features.item_features", 
            "app.features.context_features",
        ]
        
        sig = hashlib.sha256()
        for m in modules:
            src = importlib.util.find_spec(m).origin
            with open(src) as f:
                sig.update(f.read().encode())
        
        return sig.hexdigest()[:8]
    
    @classmethod
    def validate_version(cls, expected: str) -> None:
        """推理前验证特征版本与训练时一致"""
        actual = cls.get_feature_signature()
        if actual != expected:
            raise ValueError(
                f"特征版本不匹配！训练时: {expected}，推理时: {actual}。"
                "请重新训练模型或更新特征处理代码。"
            )
```

### AB 实验如何隔离？

```yaml
# 在 CD 流水线中，每个实验组有独立的 Deployment
# .github/workflows/ab-deploy.yml
- name: Deploy AB experiment
  run: |
    # 实验组 A：新模型 1.0
    helm upgrade --install rec-exp-a ./k8s/rec-system \
      --namespace rec-exp \
      --set experiment.name="model_v1_vs_v2" \
      --set experiment.group="A" \
      --set experiment.traffic=50 \
      --set image.tag=${{ env.IMAGE_TAG_A }}
    
    # 实验组 B：新模型 2.0
    helm upgrade --install rec-exp-b ./k8s/rec-system \
      --namespace rec-exp \
      --set experiment.name="model_v1_vs_v2" \
      --set experiment.group="B" \
      --set experiment.traffic=50 \
      --set image.tag=${{ env.IMAGE_TAG_B }}
    
    # API Gateway 根据 cookie/user_id 哈希路由
    # 两套推理服务完全隔离，独立扩缩容，独立监控
```

---

## 七、CI/CD 质量门禁设计

### 推荐系统 CI/CD 分层门禁

```
Gate 1：代码质量（~2分钟）
├─ flake8 / ESLint 静态分析
├─ mypy 类型检查
├─ bandit 安全扫描
└─ ✅ 必须通过才能合入 main

Gate 2：单元测试（~3分钟）
├─ pytest 核心逻辑单元测试
├─ 覆盖率 ≥ 70%（可调整）
└─ ✅ 必须通过才能构建镜像

Gate 3：集成测试（~5分钟）
├─ 启动真实 MySQL/Redis/Milvus
├─ 测完整推荐链路（召回→排序→重排）
├─ 测降级策略（模拟模型超时）
└─ ✅ 必须通过才能推送镜像

Gate 4：安全扫描（~2分钟）
├─ Trivy 镜像漏洞扫描（CVE）
├─ 依赖安全检查（safety）
└─ ✅ 高危漏洞必须修复才能部署

Gate 5：Staging 冒烟（~5分钟）
├─ 健康检查
├─ 推荐接口功能测试
├─ 性能基线测试（P99 < 300ms）
└─ ✅ 必须通过才能进入灰度

Gate 6：金丝雀监控（~30分钟）
├─ 自动监控 CTR / P99 / 错误率
├─ 对比新版本 vs 旧版本指标
└─ ✅ 指标正常自动扩量，异常自动回滚
```

### CI/CD 质量门禁配置示例

```python
# app/tests/ci_integration_test.py
# CI Gate 3：集成测试必须覆盖的场景

import pytest
from httpx import AsyncClient
from app.main import app


class TestRecommendPipeline:
    """推荐全链路集成测试（CI Gate 3）"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """每个测试前启动测试数据库"""
        # 使用 Docker Compose 启动的测试服务
        # 测试完成后自动清理
        pass
    
    async def test_recall_not_empty(self):
        """召回层：必须有结果，不能全空"""
        async with AsyncClient(base_url="http://test-server") as client:
            resp = await client.get(
                "/api/v1/recommend",
                params={"user_id": 123, "scene": "home", "top_k": 20}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["items"]) > 0, "召回不能为空"
            assert len(data["items"]) <= 100, "召回上限保护"
    
    async def test_diversity(self):
        """重排层：推荐结果必须有多样性"""
        resp = await client.get("/api/v1/recommend", params={"user_id": 123})
        categories = [item["category"] for item in resp.json()["items"]]
        unique_categories = len(set(categories))
        assert unique_categories >= 3, f"多样性不足，仅 {unique_categories} 个类目"
    
    async def test_degradation(self):
        """降级策略：模型超时后有兜底"""
        # 模拟模型服务超时
        with patch("app.services.ranker.predict", side_effect=TimeoutError):
            resp = await client.get("/api/v1/recommend", params={"user_id": 123})
            assert resp.status_code == 200
            assert "items" in resp.json()  # 降级后仍有结果
            assert resp.json()["is_degraded"] is True
    
    async def test_p99_latency(self):
        """性能测试：P99 < 300ms"""
        import time
        latencies = []
        
        for _ in range(100):
            start = time.perf_counter()
            await client.get("/api/v1/recommend", params={"user_id": 123})
            latencies.append((time.perf_counter() - start) * 1000)
        
        latencies.sort()
        p99 = latencies[98]
        assert p99 < 300, f"P99 延迟 {p99:.1f}ms，超过 300ms 上限"
    
    async def test_feature_skew_detection(self):
        """特征一致性：训练-推理特征分布差异检测"""
        # 上线前必须验证特征签名与训练时一致
        from app.core.feature_version import FeatureVersionManager
        
        signature = FeatureVersionManager.get_feature_signature()
        # 这个签名必须在 CI 中与训练时的签名对比
        assert signature == os.environ.get("EXPECTED_FEATURE_SIGNATURE"), \
            "特征版本与训练时不一致！可能存在 Skew"
```

---

## 八、常见 CI/CD 坑与避坑指南

### 坑 1：CI 太慢，开发体验差

```yaml
# ❌ 每次 CI 都从头安装依赖（5分钟）
# ✅ 缓存依赖（30秒）

- name: Cache pip dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

# ❌ 每次跑全量测试
# ✅ PR 阶段只跑变更相关测试，全量测试只在 main 分支跑
```

### 坑 2：模型更新没有版本管理

```yaml
# ❌ 模型直接替换，出了事不知道回滚到哪个版本
# ✅ 用 MLflow Model Registry + GitHub Actions 自动版本对齐
```

### 坑 3：测试覆盖率高但测的都是错的

```python
# ❌ 测试用 Mock 绕过了所有真实逻辑
def test_recall(mocker):
    # 这个测试测的是 Mock 返回值，不是真实逻辑
    mocker.patch("app.services.recall.get_items", return_value=[])
    # ...
    assert result == []  # 通过了，但啥也没测

# ✅ 集成测试测真实链路，Mock 只用于外部依赖（DB/Redis/模型服务）
```

### 坑 4：CI 通过但生产挂了

```
原因：测试环境和生产环境差异太大
解决：
1. 测试用 Docker Compose 启动和 prod 相同的镜像
2. 用 Terraform/Ansible 管理测试环境配置，与生产一致
3. CI 最后的 Gate 是 Staging 环境冒烟测试（最接近生产）
```

### 坑 5：回滚靠手动

```yaml
# ✅ 自动回滚：检测到异常立即回滚
- name: Auto rollback on failure
  if: failure()
  run: |
    # Prometheus 检测到错误率 > 阈值
    if kubectl exec -n monitoring deploy/prometheus -- \
       promtool query instant \
       'rate(http_errors_total[5m]) > 0.01'; then
      echo "检测到高错误率，自动回滚..."
      kubectl rollout undo deployment/rec-system -n rec-production
    fi
```

---

## 九、适用场景速查表

| 场景 | CI/CD 重点 | 避坑 |
|------|-----------|------|
| **个人项目（刚学代码架构）** | GitHub Actions + Docker，上线到阿里云 | 不要一上来就 K8s，先用 Docker Compose |
| **团队项目（多人协作）** | PR 必须过 CI，Branch Protection | 禁止绕过 CI 合入 main |
| **模型频繁更新** | MLflow + 自动模型部署 + 灰度 | 模型版本必须与特征版本对齐 |
| **推荐系统（推荐系统专项）** | AB 实验隔离 + 指标对比 + 自动回滚 | 流量分割用一致性哈希，不用随机 |
| **追求极速反馈** | 分层测试（快测→慢测），并行执行 | Gate 1+2 控制在 5 分钟内 |

---

## 十、上线前 CI/CD 检查清单

```
□ GitHub Actions CI 全绿（lint + test + build）
□ Docker 镜像 < 300MB
□ 单元测试覆盖率 ≥ 70%
□ 集成测试覆盖推荐全链路
□ Bandit / Trivy 无高危漏洞
□ Staging 冒烟测试通过
□ 模型版本 + 特征版本已记录
□ K8s YAML 配置正确（resources/健康检查/滚动策略）
□ 金丝雀发布配置正确（流量分配/监控指标/回滚阈值）
□ 钉钉/飞书告警已配置
□ 回滚方案已测试（kubectl rollout undo）
□ 数据库 migration 已准备（如有 schema 变更）
□ 限流配置已验证（压测通过）
□ 监控大盘（SLO）已配置
□ 值班联系人已更新
□ 变更记录已写入 CHANGELOG.md
```

---

## 常见误区速查

| 误区 | 正确认知 |
|------|---------|
| "CI/CD 就是自动化部署" | CI 是质量门禁，CD 是部署流水线，侧重点不同 |
| "测试覆盖率越高越好" | 覆盖率是手段不是目的，测核心路径 > 覆盖率高但测的都是边界 |
| "上了 K8s 就高枕无忧" | K8s 只是平台，配置错误（resources/健康检查）照样挂 |
| "回滚不用测，到时候再说" | 回滚是最高风险操作，必须定期演练，否则真挂了手忙脚乱 |
| "CI 通过就万事大吉" | CI 通过 ≠ 生产没问题，测试环境和生产环境的差异是最大的坑 |
| "每个 commit 都部署" | 推荐系统有模型，更新频率应与模型迭代节奏匹配，不是越快越好 |
