# 单一职责原则 (SRP)

## 概念解释
每个类、函数、模块只负责**一件事**。当需要修改某个职责时，只有这一个原因会促使你改变它。

## 代码示例

### 反例（坏味道）
```python
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
    
    def save_to_db(self):
        # 保存到数据库
        pass
    
    def send_email(self):
        # 发送邮件
        pass
    
    def validate(self):
        # 验证数据
        pass
```
❌ 问题：User类同时处理数据、持久化、邮件、验证，职责过多

### 正例（改进后）
```python
# 纯粹的模型
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

# 验证器
class UserValidator:
    def validate(self, user: User):
        # 验证逻辑
        pass

# 仓库（数据持久化）
class UserRepository:
    def save(self, user: User):
        # 数据库操作
        pass

# 邮件服务
class EmailService:
    def send(self, user: User, message: str):
        # 发送邮件
        pass
```
✅ 优点：职责清晰，易于测试和维护

## 适用场景
- 团队协作开发
- 需要频繁修改的业务
- 编写可测试代码

## 常见误区
- ❌ 把所有代码塞进一个类
- ❌ 过度拆分（反而增加复杂度）
- ✅ 根据**变化原因**判断是否拆分
