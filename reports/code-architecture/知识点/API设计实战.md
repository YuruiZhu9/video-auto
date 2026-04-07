# API 设计实战：从设计到落地

## 概念解释

API（Application Programming Interface）是系统与系统、模块与模块之间的「合约」。好的 API 设计让调用者用得爽，坏的 API 设计让调用者想砸键盘。

API 设计不是后端开发才需要考虑的——前端、后端、移动端、AI Agent 都在调用 API。一个设计糟糕的 API 会：

- **内部**：让团队成员互相甩锅，接口文档永远对不上实现
- **外部**：让合作伙伴集成成本暴增，最终选择竞品

### RESTful API 是什么？

REST（Representational State Transfer）是 Roy Fielding 在 2000 年提出的架构风格。RESTful API 是遵循 REST 原则设计的 API。

**6个核心约束：**
1. **客户端-服务器分离**：客户端不关心服务端存储，服务器不关心客户端状态
2. **无状态**：每个请求包含所有必要信息，服务器不存储客户端上下文
3. **可缓存**：响应可标记为可缓存或不可缓存
4. **分层系统**：客户端不需要知道连接的是终点还是中间层
5. **按需代码**（可选）：服务端可临时扩展客户端功能
6. **统一接口**：资源通过 URL 定位，操作通过 HTTP 方法表达

### 什么是好的 API 设计？

> **Bruce Johnson's Three Laws of API Design:**
> 1. API 应该对调用者友好（easy to use correctly）
> 2. API 应该防止误用（hard to use incorrectly）
> 3. API 应该清晰明了（clear in intent）

---

## 代码示例

### 反例（坏味道）

#### 1. RESTful 风格缺失

```python
# ❌ 糟糕的 API 设计：动词出现在 URL 中
@app.route('/api/getUser', methods=['GET'])
def get_user():
    pass

@app.route('/api/createUser', methods=['POST'])
def create_user():
    pass

@app.route('/api/deleteUser', methods=['POST'])
def delete_user():
    pass

@app.route('/api/updateUser', methods=['POST'])
def update_user():
    pass
```

**问题分析：**
- 把 HTTP 方法当摆设，所有操作都用 POST
- URL 中混入动作动词，不符合 REST 资源导向思想
- `getUser`、`createUser`、`deleteUser`、`updateUser` 四个接口，操作的都是 `User` 资源，应该合并

#### 2. URL 层级混乱

```python
# ❌ URL 层级不清晰，嵌套过深
GET /api/v1/organizations/123/users/456/permissions/789
```

**问题分析：**
- 超过 2 层嵌套，URL 脆弱且难以维护
- 删除用户 456 后，这个 URL 就失效了，但可能还被其他地方引用
- 应该直接用 `/api/v1/users/456/permissions/789`

#### 3. 响应格式不一致

```python
# ❌ 没有统一响应格式，各接口各搞各的
@app.route('/api/user/<id>', methods=['GET'])
def get_user(id):
    user = db.query(id)
    # 有的返回字符串
    if not user:
        return "User not found", 404
    # 有的返回字典
    return {"name": user.name, "email": user.email}

@app.route('/api/users', methods=['GET'])
def list_users():
    users = db.query_all()
    # 又返回列表
    return [u.to_dict() for u in users]
```

**问题分析：**
- 有的接口返回字符串，有的返回字典，有的返回列表
- 客户端需要针对每个接口写不同的解析逻辑
- 没有统一的错误处理，日志难以追踪

#### 4. 状态码乱用

```python
# ❌ HTTP 状态码乱用，所有错误都返回 200 + 错误信息
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = auth(data['username'], data['password'])
    if not user:
        # 认证失败却返回 200
        return {"code": 401, "msg": "密码错误"}
    return {"code": 0, "data": user.to_dict()}
```

**问题分析：**
- HTTP 状态码 200 表示「成功」，但这里明明是认证失败
- 客户端收到 200 后还要再解析 body 里的 code 字段才能知道结果
- 违反 HTTP 语义，CDN/网关等中间层无法正确处理

