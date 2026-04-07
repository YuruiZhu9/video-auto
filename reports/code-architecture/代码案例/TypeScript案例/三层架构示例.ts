# TypeScript 代码架构案例

## 三层架构示例

### 项目结构
```
src/
├── presentation/
│   └── user.controller.ts
├── business/
│   ├── user.service.ts
│   └── validation.error.ts
├── data/
│   ├── user.model.ts
│   └── user.repository.ts
├── types/
│   └── index.ts
└── main.ts
```

### 完整代码

#### 类型定义
```typescript
// types/index.ts
export interface User {
  id?: number;
  name: string;
  email: string;
  createdAt?: Date;
}

export interface CreateUserDto {
  name: string;
  email: string;
}

export interface UpdateUserDto {
  name?: string;
  email?: string;
}
```

#### 数据层 (Data Layer)
```typescript
// data/user.model.ts
export class UserModel {
  constructor(
    public id: number,
    public name: string,
    public email: string,
    public createdAt: Date = new Date()
  ) {}
}

// data/user.repository.ts
import { User, CreateUserDto, UpdateUserDto } from '../types';
import { UserModel } from './user.model';

interface Database {
  query(sql: string, params?: any[]): any[];
  run(sql: string, params?: any[]): { lastID: number; changes: number };
}

export class UserRepository {
  constructor(private db: Database) {}

  private mapToModel(row: any): UserModel | null {
    if (!row) return null;
    return new UserModel(row.id, row.name, row.email, new Date(row.created_at));
  }

  findById(id: number): UserModel | null {
    const rows = this.db.query('SELECT * FROM users WHERE id = ?', [id]);
    return this.mapToModel(rows[0]);
  }

  findByEmail(email: string): UserModel | null {
    const rows = this.db.query('SELECT * FROM users WHERE email = ?', [email]);
    return this.mapToModel(rows[0]);
  }

  findAll(): UserModel[] {
    const rows = this.db.query('SELECT * FROM users ORDER BY created_at DESC');
    return rows.map(row => this.mapToModel(row)!);
  }

  create(dto: CreateUserDto): UserModel {
    const result = this.db.run(
      'INSERT INTO users (name, email) VALUES (?, ?)',
      [dto.name, dto.email]
    );
    return new UserModel(result.lastID, dto.name, dto.email);
  }

  update(id: number, dto: UpdateUserDto): UserModel | null {
    const user = this.findById(id);
    if (!user) return null;

    const updates: string[] = [];
    const params: any[] = [];

    if (dto.name !== undefined) {
      updates.push('name = ?');
      params.push(dto.name);
    }
    if (dto.email !== undefined) {
      updates.push('email = ?');
      params.push(dto.email);
    }

    if (updates.length === 0) return user;

    params.push(id);
    this.db.run(`UPDATE users SET ${updates.join(', ')} WHERE id = ?`, params);
    
    return this.findById(id);
  }

  delete(id: number): boolean {
    const result = this.db.run('DELETE FROM users WHERE id = ?', [id]);
    return result.changes > 0;
  }
}
```

#### 业务层 (Business Layer)
```typescript
// business/validation.error.ts
export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// business/user.service.ts
import { User, CreateUserDto, UpdateUserDto } from '../types';
import { UserRepository } from '../data/user.repository';
import { ValidationError } from './validation.error';

export class UserService {
  constructor(private userRepo: UserRepository) {}

  private validateName(name: string): void {
    if (!name || name.trim().length < 2) {
      throw new ValidationError('用户名至少2个字符');
    }
    if (name.length > 50) {
      throw new ValidationError('用户名不能超过50个字符');
    }
  }

  private validateEmail(email: string): void {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      throw new ValidationError('邮箱格式不正确');
    }
  }

  create(dto: CreateUserDto): User {
    this.validateName(dto.name);
    this.validateEmail(dto.email);

    // 检查邮箱是否已存在
    const existing = this.userRepo.findByEmail(dto.email);
    if (existing) {
      throw new ValidationError('邮箱已被注册');
    }

    return this.userRepo.create(dto);
  }

  update(id: number, dto: UpdateUserDto): User {
    const user = this.userRepo.findById(id);
    if (!user) {
      throw new ValidationError('用户不存在');
    }

    if (dto.name) {
      this.validateName(dto.name);
    }
    if (dto.email) {
      this.validateEmail(dto.email);
      // 检查新邮箱是否被占用
      const existing = this.userRepo.findByEmail(dto.email);
      if (existing && existing.id !== id) {
        throw new ValidationError('邮箱已被注册');
      }
    }

    const updated = this.userRepo.update(id, dto);
    if (!updated) {
      throw new ValidationError('更新失败');
    }
    return updated;
  }

  delete(id: number): boolean {
    const user = this.userRepo.findById(id);
    if (!user) {
      throw new ValidationError('用户不存在');
    }
    return this.userRepo.delete(id);
  }

  findById(id: number): User | null {
    return this.userRepo.findById(id);
  }

  findAll(): User[] {
    return this.userRepo.findAll();
  }
}
```

