# API 安全与身份认证实战

> 推荐系统 API 每天都暴露在公网上，用户 token、推荐策略参数、用户行为数据都是攻击目标。本文档覆盖认证、授权、API 安全最佳实践，Python + TypeScript 双语言实战。

---

## 概念解释

### 认证（Authentication）vs 授权（Authorization）

| 维度 | 认证 AuthN | 授权 AuthZ |
|------|-----------|-----------|
| 问题 | **你是谁？** | **你能做什么？** |
| 机制 | 用户名密码、JWT、OAuth2 | RBAC、ABAC、Policy |
| 发生的时机 | 请求进来第一关 | 认证通过后，检查权限 |

```
请求进来
    ↓
[认证层] 这个请求是谁发的？token 有效吗？
    ↓ 通过
[授权层] 这个用户能访问这个接口吗？
    ↓ 通过
[业务层] 执行推荐逻辑，返回结果
```

---

## 1. JWT（JSON Web Token）：最常见的认证方案

### 工作原理

```
客户端登录 → 服务器验证密码 → 签发 JWT（包含 user_id + 过期时间）→ 客户端保存
    ↓
后续请求 → Header 带上 Authorization: Bearer <token>
    ↓
服务器验签 → 检查过期时间 → 取出 user_id → 执行业务
```

### JWT 结构

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.   ← Header（算法+类型）
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ik   ← Payload（用户数据，可 Base64 解密）
pZCI6IjEyMyJ9.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_ad   ← Signature（签名，防篡改）
```

**⚠️ 重要：JWT Payload 是 Base64 编码，不是加密。敏感信息（如密码）不能放 Payload！**

### Python 实现（Flask + PyJWT）

```python
# 安装：pip install pyjwt

import jwt
import datetime
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

def create_token(user_id: int, role: str) -> str:
    """签发 JWT"""
    payload = {
        "sub": user_id,          # subject，用户唯一标识
        "role": role,            # 用户角色（不要放敏感信息！）
        "iat": datetime.datetime.utcnow(),  # issued at
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    """验签，返回 payload 或 None（失败）"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None   # token 过期
    except jwt.InvalidTokenError:
        return None   # 签名错误/格式错误


def require_auth(f):
    """装饰器：保护需要认证的接口"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "缺少或格式错误的 Authorization 头"}), 401
        
        token = auth_header[7:]  # 去掉 "Bearer " 前缀
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "无效或已过期的 token"}), 401
        
        # 把 user_id 注入请求上下文
        request.user_id = payload["sub"]
        request.user_role = payload["role"]
        return f(*args, **kwargs)
    return decorated


# 使用示例
@app.route("/api/recommend", methods=["POST"])
@require_auth
def get_recommend():
    # request.user_id 已经在装饰器中注入了
    items = recommendation_service.get_for_user(request.user_id)
    return jsonify({"items": items})
```

### TypeScript 实现（NestJS + @nestjs/jwt）

```typescript
// 安装：npm install @nestjs/jwt @nestjs/passport passport passport-jwt

import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  constructor(private jwtService: JwtService) {}

  // 签发 token
  createToken(userId: number, role: string): string {
    const payload = { sub: userId, role };
    return this.jwtService.sign(payload);
  }

  // 验证 token
  verifyToken(token: string): { sub: number; role: string } | null {
    try {
      return this.jwtService.verify(token);
    } catch {
      return null;
    }
  }

  // 登录（示例）
  async login(username: string, password: string) {
    const user = await this.userRepository.findByUsername(username);
    if (!user || !await bcrypt.compare(password, user.passwordHash)) {
      throw new UnauthorizedException('用户名或密码错误');
    }
    return {
      access_token: this.createToken(user.id, user.role),
    };
  }
}

// JWT Strategy（Passport）
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: process.env.JWT_SECRET!,
    });
  }

  async validate(payload: { sub: number; role: string }) {
    return { userId: payload.sub, role: payload.role };
  }
}

