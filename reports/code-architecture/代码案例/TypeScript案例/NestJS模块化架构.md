# NestJS 模块化架构实战

## 项目结构
```
src/
├── main.ts                     # 入口
├── app.module.ts              # 根模块
├── config/
│   └── configuration.ts      # 配置
├── common/
│   ├── decorators/           # 装饰器
│   ├── filters/              # 异常过滤器
│   ├── guards/               # 守卫
│   └── interceptors/         # 拦截器
├── users/
│   ├── users.module.ts
│   ├── users.controller.ts   # 表现层
│   ├── users.service.ts      # 业务层
│   ├── users.repository.ts   # 数据层
│   ├── dto/                  # 数据传输对象
│   └── entities/
│       └── user.entity.ts
├── auth/
│   ├── auth.module.ts
│   ├── auth.controller.ts
│   ├── auth.service.ts
│   ├── strategies/
│   │   └── jwt.strategy.ts
│   └── guards/
│       └── jwt-auth.guard.ts
└── orders/
    └── ...
```

## 代码实现

### 数据实体（Entity）

```typescript
// users/entities/user.entity.ts
import { 
  Entity, 
  Column, 
  PrimaryGeneratedColumn, 
  CreateDateColumn, 
  UpdateDateColumn,
  OneToMany 
} from 'typeorm';
import { Order } from '../../orders/entities/order.entity';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ length: 100 })
  name: string;

  @Column({ unique: true })
  email: string;

  @Column()
  password: string; // 加密后的密码

  @Column({ nullable: true })
  phone: string;

  @Column({ default: false })
  isActive: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @OneToMany(() => Order, order => order.user)
  orders: Order[];
}
```

### DTO（数据传输对象）

```typescript
// users/dto/create-user.dto.ts
import { IsEmail, IsString, MinLength, IsOptional } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @MinLength(2)
  name: string;

  @IsEmail()
  email: string;

  @IsString()
  @MinLength(6)
  password: string;

  @IsOptional()
  @IsString()
  phone?: string;
}

// users/dto/update-user.dto.ts
import { PartialType } from '@nestjs/mapped-types';
import { CreateUserDto } from './create-user.dto';

export class UpdateUserDto extends PartialType(CreateUserDto) {}
```

### Repository（数据层）

```typescript
// users/users.repository.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UsersRepository {
  constructor(
    @InjectRepository(User)
    private readonly repo: Repository<User>,
  ) {}

  async findById(id: number): Promise<User | null> {
    return this.repo.findOne({ where: { id } });
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.repo.findOne({ where: { email } });
  }

  async findAll(skip = 0, take = 20): Promise<[User[], number]> {
    return this.repo.findAndCount({ skip, take });
  }

  async create(data: Partial<User>): Promise<User> {
    const user = this.repo.create(data);
    return this.repo.save(user);
  }

  async update(id: number, data: Partial<User>): Promise<User> {
    await this.repo.update(id, data);
    return this.findById(id);
  }

  async delete(id: number): Promise<void> {
    await this.repo.delete(id);
  }
}
```

### Service（业务层）

