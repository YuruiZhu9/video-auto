# TypeScript 代码架构案例

## 案例：NestJS企业级架构

### 项目结构

```
src/
├── main.ts
├── app.module.ts
├── config/
│   └── configuration.ts
├── common/
│   ├── decorators/
│   ├── filters/
│   ├── interceptors/
│   └── guards/
├── modules/
│   ├── users/
│   │   ├── dto/
│   │   │   ├── create-user.dto.ts
│   │   │   └── update-user.dto.ts
│   │   ├── entities/
│   │   │   └── user.entity.ts
│   │   ├── interfaces/
│   │   │   └── user.interface.ts
│   │   ├── users.controller.ts
│   │   ├── users.service.ts
│   │   ├── users.module.ts
│   │   └── users.repository.ts
│   └── auth/
└── shared/
    └── utils/
```

### 完整示例

```typescript
// modules/users/entities/user.entity.ts
export class User {
  id: number;
  name: string;
  email: string;
  password: string;
  createdAt: Date;
  updatedAt: Date;

  constructor(partial: Partial<User>) {
    Object.assign(this, partial);
  }
}

// modules/users/dto/create-user.dto.ts
import { IsEmail, IsString, MinLength } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @MinLength(2)
  name: string;

  @IsEmail()
  email: string;

  @IsString()
  @MinLength(6)
  password: string;
}

// modules/users/interfaces/user.interface.ts
export interface IUserRepository {
  findAll(): Promise<User[]>;
  findOne(id: number): Promise<User | null>;
  create(user: Partial<User>): Promise<User>;
  update(id: number, user: Partial<User>): Promise<User>;
  delete(id: number): Promise<void>;
}

// modules/users/users.repository.ts
import { Injectable } from '@nestjs/common';
import { User } from './entities/user.entity';
import { IUserRepository } from './interfaces/user.interface';

// 模拟数据库
const users: User[] = [];

@Injectable()
export class UsersRepository implements IUserRepository {
  async findAll(): Promise<User[]> {
    return users;
  }

  async findOne(id: number): Promise<User | null> {
    return users.find(u => u.id === id) || null;
  }

  async create(userData: Partial<User>): Promise<User> {
    const user = new User({
      ...userData,
      id: users.length + 1,
      createdAt: new Date(),
      updatedAt: new Date(),
    } as User);
    users.push(user);
    return user;
  }

  async update(id: number, userData: Partial<User>): Promise<User> {
    const index = users.findIndex(u => u.id === id);
    if (index === -1) throw new Error('User not found');
    
    users[index] = { ...users[index], ...userData, updatedAt: new Date() };
    return users[index];
  }

  async delete(id: number): Promise<void> {
    const index = users.findIndex(u => u.id === id);
    if (index !== -1) users.splice(index, 1);
  }
}

// modules/users/users.service.ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { UsersRepository } from './users.repository';
import { CreateUserDto } from './dto/create-user.dto';
import { User } from './entities/user.entity';

@Injectable()
export class UsersService {
  constructor(private readonly usersRepository: UsersRepository) {}

  async findAll(): Promise<User[]> {
    return this.usersRepository.findAll();
  }

  async findOne(id: number): Promise<User> {
    const user = await this.usersRepository.findOne(id);
    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }
    return user;
  }

  async create(createUserDto: CreateUserDto): Promise<User> {
    // 业务逻辑：密码加密等
    const hashedPassword = await this.hashPassword(createUserDto.password);
    return this.usersRepository.create({
      ...createUserDto,
      password: hashedPassword,
    });
  }

  async remove(id: number): Promise<void> {
    const user = await this.findOne(id);
    await this.usersRepository.delete(user.id);
  }

  private async hashPassword(password: string): Promise<string> {
    // 实际项目中使用bcrypt
    return `hashed_${password}`;
  }
}

// modules/users/users.controller.ts
import { 
  Controller, 
  Get, 
  Post, 
  Body, 
  Param, 
  Delete,
  ParseIntPipe 
} from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll() {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    return this.usersService.findOne(id);
  }

  @Post()
  create(@Body() createUserDto: CreateUserDto) {
    return this.usersService.create(createUserDto);
  }

  @Delete(':id')
  remove(@Param('id', ParseIntPipe) id: number) {
    return this.usersService.remove(id);
  }
}

// modules/users/users.module.ts
import { Module } from '@nestjs/common';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';
import { UsersRepository } from './users.repository';

@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],
})
export class UsersModule {}
```

---

## 架构解析

### 分层清晰
- **Controller层**：处理HTTP请求/响应
- **Service层**：业务逻辑
- **Repository层**：数据访问

### 符合SOLID原则
- **S**：每个类职责单一
- **O**：通过依赖注入扩展
- **D**：依赖抽象（接口）而非具体实现

### 优势
- 易于测试（每个层可以单独mock）
- 易于维护（修改不影响其他层）
- 易于扩展（新增功能只需添加模块）