// 路由保护
@Controller('recommend')
export class RecommendController {
  @UseGuards(JwtAuthGuard)
  @Post()
  getRecommend(@Request() req) {
    // req.user 由 JwtStrategy 注入
    return this.recommendService.getForUser(req.user.userId);
  }
}
```

### JWT 安全 Checklist

| ⚠️ 风险 | ✅ 缓解措施 |
|--------|-----------|
| Token 被盗 | 使用 HTTPS；短期 token（15min）+ Refresh Token |
| Payload 被篡改（但不改签名） | **不要在 Payload 放敏感数据**（Base64 可直接读） |
| 签名用 HS256 泄露密钥 | 生产用 RS256（公私钥对）；密钥放环境变量 |
| Token 不设过期 | **永远设 `exp`**，建议 15min-24h |
| 重放攻击 | 后端维护 Token ID 黑名单，或用 `nonce` + 时间戳 |

---

## 2. RBAC（基于角色的访问控制）：权限管理

### RBAC 核心模型

```
用户（User）→ 角色（Role）→ 权限（Permission）
                   ↓
              用户组（Group）→ 角色（可继承）

用户1 --→ admin
用户2 --→ editor ──→ 角色（发布内容 + 草稿编辑）
用户3 --→ viewer
```

### 推荐系统 RBAC 实战

```python
from enum import Enum
from typing import Set
from functools import wraps

class Permission(Enum):
    RECOMMEND_READ    = "recommend:read"     # 查看推荐结果
    RECOMMEND_ADMIN   = "recommend:admin"    # 管理推荐策略
    USER_PROFILE_READ = "user:profile:read" # 读取用户画像
    USER_PROFILE_EDIT = "user:profile:edit" # 编辑用户画像
    ANALYTICS_VIEW    = "analytics:view"    # 查看数据分析
    SYSTEM_CONFIG     = "system:config"      # 系统配置

ROLE_PERMISSIONS: dict[str, Set[Permission]] = {
    "viewer": {Permission.RECOMMEND_READ, Permission.ANALYTICS_VIEW},
    "editor": {Permission.RECOMMEND_READ, Permission.ANALYTICS_VIEW,
               Permission.USER_PROFILE_READ},
    "admin": set(Permission),  # 管理员拥有所有权限
    "algorithm_engineer": {Permission.RECOMMEND_READ, Permission.RECOMMEND_ADMIN,
                            Permission.USER_PROFILE_READ, Permission.ANALYTICS_VIEW},
}

