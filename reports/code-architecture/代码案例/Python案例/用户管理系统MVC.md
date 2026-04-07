# Python MVC 案例 - 用户管理系统

## 项目结构
```
user_system/
├── models/
│   └── user.py
├── views/
│   └── user_view.py
├── controllers/
│   └── user_controller.py
├── repositories/
│   └── user_repository.py
└── app.py
```

## 代码实现

### Model - 数据模型
```python
# models/user.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
```

### Repository - 数据访问层
```python
# repositories/user_repository.py
from models.user import User
from typing import List, Optional

class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def find_all(self) -> List[User]:
        cursor = self.db.execute("SELECT * FROM users ORDER BY created_at DESC")
        return [User(*row[:4]) for row in cursor.fetchall()]
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        cursor = self.db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return User(*row[:4]) if row else None
    
    def find_by_email(self, email: str) -> Optional[User]:
        cursor = self.db.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return User(*row[:4]) if row else None
    
    def create(self, name: str, email: str) -> User:
        cursor = self.db.execute(
            "INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)",
            (name, email, datetime.now().isoformat())
        )
        return User(cursor.lastrowid, name, email)
    
    def update(self, user: User) -> bool:
        self.db.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (user.name, user.email, user.id)
        )
        return self.db.rowcount > 0
    
    def delete(self, user_id: int) -> bool:
        self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return self.db.rowcount > 0
```

### View - 视图层
```python
# views/user_view.py
from typing import List
from models.user import User
import json

def render_user_list(users: List[User]) -> str:
    """渲染用户列表页面"""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>用户管理</title></head>
    <body>
        <h1>用户列表</h1>
        <a href="/users/new">添加用户</a>
        <table border="1">
            <tr><th>ID</th><th>姓名</th><th>邮箱</th><th>操作</th></tr>
    """
    for user in users:
        html += f"""
            <tr>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>
                    <a href="/users/{user.id}/edit">编辑</a>
                    <a href="/users/{user.id}/delete">删除</a>
                </td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return html

def render_user_detail(user: User) -> str:
    """渲染用户详情"""
    return json.dumps(user.to_dict(), ensure_ascii=False, indent=2)

def render_success(message: str) -> str:
    """渲染成功消息"""
    return f"<script>alert('{message}'); window.location.href='/users';</script>"

def render_error(message: str) -> str:
    """渲染错误消息"""
    return f"<h2 style='color:red'>错误: {message}</h2>"
```

### Controller - 控制器层
```python
# controllers/user_controller.py
from repositories.user_repository import UserRepository
from views.user_view import render_user_list, render_user_detail
from views.user_view import render_success, render_error
from models.user import User

class UserController:
    def __init__(self, repository: UserRepository):
        self.repo = repository
    
    def list_users(self) -> str:
        try:
            users = self.repo.find_all()
            return render_user_list(users)
        except Exception as e:
            return render_error(str(e))
    
    def get_user(self, user_id: int) -> str:
        try:
            user = self.repo.find_by_id(user_id)
            if user:
                return render_user_detail(user)
            return render_error("用户不存在")
        except Exception as e:
            return render_error(str(e))
    
    def create_user(self, name: str, email: str) -> str:
        try:
            # 业务验证
            if not name or not email:
                return render_error("姓名和邮箱不能为空")
            
            existing = self.repo.find_by_email(email)
            if existing:
                return render_error("邮箱已被使用")
            
            user = self.repo.create(name, email)
            return render_success("用户创建成功")
        except Exception as e:
            return render_error(str(e))
    
    def update_user(self, user_id: int, name: str, email: str) -> str:
        try:
            user = self.repo.find_by_id(user_id)
            if not user:
                return render_error("用户不存在")
            
            user.name = name
            user.email = email
            
            self.repo.update(user)
            return render_success("用户更新成功")
        except Exception as e:
            return render_error(str(e))
    
    def delete_user(self, user_id: int) -> str:
        try:
            if self.repo.delete(user_id):
                return render_success("用户删除成功")
            return render_error("用户不存在")
        except Exception as e:
            return render_error(str(e))
```

### 主程序
```python
# app.py
from flask import Flask, request
from controllers.user_controller import UserController
from repositories.user_repository import UserRepository
import sqlite3

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

# 初始化依赖
db = init_db()
repo = UserRepository(db)
controller = UserController(repo)

# 路由
@app.route('/users')
def list_users():
    return controller.list_users()

@app.route('/users/<int:user_id>')
def get_user(user_id):
    return controller.get_user(user_id)

@app.route('/users/new', methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET':
        return "<form method='post'>...</form>"
    name = request.form.get('name')
    email = request.form.get('email')
    return controller.create_user(name, email)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def update_user(user_id):
    if request.method == 'GET':
        user = repo.find_by_id(user_id)
        return f"<form method='post'>...</form>"
    name = request.form.get('name')
    email = request.form.get('email')
    return controller.update_user(user_id, name, email)

@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    return controller.delete_user(user_id)

if __name__ == '__main__':
    app.run(debug=True)
```

## 架构优势

1. **职责清晰**：每层只做一件事
2. **易于测试**：各层可单独测试
3. **可扩展**：新增功能不影响现有代码
4. **易维护**：出问题快速定位
