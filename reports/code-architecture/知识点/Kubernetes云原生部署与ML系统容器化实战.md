# Kubernetes 云原生部署与 ML 系统容器化实战

> 推荐系统从开发到上线的最后一公里

## 概念解释

Kubernetes（K8s）是 Google 开源的容器编排平台，负责管理容器化应用的**部署、扩缩容、网络、存储**。

为什么推荐系统需要 K8s？
- **推荐系统是计算密集型**：召回/排序/重排需要大量 CPU/GPU资源
- **流量波动大**：大促时 QPS 可能暴涨 100 倍，需要弹性伸缩
- **多服务依赖**：模型服务、Redis、MySQL、Kafka 需要统一管理
- **零宕机发布**：模型更新不能影响服务，可用 Rolling Update

## 核心架构

```
┌──────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                        │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  recall Pod │  │  rank Pod   │  │  rerank Pod │         │
│  │  (×3 replicas)│ │ (×5 replicas)│ │ (×2 replicas)│         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│  ┌──────▼────────────────▼────────────────▼──────┐          │
│  │              Service (ClusterIP)                │          │
│  │         recall-svc / rank-svc / rerank-svc     │          │
│  └──────────────────────┬─────────────────────────┘          │
│                         │                                     │
│              ┌──────────▼──────────┐                         │
│              │   API Gateway Svc   │  (Ingress)              │
│              └─────────────────────┘                         │
└──────────────────────────────────────────────────────────────┘
```

## 容器化：Dockerfile 怎么写

### 反例（坏味道）

```dockerfile
# ❌ 踩坑：把训练代码和 serving 代码混在一起
FROM python:3.9
RUN pip install tensorflow pytorch scikit-learn pandas numpy
COPY . /app
WORKDIR /app
CMD ["python", "train.py"]  # 训练代码不是这样用的
```

### 正例（改进后）

**推荐系统模型服务 Dockerfile**

```dockerfile
# 推荐系统模型服务 - 精简镜像
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖（按需安装，不要全量）
COPY requirements_serving.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements_serving.txt

# 复制应用代码
COPY ./app /app
WORKDIR /app

# 非 root 用户运行（安全最佳实践）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 入口脚本（支持热加载）
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```txt
# requirements_serving.txt（只放 serving 需要的依赖）
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
redis==5.0.1
httpx==0.26.0
numpy==1.26.0
# 不要放：tensorflow pytorch（模型加载时才导入）
```

## Kubernetes 部署配置

### 1. Deployment（部署配置）

```yaml
# recall-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recall-service
  namespace: recommendation
  labels:
    app: recall-service
    team: algorithm
spec:
  replicas: 3  # 默认 3 个副本
  selector:
    matchLabels:
      app: recall-service
  # Rolling Update 配置（零宕机发布的关键）
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 最多比期望多 1 个 Pod
      maxUnavailable: 0  # 滚动过程中，始终有 3 个可用
  template:
    metadata:
      labels:
        app: recall-service
      annotations:
        prometheus.io/scrape: "true"           # 自动采集指标
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      # 亲和性：分散到不同节点（高可用）
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: recall-service
                topologyKey: kubernetes.io/hostname
      
      containers:
        - name: recall-service
          image: registry.example.com/recall-service:v2.3.1
          imagePullPolicy: Always
          
          ports:
            - containerPort: 8080
              name: http
          
          # 资源限制（防邻位干扰）
          resources:
            requests:
              cpu: "500m"      # 请求 0.5 核
              memory: "512Mi"  # 请求 512MB
            limits:
              cpu: "2000m"    # 最多用 2 核（防单个 Pod 抢光资源）
              memory: "2Gi"    # 最多用 2GB（超过 OOM Kill）
          
          # 探针配置（健康检查）
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10   # 启动后 10s 开始探测
            periodSeconds: 15         # 每 15s 探测一次
            timeoutSeconds: 5
            failureThreshold: 3        # 连续 3 次失败 → 重启 Pod
          
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3        # 连续 3 次失败 → 摘除流量
          
          env:
            - name: REDIS_HOST
              valueFrom:
                configMapKeyRef:
                  name: recall-config
                  key: redis.host
            - name: REDIS_PORT
              value: "6379"
            - name: MODEL_VERSION
              value: "v2.3.1"
            - name: LOG_LEVEL
              value: "INFO"
          
          # 存活钩子：Pod 终止前优雅处理
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
          
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
      
      volumes:
        - name: config
          configMap:
            name: recall-config