def require_permission(perm: Permission):
    """装饰器：检查用户是否有指定权限"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user_role'):
                return jsonify({"error": "未认证"}), 401
            
            user_perms = ROLE_PERMISSIONS.get(request.user_role, set())
            if perm not in user_perms:
                return jsonify({
                    "error": "权限不足",
                    "required": perm.value,
                    "current_role": request.user_role
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# 使用示例
@app.route("/api/recommend/strategy", methods=["PUT"])
@require_auth
@require_permission(Permission.RECOMMEND_ADMIN)
def update_strategy():
    """只有 algorithm_engineer 和 admin 能修改推荐策略"""
    # ...
    pass

@app.route("/api/recommend/result", methods=["GET"])
@require_auth
def get_recommend():
    """viewer、editor、admin 都能看推荐结果"""
    # ...
    pass
```

### TypeScript NestJS 实现

```typescript
// permissions.decorator.ts
export const REQUIRED_PERMISSIONS = (...perms: Permission[]) =>
  SetMetadata('permissions', perms);

// permissions.guard.ts
@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredPerms = this.reflector.get<Permission[]>(
      'permissions', context.getHandler(),
    ) || [];
    if (requiredPerms.length === 0) return true;

    const { user } = context.switchToHttp().getRequest();
    const userPerms = ROLE_PERMISSIONS[user.role] || [];
    return requiredPerms.every(p => userPerms.includes(p));
  }
}

// 使用
@Get('strategy')
@UseGuards(JwtAuthGuard, PermissionsGuard)
@RequiredPermissions(Permission.RECOMMEND_ADMIN)
updateStrategy(@Body() dto: UpdateStrategyDto) {
  return this.strategyService.update(dto);
}
```

---

## 3. API 安全：十大最佳实践

### 3.1 HTTPS 强制

```
HTTP 明文传输 → 可被中间人劫持
HTTPS 加密传输 → 防止窃听和篡改

# Nginx 配置（强制 HTTPS）
server {
    listen 80;
    return 301 https://$host$request_uri;  # 强制重定向到 HTTPS
}
```

### 3.2 请求频率限制（Rate Limiting）

**为什么重要**：推荐系统接口容易被刷，轻则费用暴增，重则服务雪崩。

```python
# 简单实现：基于内存的限流
import time
from collections import defaultdict
from flask import request, jsonify

class RateLimiter:
    def __init__(self):
        self.requests: dict[int, list[float]] = defaultdict(list)
    
    def is_allowed(self, user_id: int, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        # 清理窗口外的请求
        self.requests[user_id] = [
            t for t in self.requests[user_id] if now - t < window_seconds
        ]
        if len(self.requests[user_id]) >= max_requests:
            return False
        self.requests[user_id].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # 优先用 user_id，未登录用 IP
            user_id = getattr(request, 'user_id', None) or request.remote_addr
            if not rate_limiter.is_allowed(user_id, max_requests, window_seconds):
                return jsonify({
                    "error": "请求过于频繁，请稍后再试",
                    "retry_after": window_seconds
                }), 429
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route("/api/recommend", methods=["POST"])
@require_auth
@rate_limit(max_requests=60, window_seconds=60)  # 每分钟60次
def get_recommend():
    pass

# 生产推荐：Redis 分布式限流（多实例共用同一个计数器）
# 使用令牌桶算法，详见 Redis 缓存文档
```

**限流策略分级**：
| 级别 | 限制 | 触发后 |
|------|------|--------|
| 普通用户 | 60次/分钟 | 429 Too Many Requests |
| 付费用户 | 600次/分钟 | 429 |
| 算法工程师（内部） | 无限制 | — |

### 3.3 输入验证：永远不要信任用户输入

```python
# ❌ 反例：直接用用户输入构造 SQL
user_id = request.json["user_id"]
query = f"SELECT * FROM recommendations WHERE user_id = {user_id}"  # SQL注入！

# ✅ 正例：用参数化查询
from sqlalchemy import text
query = text("SELECT * FROM recommendations WHERE user_id = :uid")
result = db.session.execute(query, {"uid": user_id})

# ✅ FastAPI + Pydantic 自动验证
from pydantic import BaseModel, Field

class RecommendRequest(BaseModel):
    user_id: int = Field(..., gt=0)                          # 必须是正整数
    scene: str = Field(..., pattern="^(home|detail|search)$")  # 白名单校验
    limit: int = Field(default=10, ge=1, le=100)            # 限制范围
    extra_filters: dict = Field(default_factory=dict)        # 防注入：限制 key

@app.post("/api/recommend")
def get_recommend(req: RecommendRequest):
    items = recommendation_service.get(user_id=req.user_id,
                                        scene=req.scene,
                                        limit=req.limit)
    return {"items": items}
```

### 3.4 敏感数据脱敏

推荐系统常见敏感数据：**手机号、邮箱、用户 ID、行为数据**。

```python
import re

def mask_phone(phone: str) -> str:
    """13812345678 → 138****5678"""
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]

def mask_email(email: str) -> str:
    """john@example.com → j***@example.com"""
    if not email or "@" not in email:
        return email
    name, domain = email.split("@", 1)
    return name[0] + "***@" + domain

def mask_user_id(user_id: int) -> str:
    """对外暴露时用脱敏 ID"""
    return f"U{user_id:06d}"  # U000001

# API 响应时自动脱敏（装饰器）
def sanitize_response(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        result = f(*args, **kwargs)
        if isinstance(result, dict):
            result["user_phone"] = mask_phone(result.get("user_phone", ""))
            result["user_email"] = mask_email(result.get("user_email", ""))
        return result
    return decorated
```

### 3.5 CORS：跨域资源共享

```python
# Flask-CORS 配置
from flask_cors import CORS
CORS(app,
     resources={r"/api/*": {
         "origins": ["https://your-frontend.com"],  # 白名单
         "methods": ["GET", "POST"],                  # 只允许必要方法
         "allow_headers": ["Authorization", "Content-Type"],
         "expose_headers": ["X-Request-ID"],         # 允许前端访问的响应头
         "max_age": 3600,                             # 预检请求缓存
     }})
# ⚠️ 生产环境不要用 origins="*"（允许所有来源）
```

### 3.6 API 响应格式统一

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ApiResponse:
    code: int        # 业务状态码（200=成功，4xx=客户端错误，5xx=服务端错误）
    message: str     # 友好提示
    data: Any = None
    request_id: str = ""  # 用于问题排查

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "request_id": self.request_id,
        }

# 全局中间件：为每个请求生成 request_id
@app.before_request
def add_request_id():
    request.request_id = request.headers.get("X-Request-ID", generate_uuid())
    g.request_id = request.request_id

@app.after_request
def add_headers(response):
    response.headers["X-Request-ID"] = g.request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify(ApiResponse(
        code=500,
        message="内部错误，请稍后重试",
        request_id=g.get("request_id", "")
    ).to_dict()), 500
```

### 3.7 SQL 注入防护

| 做法 | 说明 |
|------|------|
| 参数化查询 | SQL 语句和参数分开，永远不拼接用户输入 |
| ORM 使用 | SQLAlchemy、Prisma 等 ORM 默认防注入 |
| 最小权限原则 | 数据库连接只用业务所需最小权限，不要用 root |
| 输入白名单 | `scene in ("home", "detail", "search")` |

### 3.8 请求体大小限制

```python
# Flask：限制 JSON 请求体最大 1MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "请求体过大，最大支持 1MB"}), 413

# FastAPI
from fastapi import FastAPI
app = FastAPI()

# 全局限流中间件
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class RequestSizeMiddleware(BaseHTTPMiddleware):
    MAX_SIZE = 1 * 1024 * 1024  # 1MB

    async def dispatch(self, request: Request, call_next):
        if int(request.headers.get("content-length", 0)) > self.MAX_SIZE:
            return JSONResponse({"error": "请求体过大"}, status_code=413)
        return await call_next(request)
```

### 3.9 审计日志

```python
import logging
import json

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# 审计日志内容：谁在什么时间做了什么
@app.after_request
def audit_log(response):
    if request.path.startswith("/api/"):
        audit_logger.info(json.dumps({
            "request_id": g.get("request_id", ""),
            "user_id": getattr(request, "user_id", "anonymous"),
            "method": request.method,
            "path": request.path,
            "ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", ""),
            "response_code": response.status_code,
            "duration_ms": round((time.time() - request.start_time) * 1000, 2),
        }, ensure_ascii=False))
    return response
```

### 3.10 推荐系统专项安全

```python
# 推荐结果防注入：用户传入的 filter 不能包含危险操作
@app.route("/api/recommend", methods=["POST"])
@require_auth
def get_recommend():
    # ❌ 危险：直接把用户输入当过滤条件执行
    # filters = request.json.get("filters", "")
    # query = f"SELECT * FROM items WHERE {filters}"  # SQL注入！

    # ✅ 安全：使用白名单 + 类型校验
    allowed_filters = {
        "category": str,
        "min_price": float,
        "max_price": float,
        "tags": list,
        "scene": str,
    }
    filters = {}
    raw_filters = request.json.get("filters", {})
    for key, expected_type in allowed_filters.items():
        if key in raw_filters:
            try:
                filters[key] = expected_type(raw_filters[key])
            except (ValueError, TypeError):
                pass  # 忽略类型不匹配的值

    # scene 白名单校验
    VALID_SCENES = {"home", "detail", "search", "cart", "profile"}
    if filters.get("scene") and filters["scene"] not in VALID_SCENES:
        return jsonify({"error": "非法的 scene 参数"}), 400

    return recommendation_service.get(user_id=request.user_id, **filters)
```

---

## 4. OAuth2 简介：第三方登录

### 适用场景

- 小程序/App 需要微信登录
- 开放平台给第三方开发者提供 API
- 不想让用户注册新账号，用已有账号登录

### 推荐系统 OAuth2 流程

```
用户点击"微信登录"
    ↓
你的服务器 → 微信授权服务器（携带 client_id + redirect_uri）
    ↓
用户同意授权
    ↓
微信授权服务器 → 回调你的 redirect_uri（带 code）
    ↓
你的服务器 → 微信（用 code 换 access_token）
    ↓
你的服务器 → 微信（用 access_token 获取用户信息）
    ↓
你的服务器 → 生成自己的 JWT，返回给客户端
```

```python
# 微信 OAuth2 示例
import os
import httpx
from urllib.parse import urlencode

WECHAT_APP_ID = os.environ["WECHAT_APP_ID"]
WECHAT_APP_SECRET = os.environ["WECHAT_APP_SECRET"]
REDIRECT_URI = "https://your-app.com/api/auth/wechat/callback"

@app.route("/api/auth/wechat/login")
def wechat_login():
    """第一步：跳转到微信授权页面"""
    params = {
        "appid": WECHAT_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "snsapi_userinfo",
        "state": generate_csrf_token(),  # CSRF 防护
    }
    url = f"https://open.weixin.qq.com/connect/qrconnect2?{urlencode(params)}"
    return {"redirect_url": url}

@app.route("/api/auth/wechat/callback")
def wechat_callback():
    """第三步：接收 code，换取用户信息"""
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or state != get_saved_csrf_token():
        return jsonify({"error": "CSRF 校验失败"}), 400

    # 用 code 换 access_token
    token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    token_resp = httpx.get(token_url, params={
        "appid": WECHAT_APP_ID,
        "secret": WECHAT_APP_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    })
    token_data = token_resp.json()

    if "errcode" in token_data:
        return jsonify({"error": "微信授权失败"}), 401

    # 用 access_token 获取用户信息
    user_info_url = "https://api.weixin.qq.com/sns/userinfo"
    user_resp = httpx.get(user_info_url, params={
        "access_token": token_data["access_token"],
        "openid": token_data["openid"],
    })
    user_info = user_resp.json()

    # 查找或创建用户
    user = user_service.find_or_create_by_wechat(
        openid=user_info["openid"],
        nickname=user_info["nickname"],
        avatar=user_info["headimgurl"],
    )

    # 生成自己的 JWT
    return {"access_token": create_token(user.id, user.role)}
```

---

## 5. 常见安全漏洞与防范

### 漏洞速查表

| 漏洞 | 说明 | 防范 |
|------|------|------|
| **SQL 注入** | 用户输入拼进 SQL 语句 | 参数化查询 / ORM |
| **XSS** | 在推荐结果中注入恶意脚本 | 输出转义 / CSP |
| **CSRF** | 诱导用户访问恶意页面，自动提交表单 | CSRF Token / SameSite Cookie |
| **Token 泄露** | URL/日志中暴露 token | 用 Header 而非 URL 传 token |
| **越权访问** | 改了 URL 参数就能看别人的数据 | 授权层检查 `user_id` 归属 |
| **敏感数据泄露** | API 返回不必要的用户隐私信息 | 接口最小化返回 + 脱敏 |
| **重放攻击** | 截获请求反复发送 | 请求序列号 + 时间戳 + Nonce |
| **暴力破解** | 反复尝试登录密码 | 限流 + 多次失败锁定账户 |
| **SSRF** | 用户提交 URL 后服务器去请求（可能访问内网） | URL 白名单 + DNS 重绑定防护 |

### CSRF 防护（Flask）

```python
# 生成 CSRF Token
from flask_wtf.csrf import generate_csrf

@app.get("/form")
def form_page():
    return render_template("form.html", csrf_token=generate_csrf())

# API 无状态场景：用自定义 Header 携带 token
# 客户端在每次请求时同时带上 JWT 和 X-CSRF-Token
@app.before_request
def check_csrf():
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        # 如果是 JSON 请求，需要额外校验
        csrf_header = request.headers.get("X-CSRF-Token", "")
        if not csrf_header or csrf_header != session.get("csrf_token"):
            return jsonify({"error": "CSRF token 无效"}), 403
```

---

## 适用场景

- **对外 API**（小程序/App/H5）必须做认证 + HTTPS + 限流
- **内部微服务**（召回调/排序服务）用 mTLS 或服务网格认证
- **算法实验平台**：多人共用，需 RBAC 区分普通用户/算法工程师
- **开放平台**：给第三方提供推荐 API，必须用 OAuth2 + API Key

---

## 常见误区

- ❌ **"我们内网，不需 HTTPS"** → k8s 集群内也需要 mTLS，防止横向渗透
- ❌ **"JWT Payload 加密了"** → Base64 只是编码，任何人能读，放敏感信息需额外加密
- ❌ **"限流影响用户体验"** → 合理限流（如 100次/分钟）普通用户无感知，保护的是服务稳定性
- ❌ **"加个 @require_auth 就行了"** → 认证通过 ≠ 授权通过，需分别检查权限
- ❌ **"返回所有数据，前端自己过滤"** → API 最小化原则，不返回不必要的字段
- ❌ **"密码存明文，登录时比对"** → 必须 bcrypt/argon2 哈希后存，不存明文

---

## 推荐系统安全架构总览

```
客户端请求（携带 JWT）
        ↓ HTTPS
    API Gateway
    ├─ SSL/TLS 终止
    ├─ IP 白名单（可选）
    ├─ 请求限流（令牌桶）
    ├─ 参数校验（Pydantic/JSON Schema）
    ├─ JWT 验签
    ├─ RBAC 权限检查
    ├─ 审计日志
    └─ 响应脱敏
        ↓ 内部 gRPC/HTTP（服务网格认证）
    业务服务层（推荐引擎）
        ↓
    数据层（Redis/MySQL/Hive）
        ↓
    模型推理服务（独立部署，鉴权）
```
