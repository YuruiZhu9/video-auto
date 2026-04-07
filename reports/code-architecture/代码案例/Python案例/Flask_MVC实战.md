# Python MVC 项目实战

## 目标
用 Flask 实现一个简单的用户管理系统，展示标准 MVC 架构。

## 项目结构

```
user_mvc/
├── app.py              # 入口
├── models/
│   ├── __init__.py
│   ├── user.py        # User模型
│   └── user_repo.py   # 数据操作
├── views/
│   ├── __init__.py
│   └── user_view.py   # 路由+控制器
├── services/
│   ├── __init__.py
│   └── user_service.py # 业务逻辑
└── database.py        # 数据库配置
```

---

## 1. 数据库配置

```python
# database.py
import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

db = Database()
```

---

## 2. Model 层

```python
# models/user.py
class User:
    def __init__(self, id=None, name=None, email=None, age=None):
        self.id = id
        self.name = name
        self.email = email
        self.age = age
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age
        }
    
    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return User(id=row[0], name=row[1], email=row[2], age=row[3])

# models/user_repo.py
from database import db

class UserRepository:
    def find_all(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, email, age FROM users')
            return [User.from_row(row) for row in cursor.fetchall()]
    
    def find_by_id(self, user_id):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, email, age FROM users WHERE id = ?', 
                          (user_id,))
            return User.from_row(cursor.fetchone())
    
    def find_by_email(self, email):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, email, age FROM users WHERE email = ?',
                          (email,))
            return User.from_row(cursor.fetchone())
    
    def create(self, user: User):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
                (user.name, user.email, user.age)
            )
            conn.commit()
            return cursor.lastrowid
    
    def update(self, user: User):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET name=?, email=?, age=? WHERE id=?',
                (user.name, user.email, user.age, user.id)
            )
            conn.commit()
    
    def delete(self, user_id):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
            conn.commit()
```

---

## 3. Service 层（业务逻辑）

```python
# services/user_service.py
from models.user import User
from models.user_repo import UserRepository

class UserService:
    def __init__(self):
        self.repo = UserRepository()
    
    def get_all_users(self):
        return self.repo.find_all()
    
    def get_user(self, user_id):
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user
    
    def create_user(self, name, email, age):
        # 业务验证
        if not name or not email:
            raise ValueError("Name and email are required")
        
        # 检查邮箱是否已存在
        existing = self.repo.find_by_email(email)
        if existing:
            raise ValueError(f"Email {email} already exists")
        
        user = User(name=name, email=email, age=age)
        user.id = self.repo.create(user)
        return user
    
    def update_user(self, user_id, name, email, age):
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # 检查邮箱是否被其他用户使用
        if email != user.email:
            existing = self.repo.find_by_email(email)
            if existing:
                raise ValueError(f"Email {email} already exists")
        
        user.name = name
        user.email = email
        user.age = age
        self.repo.update(user)
        return user
    
    def delete_user(self, user_id):
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        self.repo.delete(user_id)
```

---

## 4. View + Controller 层

```python
# views/user_view.py
from flask import Blueprint, request, jsonify
from services.user_service import UserService

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/users', methods=['GET'])
def list_users():
    """获取用户列表"""
    users = user_service.get_all_users()
    return jsonify([u.to_dict() for u in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    try:
        user = user_service.get_user(user_id)
        return jsonify(user.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@user_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.json
    try:
        user = user_service.create_user(
            name=data.get('name'),
            email=data.get('email'),
            age=data.get('age')
        )
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    data = request.json
    try:
        user = user_service.update_user(
            user_id=user_id,
            name=data.get('name'),
            email=data.get('email'),
            age=data.get('age')
        )
        return jsonify(user.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    try:
        user_service.delete_user(user_id)
        return jsonify({'status': 'deleted'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
```

---

## 5. 入口文件

```python
# app.py
from flask import Flask
from views.user_view import user_bp

app = Flask(__name__)
app.register_blueprint(user_bp)

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 架构说明

```
┌─────────────────────────────────────────┐
│            Views (Flask)                │
│   接收HTTP请求，返回JSON响应            │
│   路由 + 参数校验 + 调用Service         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Services                     │
│   业务逻辑处理                          │
│   验证规则、业务流程                    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Models                        │
│   数据模型 + 数据访问层                  │
│   User类 + UserRepository               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Database                      │
│   SQLite 数据库                          │
└─────────────────────────────────────────┘
```

## 运行方式

```bash
# 安装依赖
pip install flask

# 启动服务
python app.py

# 测试
curl http://localhost:5000/users
```
