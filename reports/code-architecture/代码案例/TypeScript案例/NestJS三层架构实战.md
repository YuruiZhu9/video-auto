# TypeScript + NestJS 项目实战

## 目标
用 NestJS 实现用户管理系统，展示标准三层架构 + 依赖注入。

## 项目结构

```
user-nestjs/
├── src/
│   ├── main.ts
│   ├── app.module.ts
│   ├── users/
│   │   ├── users.module.ts
│   │   ├── users.controller.ts    # 表现层
│   │   ├── users.service.ts       # 业务层
│   │   ├── users.repository.ts    # 数据层
│   │   ├── user.entity.ts         # 数据模型
│   │   └── dto/
│   │       ├── create-user.dto.ts
│   │       └── update-user.dto.ts
│   └── database/
│       └── database.module.ts
└── package.json
```

---

## 1. 安装依赖

```bash
npm install @nestjs/core @nestjs/common @nestjs/platform-express reflect-metadata rxjs class-validator class-transformer typeorm sqlite3
npm install -D typescript @types/node ts-node
```

---

## 2. 数据模型

```typescript
// src/users/user.entity.ts
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column({ unique: true })
  email: string;

  @Column({ nullable: true })
  age: number;

  @Column({ default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
```

---

## 3. DTO（数据传输对象）

```typescript
// src/users/dto/create-user.dto.ts
import { IsString, IsEmail, IsOptional, IsInt, Min, Max } from 'class-validator';

export class CreateUserDto {
  @IsString()
  name: string;

  @IsEmail()
  email: string;

  @IsOptional()
  @IsInt()
  @Min(0)
  @Max(150)
  age?: number;
}

// src/users/dto/update-user.dto.ts
import { PartialType } from '@nestjs/mapped-types';
import { CreateUserDto } from './create-user.dto';

export class UpdateUserDto extends PartialType(CreateUserDto) {}
```

---

## 4. Repository（数据访问层）

```typescript
// src/users/users.repository.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './user.entity';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

@Injectable()
export class UsersRepository {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async findAll(): Promise<User[]> {
    return this.userRepository.find();
  }

  async findOne(id: number): Promise<User | null> {
    return this.userRepository.findOne({ where: { id } });
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.userRepository.findOne({ where: { email } });
  }

  async createUser(dto: CreateUserDto): Promise<User> {
    const user = this.userRepository.create(dto);
    return this.userRepository.save(user);
  }

  async updateUser(id: number, dto: UpdateUserDto): Promise<User> {
    await this.userRepository.update(id, dto);
    return this.findOne(id);
  }

  async deleteUser(id: number): Promise<void> {
    await this.userRepository.delete(id);
  }
}
```

---

## 5. Service（业务逻辑层）

```typescript
// src/users/users.service.ts
import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { UsersRepository } from './users.repository';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './user.entity';

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

  async create(dto: CreateUserDto): Promise<User> {
    // 检查邮箱是否已存在
    const existingUser = await this.usersRepository.findByEmail(dto.email);
    if (existingUser) {
      throw new ConflictException(`Email ${dto.email} already exists`);
    }
    return this.usersRepository.createUser(dto);
  }

  async update(id: number, dto: UpdateUserDto): Promise<User> {
    // 检查用户是否存在
    await this.findOne(id);
    
    // 检查邮箱是否被其他用户使用
    if (dto.email) {
      const existingUser = await this.usersRepository.findByEmail(dto.email);
      if (existingUser && existingUser.id !== id) {
        throw new ConflictException(`Email ${dto.email} already exists`);
      }
    }
    
    return this.usersRepository.updateUser(id, dto);
  }

  async remove(id: number): Promise<void> {
    // 检查用户是否存在
    await this.findOne(id);
    await this.usersRepository.deleteUser(id);
  }
}
```

---

## 6. Controller（表现层）

```typescript
// src/users/users.controller.ts
import { 
  Controller, 
  Get, 
  Post, 
  Body, 
  Patch, 
  Param, 
  Delete, 
  ParseIntPipe 
} from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

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

  @Patch(':id')
  update(
    @Param('id', ParseIntPipe) id: number,
    @Body() updateUserDto: UpdateUserDto,
  ) {
    return this.usersService.update(id, updateUserDto);
  }

  @Delete(':id')
  remove(@Param('id', ParseIntPipe) id: number) {
    return this.usersService.remove(id);
  }
}
```

---

## 7. Module 配置

```typescript
// src/users/users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';
import { UsersRepository } from './users.repository';
import { User } from './user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],
})
export class UsersModule {}

// src/app.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersModule } from './users/users.module';
import { User } from './users/user.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'sqlite',
      database: 'database.sqlite',
      entities: [User],
      synchronize: true, // 开发环境使用
    }),
    UsersModule,
  ],
})
export class AppModule {}
```

---

## 8. 入口文件

```typescript
// src/main.ts
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // 全局验证管道
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true, // 自动去除未定义的属性
    transform: true, // 自动转换类型
  }));
  
  await app.listen(3000);
  console.log('Application is running on: http://localhost:3000');
}

bootstrap();
```

---

## 架构说明

```
┌─────────────────────────────────────────────┐
│         Controller (表现层)                  │
│  @Get @Post @Patch @Delete                  │
│  接收请求、参数校验、调用Service             │
└────────────────────┬────────────────────────┘
                     │ 依赖注入
┌────────────────────▼────────────────────────┐
│         Service (业务层)                    │
│  业务逻辑处理、事务管理                       │
└────────────────────┬────────────────────────┘
                     │ 依赖注入
┌────────────────────▼────────────────────────┐
│         Repository (数据层)                │
│  数据访问、SQL操作                          │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│         TypeORM + SQLite                    │
│  数据库                                     │
└─────────────────────────────────────────────┘
```

---

## 运行方式

```bash
# 启动开发服务器
npm run start:dev

# 测试
curl http://localhost:3000/users
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "email": "zhangsan@example.com", "age": 25}'
```

---

## NestJS 优势

| 特性 | 优势 |
|------|------|
| 依赖注入 | 解耦、易测 |
| 模块化 | 代码组织清晰 |
| 装饰器 | 声明式路由 |
| 管道/守卫 | 统一处理校验、权限 |
| TypeORM | 完美的 ORM 集成 |