```

### 2. Service（服务发现）

```yaml
# recall-service-svc.yaml
apiVersion: v1
kind: Service
metadata:
  name: recall-svc
  namespace: recommendation
  labels:
    app: recall-service
spec:
  type: ClusterIP  # 集群内部访问（API Gateway 用这个）
  ports:
    - port: 80           # Service 端口
      targetPort: 8080   # Pod 实际端口
      protocol: TCP
      name: http
  selector:
    app: recall-service
```

### 3. HPA（自动扩缩容）

```yaml
# recall-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recall-hpa
  namespace: recommendation
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recall-service
  # 扩缩容范围
  minReplicas: 3    # 最少 3 个（保证可用性）
  maxReplicas: 20   # 最多 20 个（成本上限）
  
  metrics:
    # 基于 CPU 自动扩缩容
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # CPU 平均 > 70% → 扩容
    
    # 基于自定义指标（推荐系统专用）
    - type: Pods
      pods:
        metric:
          name: recommendation_request_duration_p99
        target:
          type: AverageValue
          averageValue: "300m"  # P99 延迟 > 300ms → 扩容
```

### 4. Ingress（外部访问）

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: recommendation-ingress
  namespace: recommendation
  annotations:
    # 限流注解（防止流量洪峰打垮服务）
    nginx.ingress.kubernetes.io/limit-rps: "1000"
    nginx.ingress.kubernetes.io/limit-connections: "100"
    # 重写规则
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api/recall
            pathType: Prefix
            backend:
              service:
                name: recall-svc
                port:
                  number: 80
          - path: /api/rank
            pathType: Prefix
            backend:
              service:
                name: rank-svc
                port:
                  number: 80
```

## 推荐系统完整 K8s 部署架构

```yaml
# 推荐系统完整部署（docker-compose 本地开发版 + K8s 生产版）
# docker-compose.yaml 用于本地开发调试
version: "3.8"
services:
  # API Gateway
  api-gateway:
    build: ./api-gateway
    ports:
      - "8000:8000"
    environment:
      - RECALL_SERVICE_URL=http://recall-service:8000
      - RANK_SERVICE_URL=http://rank-service:8000
    depends_on:
      - recall-service
      - rank-service
  
  # 召回服务
  recall-service:
    build: ./recall-service
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "1.0"
          memory: "1G"
  
  # 排序服务（GPU 加速）
  rank-service:
    build: ./rank-service
    environment:
      - MODEL_PATH=/app/models/ranker_v2
      - REDIS_HOST=redis
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "2.0"
          memory: "4G"
          # nvidia.com/gpu: "1"  # 生产环境开启 GPU
  
  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
  
  # MySQL 用户画像
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=dev_password
      - MYSQL_DATABASE=recommendation
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## ConfigMap & Secret（配置管理）

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: recall-config
  namespace: recommendation
data:
  redis.host: "redis-svc"
  redis.port: "6379"
  recall.top_k: "100"
  recall.timeout_ms: "50"
---
# secret.yaml（敏感数据用 Secret，不要放 ConfigMap）
apiVersion: v1
kind: Secret
metadata:
  name: recall-secrets
  namespace: recommendation
type: Opaque
stringData:
  redis.password: "your-redis-password"       # Base64 编码存储
  mysql.password: "your-mysql-password"
  model.api_key: "your-model-api-key"
```

## 蓝绿部署（零风险发布）

```yaml
# blue-green-deployment.yaml
# 新版本先部署到"蓝"环境，验证通过后切换流量
apiVersion: v1
kind: Namespace
metadata:
  name: recommendation-blue
---
apiVersion: v1
kind: Namespace
metadata:
  name: recommendation-green
---
# 通过 Service Selector 切换流量
# 切换前：selector: app: recall-service, version: blue
# 切换后：selector: app: recall-service, version: green
apiVersion: v1
kind: Service
metadata:
  name: recall-svc
  namespace: recommendation
spec:
  selector:
    app: recall-service
    version: blue  # 改这个切换流量
  ports:
    - port: 80
      targetPort: 8080
```

## 推荐系统 K8s 部署检查清单

### 部署前（Pre-deploy）
- [ ] 所有镜像已 build 并推送到 registry
- [ ] 资源 requests/limits 已合理设置
- [ ] liveness/readinessProbe 已配置
- [ ] ConfigMap/Secret 已创建
- [ ] HPA 扩缩容策略已设置
- [ ] 旧版本 Pod 数量充足（maxUnavailable: 0）