#### 表现层 (Presentation Layer)
```typescript
// presentation/user.controller.ts
import { User, CreateUserDto, UpdateUserDto } from '../types';
import { UserService } from '../business/user.service';
import { ValidationError } from '../business/validation.error';

export interface HttpResponse {
  statusCode: number;
  body: string;
}

export class UserController {
  constructor(private userService: UserService) {}

  private success(data: any): HttpResponse {
    return {
      statusCode: 200,
      body: JSON.stringify({ success: true, data })
    };
  }

  private error(message: string, statusCode: number = 400): HttpResponse {
    return {
      statusCode,
      body: JSON.stringify({ success: false, error: message })
    };
  }

  list(): HttpResponse {
    try {
      const users = this.userService.findAll();
      return this.success(users);
    } catch (e) {
      return this.error(e.message);
    }
  }

  get(id: number): HttpResponse {
    try {
      const user = this.userService.findById(id);
      if (!user) {
        return this.error('用户不存在', 404);
      }
      return this.success(user);
    } catch (e) {
      return this.error(e.message);
    }
  }

  create(body: CreateUserDto): HttpResponse {
    try {
      const user = this.userService.create(body);
      return this.success(user);
    } catch (e) {
      if (e instanceof ValidationError) {
        return this.error(e.message);
      }
      return this.error('创建失败');
    }
  }

  update(id: number, body: UpdateUserDto): HttpResponse {
    try {
      const user = this.userService.update(id, body);
      return this.success(user);
    } catch (e) {
      if (e instanceof ValidationError) {
        return this.error(e.message);
      }
      return this.error('更新失败');
    }
  }

  delete(id: number): HttpResponse {
    try {
      const result = this.userService.delete(id);
      return this.success({ deleted: result });
    } catch (e) {
      if (e instanceof ValidationError) {
        return this.error(e.message);
      }
      return this.error('删除失败');
    }
  }
}
```

---

## 依赖注入示例

```typescript
// main.ts
import express from 'express';
import { UserRepository } from './data/user.repository';
import { UserService } from './business/user.service';
import { UserController } from './presentation/user.controller';

// 模拟数据库
const mockDb = {
  query: (sql: string, params: any[]) => [],
  run: (sql: string, params: any[]) => ({ lastID: 1, changes: 1 })
};

// 依赖注入
const userRepo = new UserRepository(mockDb);
const userService = new UserService(userRepo);
const userController = new UserController(userService);

// Express 路由
const app = express();
app.use(express.json());

app.get('/users', (req, res) => {
  const response = userController.list();
  res.status(response.statusCode).send(response.body);
});

app.get('/users/:id', (req, res) => {
  const response = userController.get(parseInt(req.params.id));
  res.status(response.statusCode).send(response.body);
});

app.post('/users', (req, res) => {
  const response = userController.create(req.body);
  res.status(response.statusCode).send(response.body);
});

app.put('/users/:id', (req, res) => {
  const response = userController.update(parseInt(req.params.id), req.body);
  res.status(response.statusCode).send(response.body);
});

app.delete('/users/:id', (req, res) => {
  const response = userController.delete(parseInt(req.params.id));
  res.status(response.statusCode).send(response.body);
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

---

## NestJS 风格示例

```typescript
// users/user.entity.ts
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column({ unique: true })
  email: string;

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}

// users/dto/create-user.dto.ts
export class CreateUserDto {
  name: string;
  email: string;
}

// users/users.service.ts
import { Injectable, ValidationError } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';
import { CreateUserDto } from './dto/create-user.dto';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async create(dto: CreateUserDto): Promise<User> {
    const existing = await this.userRepository.findOne({ where: { email: dto.email } });
    if (existing) {
      throw new ValidationError('邮箱已被注册');
    }
    
    const user = this.userRepository.create(dto);
    return this.userRepository.save(user);
  }

  async findAll(): Promise<User[]> {
    return this.userRepository.find();
  }

  async findOne(id: number): Promise<User> {
    return this.userRepository.findOne({ where: { id } });
  }

  async delete(id: number): Promise<void> {
    await this.userRepository.delete(id);
  }
}

// users/users.controller.ts
import { Controller, Get, Post, Body, Param, Delete } from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  create(@Body() createUserDto: CreateUserDto) {
    return this.usersService.create(createUserDto);
  }

  @Get()
  findAll() {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(+id);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    return this.usersService.remove(+id);
  }
}
```
