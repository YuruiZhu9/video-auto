# NestJS K8s 部署与云原生配置实战

> 将 NestJS 推荐服务容器化并部署到 Kubernetes

## 项目结构

```bash
recommendation-service/
├── Dockerfile
├── docker-compose.yaml
├── .dockerignore
├── .k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── ingress.yaml
├── Dockerfile
└── src/
    ├── main.ts
    ├── app.module.ts
    ├── recall/
    │   ├── recall.module.ts
    │   ├── recall.controller.ts
    │   ├── recall.service.ts
    │   └── recall.strategy.ts
    └── health/
        ├── health.module.ts
        └── health.controller.ts
```

## Dockerfile（NestJS 专用）

```dockerfile
# 阶段性构建（Multi-stage Build），减小镜像体积
# Stage 1: 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

# 安装依赖（利用 Docker 缓存，依赖不变时不重新安装）
COPY package*.json ./
RUN npm ci --only=production=false

# 复制源码并构建
COPY . .
RUN npm run build

# Stage 2: 生产阶段
FROM node:20-alpine AS production

# 创建非 root 用户（安全）
RUN addgroup -g 1001 -S nodejs && adduser -S nestjs -u 1001

WORKDIR /app

# 只复制构建产物和运行时依赖
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nestjs:nodejs /app/package.json ./package.json

# 切换到非 root 用户
USER nestjs

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# 启动命令
CMD ["node", "dist/main"]
```

## .dockerignore

```dockerignore
# 不需要打包进镜像的文件
node_modules
npm-debug.log
.git
.gitignore
.env
.env.*
*.md
test
.vscode
.idea
dist  # 重新构建，不要复制旧的
```

## NestJS 健康检查端点

```typescript
// health.controller.ts
import { Controller, Get } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckService,
  HealthCheckResult,
  HealthIndicator,
  HealthIndicatorResult,
} from '@nestjs/terminus';
import { RedisHealthIndicator } from '@nestjs/terminus/redis';

@Controller()
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private redis: RedisHealthIndicator,
    private readonly configService: ConfigService,
  ) {}

  // K8s livenessProbe：Pod 是否活着
  @Get('health')
  @HealthCheck()
  async liveness(): Promise<HealthCheckResult> {
    return this.health.check([
      // 只检查进程是否存活（不依赖外部依赖）
      (): Promise<HealthIndicatorResult> =>
        Promise.resolve({
          app: { status: 'up' },
        }),
    ]);
  }

  // K8s readinessProbe：Pod 是否可以接收流量
  @Get('ready')
  @HealthCheck()
  async readiness(): Promise<HealthCheckResult> {
    return this.health.check([
      // 检查 Redis 连接（推荐服务依赖 Redis）
      async (): Promise<HealthIndicatorResult> => {
        try {
          const redisHost = this.configService.get('REDIS_HOST', 'localhost');
          const redisPort = this.configService.get('REDIS_PORT', '6379');
          // 这里用 tcp 连接检查
          return {
            redis: { status: 'up', host: redisHost, port: redisPort },
          };
        } catch {
          return {
            redis: { status: 'down' },
          };
        }
      },
      // 检查 MySQL 连接
      async (): Promise<HealthIndicatorResult> => {
        try {
          // 可以用 TypeORM DataSource 检查
          return { mysql: { status: 'up' } };
        } catch {
          return { mysql: { status: 'down' } };
        }
      },
    ]);
  }
}
```

## Kubernetes YAML 配置

### Deployment

```yaml
# .k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-api
  namespace: recommendation
  labels:
    app: recommendation-api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: recommendation-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: recommendation-api
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: recommendation-api
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
        - name: recommendation-api
          image: registry.example.com/recommendation-api:v1.2.0
          imagePullPolicy: Always
          
          ports:
            - containerPort: 3000
              name: http
          
          envFrom:
            - configMapRef:
                name: recommendation-config
            - secretRef:
                name: recommendation-secrets
          
          env:
            - name: NODE_ENV
              value: "production"
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_IP
              valueFrom:
                fieldRef:
                  fieldPath: status.podIP
          
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
            successThreshold: 1
          
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
            successThreshold: 1
            timeoutSeconds: 3
          
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
          
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      
      volumes:
        - name: tmp
          emptyDir: {}
      
      # 终止 gracePeriod（Pod 收到 SIGTERM 后等待多久才 SIGKILL）
      terminationGracePeriodSeconds: 60
```

