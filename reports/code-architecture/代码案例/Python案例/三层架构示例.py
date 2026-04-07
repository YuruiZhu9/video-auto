# Python 代码架构案例

## 三层架构示例

### 项目结构
```
project/
├── presentation/
│   └── user_view.py
├── business/
│   └── user_service.py
├── data/
│   ├── user_model.py
│   └── user_repository.py
└── main.py
```

### 完整代码

#### 数据层 (Data Layer)
```python
# data/user_model.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int = None
    name: str = ""
    email: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

# data/user_repository.py
from data.user_model import User

class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def find_by_id(self, user_id: int) -> User:
        cursor = self.db.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(id=row[0], name=row[1], email=row[2], created_at=row[3])
        return None
    
    def find_by_email(self, email: str) -> User:
        cursor = self.db.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return User(id=row[0], name=row[1], email=row[2], created_at=row[3])
        return None
    
    def save(self, user: User) -> int:
        cursor = self.db.cursor()
        if user.id:
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (user.name, user.email, user.id)
            )
            return user.id
        else:
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (user.name, user.email)
            )
            return cursor.lastrowid
    
    def delete(self, user_id: int) -> bool:
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0
```

#### 业务层 (Business Layer)
```python
# business/user_service.py
from data.user_model import User
from data.user_repository import UserRepository

class ValidationError(Exception):
    pass

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, name: str, email: str) -> User:
        # 业务验证
        self._validate_name(name)
        self._validate_email(email)
        
        # 检查邮箱是否已存在
        existing = self.user_repo.find_by_email(email)
        if existing:
            raise ValidationError("邮箱已被注册")
        
        # 创建用户
        user = User(name=name, email=email)
        user.id = self.user_repo.save(user)
        return user
    
    def update_user(self, user_id: int, name: str = None, email: str = None) -> User:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValidationError("用户不存在")
        
        if name:
            self._validate_name(name)
            user.name = name
        
        if email:
            self._validate_email(email)
            # 检查新邮箱是否被占用
            existing = self.user_repo.find_by_email(email)
            if existing and existing.id != user_id:
                raise ValidationError("邮箱已被注册")
            user.email = email
        
        self.user_repo.save(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValidationError("用户不存在")
        return self.user_repo.delete(user_id)
    
    def get_user(self, user_id: int) -> User:
        return self.user_repo.find_by_id(user_id)
    
    def _validate_name(self, name: str):
        if not name or len(name.strip()) < 2:
            raise ValidationError("用户名至少2个字符")
        if len(name) > 50:
            raise ValidationError("用户名不能超过50个字符")
    
    def _validate_email(self, email: str):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("邮箱格式不正确")
```

#### 表现层 (Presentation Layer)
```python
# presentation/user_view.py
from business.user_service import UserService, ValidationError

def render_user_list(users):
    html = "<h2>用户列表</h2><ul>"
    for user in users:
        html += f"<li>{user.name} ({user.email})</li>"
    html += "</ul>"
    return html

def render_user_detail(user):
    return f"""
    <div class="user-detail">
        <h2>{user.name}</h2>
        <p>邮箱: {user.email}</p>
        <p>注册时间: {user.created_at}</p>
    </div>
    """

def render_error(error):
    return f'<div class="error">{error}</div>'

def render_success(message):
    return f'<div class="success">{message}</div>'

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def list_users(self):
        # 业务逻辑由service处理
        # 这里只负责接收请求和返回响应
        return render_user_list([])
    
    def get_user(self, user_id):
        try:
            user = self.user_service.get_user(user_id)
            if not user:
                return render_error("用户不存在")
            return render_user_detail(user)
        except ValidationError as e:
            return render_error(str(e))
    
    def create_user(self, name, email):
        try:
            user = self.user_service.create_user(name, email)
            return render_success(f"用户 {user.name} 创建成功")
        except ValidationError as e:
            return render_error(str(e))
```

---

## 依赖注入示例

```python
# main.py
import sqlite3
from data.user_repository import UserRepository
from business.user_service import UserService
from presentation.user_view import UserController

# 组装应用（依赖注入）
db = sqlite3.connect('app.db')
user_repo = UserRepository(db)
user_service = UserService(user_repo)
user_controller = UserController(user_service)

# 使用
response = user_controller.create_user("张三", "zhangsan@example.com")
print(response)
```

---

## 使用Flask的MVC示例

```python
# app.py
from flask import Flask, request, jsonify
from data.user_repository import UserRepository
from business.user_service import UserService
from presentation.user_view import UserController

app = Flask(__name__)

# 依赖注入容器
class Container:
    def __init__(self):
        self.db = sqlite3.connect('app.db')
        self.user_repo = UserRepository(self.db)
        self.user_service = UserService(self.user_repo)
        self.user_controller = UserController(self.user_service)

container = Container()

@app.route('/users', methods=['GET'])
def list_users():
    return container.user_controller.list_users()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return container.user_controller.get_user(user_id)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    return container.user_controller.create_user(
        data['name'], 
        data['email']
    )

if __name__ == '__main__':
    app.run(debug=True)
```