### 部署中（During deploy）
- [ ] Rolling Update 按预期进行（新 Pod 启动 → 旧 Pod 终止）
- [ ] 新 Pod liveness 检查通过
- [ ] 新 Pod readiness 检查通过（流量切换）
- [ ] Prometheus 指标正常（无异常错误率上升）
- [ ] Grafana 看板 P99 延迟未恶化

### 部署后（Post-deploy）
- [ ] 旧版本镜像已下线
- [ ] 滚动回滚方案已确认（如有问题 kubectl rollout undo）
- [ ] 监控告警正常触发
- [ ] 日志正常采集到 Loki
- [ ] 通知团队发布完成

## 常见误区

### 误区1：资源 limit 设置过大
```yaml
# ❌ 错误：limits 不设上限，单个 Pod 可能抢光整个集群资源
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "10"    # 10 核太激进
    memory: "20Gi"

# ✅ 正确：合理设置上限，防止邻位干扰
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "2000m"  # 最多 2 核
    memory: "2Gi"  # 最多 2GB
```

### 误区2：健康检查太严格或太宽松
```yaml
# ❌ 太严格：initialDelaySeconds 太小，服务还没启动完就开始探测
livenessProbe:
  httpGet:
    path: /health
  initialDelaySeconds: 0    # 服务还在启动就探测 → 反复重启
  failureThreshold: 1

# ✅ 正确：给足够的启动时间
livenessProbe:
  httpGet:
    path: /health
  initialDelaySeconds: 30   # 模型加载需要时间
  periodSeconds: 10
  failureThreshold: 3       # 3 次失败才重启
```

### 误区3：滚动更新 maxUnavailable 设太高
```yaml
# ❌ 错误：滚动更新时只有 1 个 Pod 可用，流量高峰时服务中断
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 0
    maxUnavailable: 2  # 3 个副本里最多只有 1 个可用

# ✅ 正确：推荐系统延迟敏感，保持全量副本
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # 最多多起 1 个
    maxUnavailable: 0  # 滚动时始终有 3 个可用
```

### 误区4：Pod 终止时没有优雅下线
```yaml
# ❌ 错误：Pod 直接被 kill，在途请求全部失败
lifecycle:
  preStop:
    exec:
      command: []  # 没做任何清理

# ✅ 正确：等已在途请求处理完，再杀掉 Pod
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]  # 等待 K8s 更新 Endpoints + 流量切换
```

## 推荐系统 K8s 架构决策树

```
Q1: 需要 GPU 加速吗？
├── 是 → rank-service 用 nvidia.com/gpu:1
│         Node 池：配置 GPU 节点（k8s-node-gpu）
│         调度：nodeSelector + tolerations 定向到 GPU 节点
└── 否 → 普通 CPU 节点足够

Q2: 流量多大？
├── < 100 QPS → 单 Deployment，replicas=2，HPA 基于 CPU
├── 100-1000 QPS → 多 Deployment，HPA 基于 CPU+自定义指标
└── > 1000 QPS → API Gateway 限流 + 多副本 + 预热 + 分层

Q3: 需要灰度发布吗？
├── 是 → Ingress canary（权重流量切分）或蓝绿部署
└── 否 → Rolling Update（maxUnavailable: 0）

Q4: 有敏感配置吗？
├── 是 → Secret（Base64）+ RBAC 限制访问
└── 否 → ConfigMap
```

## 学习路径建议

```
Day 1: 容器基础
  Docker 基础命令 → 写一个简单的 Dockerfile
  本地用 docker-compose 跑通推荐系统

Day 2: K8s 核心概念
  Pod / Service / Deployment 三大核心资源
  kubectl 常用命令（get/describe/logs/exec/port-forward）

Day 3: 推荐系统 K8s 部署
  将 docker-compose 转换为 K8s yaml
  配置健康检查 + 资源限制
  本地用 Minikube 或 Kind 部署测试

Day 4: 高级特性
  HPA 自动扩缩容
  ConfigMap/Secret 配置管理
  Ingress 路由 + 限流

Day 5: 生产级实践
  滚动更新 + 回滚
  蓝绿部署 / 金丝雀发布
  监控告警集成
```

## 相关文档

- [微服务架构实战](知识点/微服务架构实战.md)
- [模型服务化架构与推理优化实战](知识点/模型服务化架构与推理优化实战.md)
- [可观测性实战：日志指标链路追踪](知识点/可观测性实战：日志指标链路追踪.md)