```typescript
// users/users.service.ts
import { Injectable, ConflictException, NotFoundException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { UsersRepository } from './users.repository';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './entities/user.entity';

@Injectable()
export class UsersService {
  constructor(private readonly usersRepository: UsersRepository) {}

  async create(createUserDto: CreateUserDto): Promise<User> {
    // 业务逻辑：检查邮箱唯一性
    const existing = await this.usersRepository.findByEmail(createUserDto.email);
    if (existing) {
      throw new ConflictException('邮箱已被注册');
    }

    // 业务逻辑：密码加密
    const hashedPassword = await bcrypt.hash(createUserDto.password, 10);
    
    const user = await this.usersRepository.create({
      ...createUserDto,
      password: hashedPassword,
    });

    return user;
  }

  async findById(id: number): Promise<User> {
    const user = await this.usersRepository.findById(id);
    if (!user) {
      throw new NotFoundException('用户不存在');
    }
    return user;
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.usersRepository.findByEmail(email);
  }

  async findAll(page = 1, limit = 20): Promise<{ data: User[]; total: number }> {
    const skip = (page - 1) * limit;
    const [data, total] = await this.usersRepository.findAll(skip, limit);
    return { data, total };
  }

  async update(id: number, updateUserDto: UpdateUserDto): Promise<User> {
    const user = await this.findById(id);

    // 业务逻辑：检查邮箱唯一性
    if (updateUserDto.email && updateUserDto.email !== user.email) {
      const existing = await this.usersRepository.findByEmail(updateUserDto.email);
      if (existing) {
        throw new ConflictException('邮箱已被注册');
      }
    }

    // 如果更新密码，需要重新加密
    if (updateUserDto.password) {
      updateUserDto.password = await bcrypt.hash(updateUserDto.password, 10);
    }

    return this.usersRepository.update(id, updateUserDto);
  }

  async delete(id: number): Promise<void> {
    await this.findById(id);
    await this.usersRepository.delete(id);
  }

  async validatePassword(plainPassword: string, hashedPassword: string): Promise<boolean> {
    return bcrypt.compare(plainPassword, hashedPassword);
  }
}
```

### Controller（表现层）

```typescript
// users/users.controller.ts
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  ParseIntPipe,
  DefaultValuePipe,
} from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  async create(@Body() createUserDto: CreateUserDto) {
    return this.usersService.create(createUserDto);
  }

  @Get()
  async findAll(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(20), ParseIntPipe) limit: number,
  ) {
    const result = await this.usersService.findAll(page, limit);
    return {
      data: result.data,
      meta: { total: result.total, page, limit },
    };
  }

  @Get(':id')
  async findOne(@Param('id', ParseIntPipe) id: number) {
    return this.usersService.findById(id);
  }

  @Put(':id')
  @UseGuards(JwtAuthGuard)
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() updateUserDto: UpdateUserDto,
  ) {
    return this.usersService.update(id, updateUserDto);
  }

  @Delete(':id')
  @UseGuards(JwtAuthGuard)
  async remove(@Param('id', ParseIntPipe) id: number) {
    await this.usersService.delete(id);
    return { message: '删除成功' };
  }
}
```

## NestJS 架构特点

```
┌─────────────────────────────────────────────────────┐
│                    Controller                        │
│  - 路由处理                                           │
│  - 请求验证                                           │
│  - 响应格式化                                         │
├─────────────────────────────────────────────────────┤
│                     Service                          │
│  - 业务逻辑                                           │
│  - 事务管理                                           │
│  - 业务规则                                           │
├─────────────────────────────────────────────────────┤
│                   Repository                         │
│  - 数据库操作                                         │
│  - CRUD                                             │
│  - 查询构建                                          │
├─────────────────────────────────────────────────────┤
│                    Entity                            │
│  - 数据模型                                           │
│  - 关系定义                                           │
│  - 字段映射                                           │
└─────────────────────────────────────────────────────┘

✅ NestJS 优势：
1. 装饰器语法清晰
2. 依赖注入内置
3. 模块化组织
4. 装饰器验证
5. 生态完善（TypeORM、Passport 等）
```

## 踩坑记录

### 坑 1：循环依赖
NestJS 模块默认是单例，如果 A 模块和 B 模块互相导入：
```
A → B → A → 报错：Circular dependency
```

**解决方案**：
```typescript
// 使用 forwardRef
@Module({
  imports: [forwardRef(() => BModule)],
})
export class AModule {}
```

### 坑 2：Repository 注入问题
```typescript
// ❌ 错误：在 Service 中直接注入 Repository
@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepo: Repository<User>,
  ) {}
}

// ✅ 正确：使用自定义 Repository 类
@Injectable()
export class UsersRepository {
  constructor(
    @InjectRepository(User)
    private readonly repo: Repository<User>,
  ) {}
}
```

### 坑 3：NestJS 生命周期
```
请求 → Middleware → Guard → Interceptor(Before) → Pipe 
→ Controller → Service → Repository → 
→ Service → Controller → Interceptor(After) → Filter → Client
```

理解生命周期，才能正确使用 `OnModuleInit`、`OnModuleDestroy`、`BeforeApplicationShutdown`。
