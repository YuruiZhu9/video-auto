# Python MVC 实战：从零搭建用户管理系统

## 项目结构

```
user_manager/
├── models/
│   └── user.py          # Model 层
├── services/
│   └── user_service.py  # 业务逻辑层
├── controllers/
│   └── user_controller.py # Controller 层
├── repositories/
│   └── user_repository.py # 数据访问层
├── app.py               # 入口
└── requirements.txt
```

---

## 1. Model 层 - 定义数据模型

```python
# models/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """用户模型"""
    id: Optional[int]
    username: str
    email: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
    
    def validate(self) -> bool:
        """验证用户数据"""
        if not self.username or len(self.username) < 2:
            raise ValueError("用户名至少2个字符")
        if not self.email or '@' not in self.email:
            raise ValueError("邮箱格式不正确")
        return True
```

---

## 2. Repository 层 - 数据访问

```python
# repositories/user_repository.py
from typing import List, Optional
from models.user import User

class UserRepository:
    """用户数据访问层 - 单一职责：只管数据库操作"""
    
    def __init__(self):
        # 模拟数据库
        self._storage = {}
        self._id_counter = 1
    
    def save(self, user: User) -> User:
        """保存用户"""
        if user.id is None:
            user.id = self._id_counter
            self._id_counter += 1
        self._storage[user.id] = user
        return user
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """根据ID查找"""
        return self._storage.get(user_id)
    
    def find_all(self) -> List[User]:
        """查找所有用户"""
        return list(self._storage.values())
    
    def find_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找"""
        for user in self._storage.values():
            if user.username == username:
                return user
        return None
    
    def delete(self, user_id: int) -> bool:
        """删除用户"""
        if user_id in self._storage:
            del self._storage[user_id]
            return True
        return False
```

---

## 3. Service 层 - 业务逻辑

```python
# services/user_service.py
from typing import List, Optional
from models.user import User
from repositories.user_repository import UserRepository

class UserService:
    """用户服务层 - 单一职责：处理业务逻辑"""
    
    def __init__(self):
        self.repository = UserRepository()
    
    def create_user(self, username: str, email: str) -> User:
        """创建用户"""
        # 业务验证
        existing = self.repository.find_by_username(username)
        if existing:
            raise ValueError(f"用户名 {username} 已存在")
        
        # 创建用户
        user = User(id=None, username=username, email=email)
        user.validate()
        
        return self.repository.save(user)
    
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户"""
        return self.repository.find_by_id(user_id)
    
    def list_users(self) -> List[User]:
        """获取所有用户"""
        return self.repository.find_all()
    
    def update_user(self, user_id: int, username: str = None, 
                    email: str = None) -> Optional[User]:
        """更新用户"""
        user = self.repository.find_by_id(user_id)
        if not user:
            return None
        
        if username:
            user.username = username
        if email:
            user.email = email
        
        user.validate()
        return self.repository.save(user)
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        return self.repository.delete(user_id)
```

---

## 4. Controller 层 - 请求处理

```python
# controllers/user_controller.py
from flask import Blueprint, request, jsonify
from services.user_service import UserService

user_bp = Blueprint('users', __name__, url_prefix='/api/users')
user_service = UserService()

@user_bp.route('', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json()
    try:
        user = user_service.create_user(
            username=data['username'],
            email=data['email']
        )
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except KeyError as e:
        return jsonify({'error': f"缺少参数: {e}"}), 400

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify(user.to_dict())

@user_bp.route('', methods=['GET'])
def list_users():
    """获取用户列表"""
    users = user_service.list_users()
    return jsonify([u.to_dict() for u in users])

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    data = request.get_json()
    try:
        user = user_service.update_user(
            user_id=user_id,
            username=data.get('username'),
            email=data.get('email')
        )
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        return jsonify(user.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    success = user_service.delete_user(user_id)
    if not success:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({'message': '删除成功'})
```

---

## 5. 应用入口

```python
# app.py
from flask import Flask
from controllers.user_controller import user_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
```

---

## 架构说明

```
请求 → Controller (路由处理)
           ↓
       Service (业务逻辑)
           ↓
      Repository (数据访问)
           ↓
        Model (数据结构)
```

**每层职责清晰**：
- Controller：接收请求、参数校验、返回响应
- Service：业务逻辑处理
- Repository：数据库操作
- Model：数据结构定义

**优点**：
- 易于维护：改业务逻辑不影响数据访问
- 易于测试：每层可以单独测试
- 易于扩展：添加新功能只需在对应层添加代码