#### 5. 不做参数校验

```python
# ❌ 不校验参数，错误信息不友好
@app.route('/api/users/<id>/orders', methods=['GET'])
def get_user_orders(id):
    # id 如果不是数字则直接抛数据库异常
    orders = db.query("SELECT * FROM orders WHERE user_id = %s", id)
    return [o.to_dict() for o in orders]
    # 如果 id = "abc"，返回的是数据库错误而非友好的 400
```

---

### 正例（改进后）

#### 1. 标准 RESTful 风格

```python
# ✅ 好的 API 设计：资源 + HTTP 方法
from flask import Flask, jsonify, request, abort
from functools import wraps

app = Flask(__name__)

# ─────────────────────────────────────
# 统一响应格式
# ─────────────────────────────────────
def api_response(data=None, message="success", code=0):
    """统一 API 响应格式"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), 200 if code == 0 else get_status_code(code)

def get_status_code(code):
    """根据业务错误码映射 HTTP 状态码"""
    mapping = {
        0:    200,  # 成功
        4001: 400,  # 参数错误
        4002: 422,  # 语义错误
        4011: 401,  # 未认证
        4012: 403,  # 无权限
        4041: 404,  # 资源不存在
        5000: 500,  # 服务器错误
    }
    return mapping.get(code, 200)

# ─────────────────────────────────────
# 用户资源 RESTful 接口
# ─────────────────────────────────────
users_db = {}  # 模拟数据库: {id: User}
next_user_id = 1

class User:
    def __init__(self, name, email, role="user"):
        global next_user_id
        self.id = next_user_id
        next_user_id += 1
        self.name = name
        self.email = email
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role
        }

# GET    /api/v1/users        →  获取用户列表（支持分页）
# POST   /api/v1/users        →  创建用户
# GET    /api/v1/users/<id>    →  获取单个用户
# PUT    /api/v1/users/<id>    →  全量更新用户
# PATCH  /api/v1/users/<id>    →  部分更新用户
# DELETE /api/v1/users/<id>    →  删除用户

@app.route('/api/v1/users', methods=['GET'])
def list_users():
    """获取用户列表（分页 + 过滤）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    role = request.args.get('role', None)

    # 参数校验
    if page < 1 or page_size < 1 or page_size > 100:
        return api_response(message="参数错误：page >= 1, 1 <= page_size <= 100", code=4001)

    filtered = list(users_db.values())
    if role:
        filtered = [u for u in filtered if u.role == role]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = [u.to_dict() for u in filtered[start:end]]

    return api_response(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    })

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json()
    if not data:
        return api_response(message="请求体不能为空", code=4001)
    if 'name' not in data or 'email' not in data:
        return api_response(message="name 和 email 为必填字段", code=4001)
    if not validate_email(data['email']):
        return api_response(message="email 格式不正确", code=4002)

    user = User(name=data['name'], email=data['email'], role=data.get('role', 'user'))
    users_db[user.id] = user
    return api_response(data=user.to_dict(), message="创建成功", code=0), 201

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = users_db.get(user_id)
    if not user:
        return api_response(message=f"用户 {user_id} 不存在", code=4041)
    return api_response(data=user.to_dict())

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def replace_user(user_id):
    """全量更新用户（PUT 需要提供所有字段）"""
    user = users_db.get(user_id)
    if not user:
        return api_response(message=f"用户 {user_id} 不存在", code=4041)

    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return api_response(message="name 和 email 为必填字段", code=4001)

    user.name = data['name']
    user.email = data['email']
    user.role = data.get('role', user.role)
    return api_response(data=user.to_dict(), message="更新成功")

@app.route('/api/v1/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    """部分更新用户（只更新提供的字段）"""
    user = users_db.get(user_id)
    if not user:
        return api_response(message=f"用户 {user_id} 不存在", code=4041)

    data = request.get_json()
    if not data:
        return api_response(message="请求体不能为空", code=4001)

    # 只更新提供的字段
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        if not validate_email(data['email']):
            return api_response(message="email 格式不正确", code=4002)
        user.email = data['email']
    if 'role' in data:
        if data['role'] not in ('user', 'admin'):
            return api_response(message="role 必须是 user 或 admin", code=4002)
        user.role = data['role']

    return api_response(data=user.to_dict(), message="更新成功")

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    if user_id not in users_db:
        return api_response(message=f"用户 {user_id} 不存在", code=4041)
    del users_db[user_id]
    return api_response(message="删除成功")

def validate_email(email):
    import re
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))
```