### ConfigMap & Secret

```yaml
# .k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: recommendation-config
  namespace: recommendation
data:
  NODE_ENV: "production"
  REDIS_HOST: "redis-svc"
  REDIS_PORT: "6379"
  MYSQL_HOST: "mysql-svc"
  MYSQL_PORT: "3306"
  RECALL_TOP_K: "100"
  RANK_TIMEOUT_MS: "200"
  LOG_LEVEL: "info"
---
# .k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: recommendation-secrets
  namespace: recommendation
type: Opaque
stringData:
  MYSQL_PASSWORD: "prod_mysql_password"
  REDIS_PASSWORD: "prod_redis_password"
  JWT_SECRET: "your-jwt-secret-min-32-chars"
  # 其他敏感配置...
```

### Service

```yaml
# .k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: recommendation-api-svc
  namespace: recommendation
  labels:
    app: recommendation-api
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
      name: http
  selector:
    app: recommendation-api
```

### HPA

```yaml
# .k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recommendation-api-hpa
  namespace: recommendation
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recommendation-api
  minReplicas: 3
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  # 扩容冷却（防止抖动）
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60   # 扩容后 60s 内不再缩容
      policies:
        - type: Percent
          value: 100                     # 最多一次扩容 100%（翻倍）
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300  # 缩容前等待 5 分钟（保护流量高峰）
      policies:
        - type: Percent
          value: 10                      # 最多一次缩容 10%
          periodSeconds: 60
```

## 部署命令

```bash
# 构建并推送镜像
docker build -t registry.example.com/recommendation-api:v1.2.0 .
docker push registry.example.com/recommendation-api:v1.2.0

# 部署（按顺序）
kubectl apply -f .k8s/namespace.yaml
kubectl apply -f .k8s/configmap.yaml
kubectl apply -f .k8s/secret.yaml
kubectl apply -f .k8s/deployment.yaml
kubectl apply -f .k8s/service.yaml
kubectl apply -f .k8s/hpa.yaml

# 验证
kubectl get pods -n recommendation
kubectl get svc -n recommendation
kubectl get hpa -n recommendation

# 查看 Pod 日志
kubectl logs -f deployment/recommendation-api -n recommendation

# 滚动更新（改镜像版本后）
kubectl set image deployment/recommendation-api \
    recommendation-api=registry.example.com/recommendation-api:v1.2.1 \
    -n recommendation

# 滚动回滚
kubectl rollout undo deployment/recommendation-api -n recommendation

# 扩缩容（手动）
kubectl scale deployment recommendation-api --replicas=5 -n recommendation

# 端口转发（本地调试）
kubectl port-forward svc/recommendation-api-svc 8080:80 -n recommendation
```

## NestJS 容器化常见坑

### 坑1：启动很慢（Liveness 检查失败）

```typescript
// main.ts - 等待数据库连接完成再监听
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // 启用优雅关闭（收到 SIGTERM 后等待处理完在途请求）
  app.enableShutdownHooks();
  
  // 监听延迟绑定（先完成初始化再开始接收请求）
  await app.init();
  
  const server = app.getHttpAdapter().getInstance();
  server.listen(3000);
}
```

### 坑2：ConfigService 在 Bootstrap 前使用

```typescript
// ❌ 错误：在 main.ts 中直接使用 ConfigService
async function bootstrap() {
  const config = app.get(ConfigService);
  const port = config.get('PORT'); // 此时模块还没初始化
}

// ✅ 正确：等 APP_INITIALIZER 完成后再启动
// app.module.ts
{
  provide: 'APP_INITIALIZER',
  useFactory: (configService: ConfigService) => async () => {
    // 从 K8s Secret/ConfigMap 加载配置
    await configService.loadConfig();
  },
  inject: [ConfigService],
}
```

### 坑3：Redis 连接池在重启时未清理

```typescript
// ❌ 错误：Redis 连接在收到 SIGTERM 后没有清理
@Injectable()
export class RecallService {
  async onModuleDestroy() {
    // 没清理 → Pod 关闭时连接泄露
  }
}

// ✅ 正确：清理连接池
@Injectable()
export class RecallService implements OnModuleDestroy {
  async onModuleDestroy() {
    await this.redisClient.quit();    // 等待在途请求处理完
    await this.redisClient.disconnect();
  }
}
```