#### 2. 错误处理中间件

```python
# ✅ 全局错误处理 + 统一异常类
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

class APIException(Exception):
    """业务 API 异常基类"""
    def __init__(self, message, code=5000, status_code=500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class NotFoundException(APIException):
    def __init__(self, resource, resource_id):
        super().__init__(
            message=f"{resource} {resource_id} 不存在",
            code=4041,
            status_code=404
        )

class ValidationException(APIException):
    def __init__(self, message):
        super().__init__(message=message, code=4001, status_code=400)

@app.errorhandler(APIException)
def handle_api_exception(e):
    """捕获所有 API 业务异常"""
    return jsonify({
        "code": e.code,
        "message": e.message,
        "data": None
    }), e.status_code

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """捕获所有 HTTP 框架异常"""
    return jsonify({
        "code": 4000 + e.code,
        "message": e.description,
        "data": None
    }), e.code

@app.errorhandler(Exception)
def handle_generic_exception(e):
    """捕获未预期异常（生产环境不要暴露详细信息）"""
    # 记录日志
    print(f"[ERROR] {request.method} {request.path}: {e}")
    return jsonify({
        "code": 5000,
        "message": "服务器内部错误",
        "data": None
    }), 500

# 现在所有接口都可以用 raise ValidationException() 来报错
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.get(user_id)
    if not user:
        raise NotFoundException("用户", user_id)
    return jsonify({"code": 0, "data": user.to_dict()})
```

#### 3. 版本管理策略

```python
# ✅ URL 版本控制：/api/v1/ /api/v2/
# 演进策略：
# 1. v1 → v2：新字段、增加功能、字段改名（旧接口可继续用6个月）
# 2. 不做 v1.1：小版本在 URL 里无意义
# 3. 废弃标注：通过响应头告知：Deprecation: true, Sunset: Sat, 01 Jan 2027 00:00:00 GMT

@app.route('/api/v1/recommend', methods=['GET'])
def recommend_v1():
    """v1 版本：只支持基于协同过滤的推荐"""
    user_id = request.args.get('user_id', type=int)
    return jsonify({
        "code": 0,
        "data": {
            "items": collaborative_filter_recommend(user_id, top_k=10)
        },
        "version": "v1",
        "deprecated": True,
        "sunset_date": "2026-06-01"
    })

@app.route('/api/v2/recommend', methods=['GET'])
def recommend_v2():
    """v2 版本：融合协同过滤 + 大模型解释"""
    user_id = request.args.get('user_id', type=int)
    strategy = request.args.get('strategy', 'hybrid')  # hybrid | cf | llm
    return jsonify({
        "code": 0,
        "data": {
            "items": hybrid_recommend(user_id, strategy=strategy, top_k=20),
            "explanations": generate_explanations(user_id)
        },
        "version": "v2"
    })
```

#### 4. 分页与过滤

```python
# ✅ 游标分页（适合大数据量）+ 偏移分页（适合小数据量）
from flask import request, jsonify

class CursorPagination:
    """游标分页：适合数据量大的列表，避免深度分页性能问题"""
    def __init__(self, query, cursor_field="id", order="desc"):
        self.query = query
        self.cursor_field = cursor_field
        self.order = order

    def get_page(self, cursor=None, limit=20):
        q = self.query
        if cursor is not None:
            op = ">" if self.order == "asc" else "<"
            q = q.filter(getattr(self.query._entities[0].entity, self.cursor_field).operation(op, cursor))

        q = q.order_by(
            getattr(self.query._entities[0].entity, self.cursor_field).
            operation("asc" if self.order == "asc" else "desc")
        )
        items = q.limit(limit + 1).all()

        has_next = len(items) > limit
        if has_next:
            items = items[:-1]

        next_cursor = getattr(items[-1], self.cursor_field) if items and has_next else None
        return items, next_cursor

@app.route('/api/v1/feed', methods=['GET'])
def get_feed():
    """信息流：适合用游标分页，滚动加载"""
    cursor = request.args.get('cursor', None)
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)  # 上限保护

    items, next_cursor = CursorPagination(
        query=db.query(FeedItem).filter(FeedItem.published == True),
        cursor_field="created_at"
    ).get_page(cursor=cursor, limit=limit)

    return jsonify({
        "code": 0,
        "data": {
            "items": [item.to_dict() for item in items],
            "next_cursor": str(next_cursor.timestamp()) if next_cursor else None,
            "has_next": next_cursor is not None
        }
    })
```

#### 5. GraphQL vs REST 场景选择

```python
# ✅ 什么时候用 REST vs GraphQL？

# REST 适用场景：
# - 资源导向的操作（CRUD）
# - 需要 HTTP 缓存（CDN/浏览器缓存）
# - 简单的一次性请求
# - 公开 API，需要好的文档和易用性

# GraphQL 适用场景：
# - 客户端需要灵活获取不同字段
# - 多次请求可以合并为一次
# - 数据关联复杂（嵌套资源）
# - 移动端需要减少网络开销

# 实际项目中推荐：REST + OpenAPI 文档作为主方案，
# 特定复杂场景（后台管理、内部工具）补充 GraphQL

# FastAPI + OpenAPI 自动生成文档
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import Optional

app = FastAPI(
    title="推荐系统 API",
    version="1.0.0",
    description="个性化推荐服务 API",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc（更美观）
)

class UserCreate(BaseModel):
    name: str
    email: EmailStr  # 自动 Email 格式校验
    role: Optional[str] = "user"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

@app.post("/api/v1/users", response_model=UserResponse, status_code=201, tags=["用户"])
async def create_user(user: UserCreate):
    """创建用户

    - **name**: 用户名（必填）
    - **email**: 邮箱（必填，格式校验）
    - **role**: 角色（可选，默认 user）
    """
    new_user = User(name=user.name, email=user.email, role=user.role)
    return new_user
# 访问 http://host/docs 即可看到自动生成的 Swagger 文档
```

---

## 适用场景

**REST API 设计的核心原则（ Richardson 成熟度模型 Level 3 ）：**

| 层级 | 描述 | 实现度 |
|------|------|--------|
| Level 0 | 一个 URL，所有操作通过 POST | ❌ |
| Level 1 | 每个资源一个 URL，但都是 POST | ⚠️ |
| Level 2 | 正确的 HTTP 方法（GET/POST/PUT/DELETE） | ✅ |
| Level 3 | 超媒体即应用状态引擎（HATEOAS） | 🏆 |

**日常工作场景：**
- 设计内部微服务接口
- 提供对外公开 API
- 前后端数据接口约定
- AI Agent 调用外部工具的接口设计

---

## 常见误区

### ❌ 误区 1：把所有接口都设计成 POST

HTTP 方法不是摆设。`GET` 是安全的、可缓存的；`POST` 是非幂等的。乱用方法会导致：
- 浏览器/CDN 无法正确缓存
- 搜索引擎无法索引
- 安全扫描工具误报

### ❌ 误区 2：把业务错误码塞进 HTTP 状态码

HTTP 状态码表示「HTTP 层」的错误，不是「业务层」的错误。

```
✅ 正确：
  HTTP 400 + body: {"code": 4001, "message": "邮箱格式不正确"}

❌ 错误：
  HTTP 400 + body: {"code": 0, "message": "操作成功"}
  （200 + 自定义错误码 = 语义混乱）
```

### ❌ 误区 3：返回的数据结构不统一

每个接口返回格式都不一样，调用者需要写大量适配代码。**一个团队、一个响应格式。**

### ❌ 误区 4：不在文档里说明字段含义

API 文档缺少字段说明，让调用者靠猜：
- 日期是什么格式？ISO8601 还是时间戳？
- 分页的 page 是从 0 还是从 1 开始？
- 创建时间用什么时区？UTC 还是本地时间？

### ❌ 误区 5：API 版本控制混乱

没有版本规划，接口改着改着就breaking change了：
- 所有用户都在用的接口没法改
- 只能无限向后兼容，积重难返

**正确的版本规划：**
1. 上线时就定好版本 `/api/v1/`
2. v2 不兼容时，v1 再维护至少 6 个月
3. 废弃接口在响应头里标注 `Deprecation` 和 `Sunset`

---

## 进阶话题

### 认证与授权

```python
# JWT Bearer Token 认证
from functools import wraps
import jwt
import time

SECRET_KEY = "your-secret-key"  # 生产环境用环境变量

def generate_token(user_id, role):
    return jwt.encode({
        "user_id": user_id,
        "role": role,
        "exp": int(time.time()) + 3600 * 24 * 7  # 7天过期
    }, SECRET_KEY, algorithm="HS256")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return api_response(message="缺少认证 Token", code=4011), 401

        token = auth_header[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = payload['user_id']
            request.user_role = payload['role']
        except jwt.ExpiredSignatureError:
            return api_response(message="Token 已过期", code=4011), 401
        except jwt.InvalidTokenError:
            return api_response(message="无效的 Token", code=4011), 401

        return f(*args, **kwargs)
    return decorated

def require_role(role):
    """RBAC：角色权限控制"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.user_role != role and request.user_role != 'admin':
                return api_response(message="权限不足", code=4012), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/api/v1/admin/users', methods=['GET'])
@require_auth
@require_role('admin')
def list_all_users_admin():
    """只有 admin 才能访问"""
    return api_response(data=[u.to_dict() for u in users_db.values()])
```

### 限流保护

```python
# 简单的 IP + 时间窗口限流
from collections import defaultdict
import time

rate_limit_store = defaultdict(list)  # {ip: [timestamp1, timestamp2...]}

def rate_limit(limit=60, window=60):
    """限流装饰器：默认每 60 秒最多 60 次"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            window_start = now - window

            # 清理过期记录
            rate_limit_store[ip] = [t for t in rate_limit_store[ip] if t > window_start]

            if len(rate_limit_store[ip]) >= limit:
                return jsonify({
                    "code": 4290,
                    "message": f"请求过于频繁，请 {int(window - (now - rate_limit_store[ip][0])) + 1} 秒后重试",
                    "retry_after": window
                }), 429

            rate_limit_store[ip].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/api/v1/feed', methods=['GET'])
@rate_limit(limit=60, window=60)  # 每分钟60次
def get_feed():
    return api_response(data=...)
```

### API 设计 Checklist

```
□ 资源用名词复数：/users 而非 /getUser
□ 正确使用 HTTP 方法：GET(查)/POST(增)/PUT(改)/DELETE(删)
□ 统一响应格式：{code, message, data}
□ 合理使用 HTTP 状态码：2xx成功/4xx客户端错误/5xx服务端错误
□ 输入参数校验 + 友好的错误提示
□ 分页：超过 20 条必须分页
□ API 版本控制：从 v1 开始
□ 认证鉴权：敏感接口必须有
□ 限流：公开接口必须限流
□ 文档：OpenAPI/Swagger 自动生成
□ 幂等性：PUT/DELETE 天然幂等，POST 操作需特别处理
□ 时区：所有时间统一 UTC ISO8601
□ 安全：防止 SQL 注入、XSS（参数化查询 + 输出转义）
□ 变更日志：记录每个版本的变更内容
```

---

## 推荐学习路径

1. **入门**：[RESTful API 设计指南](https://docs.microsoft.com/zh-cn/azure/architecture/best-practices/api-design)（微软官方）
2. **进阶**：《API Design Patterns》— JJ Geewax（Google 工程师著）
3. **实战**：阮一峰《RESTful API 最佳实践》
4. **工具**：Postman / Insomnia + OpenAPI 自动生成客户端 SDK
