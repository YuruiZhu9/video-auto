# TypeScript 代码架构案例

## 案例：NestJS 分层架构

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
│   │   ├── users.controller.ts
│   │   ├── users.service.ts
│   │   ├── users.repository.ts
│   │   └── users.module.ts
│   └── orders/
│       └── ...
└── shared/
    ├── constants/
    ├── utils/
    └── types/
```

### 代码实现

```typescript
// modules/users/entities/user.entity.ts
import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ length: 100 })
  name: string;

  @Column({ unique: true })
  email: string;

  @Column({ nullable: true })
  avatar: string;

  @Column({ default: 'active' })
  status: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

```typescript
// modules/users/dto/create-user.dto.ts
import { IsString, IsEmail, MinLength, IsOptional } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @MinLength(2, { message: '名字至少2个字符' })
  name: string;

  @IsEmail({}, { message: '邮箱格式不正确' })
  email: string;

  @IsOptional()
  @IsString()
  avatar?: string;
}
```

```typescript
// modules/users/users.repository.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

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

  async create(userData: Partial<User>): Promise<User> {
    const user = this.userRepository.create(userData);
    return this.userRepository.save(user);
  }

  async update(id: number, userData: Partial<User>): Promise<User> {
    await this.userRepository.update(id, userData);
    return this.findOne(id);
  }

  async remove(id: number): Promise<void> {
    await this.userRepository.delete(id);
  }
}
```

```typescript
// modules/users/users.service.ts
import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
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
      throw new NotFoundException(`用户ID ${id} 不存在`);
    }
    return user;
  }

  async create(createUserDto: CreateUserDto): Promise<User> {
    // 检查邮箱是否已存在
    const existingUser = await this.usersRepository.findByEmail(createUserDto.email);
    if (existingUser) {
      throw new ConflictException('邮箱已被使用');
    }
    
    return this.usersRepository.create(createUserDto);
  }

  async update(id: number, updateData: Partial<User>): Promise<User> {
    await this.findOne(id); // 先确保用户存在
    return this.usersRepository.update(id, updateData);
  }

  async remove(id: number): Promise<void> {
    await this.findOne(id); // 先确保用户存在
    await this.usersRepository.remove(id);
  }
}
```

```typescript
// modules/users/users.controller.ts
import { 
  Controller, Get, Post, Body, Patch, Param, Delete, ParseIntPipe 
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

  @Patch(':id')
  update(
    @Param('id', ParseIntPipe) id: number,
    @Body() updateData: any,
  ) {
    return this.usersService.update(id, updateData);
  }

  @Delete(':id')
  remove(@Param('id', ParseIntPipe) id: number) {
    return this.usersService.remove(id);
  }
}
```

```typescript
// modules/users/users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './entities/user.entity';
import { UsersService } from './users.service';
import { UsersRepository } from './users.repository';
import { UsersController } from './users.controller';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],
})
export class UsersModule {}
```

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersModule } from './modules/users/users.module';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'sqlite',
      database: 'db.sqlite',
      entities: [__dirname + '/**/*.entity{.ts,.js}'],
      synchronize: true, // 开发环境使用
    }),
    UsersModule,
  ],
})
export class AppModule {}
```

---

## NestJS 架构优势

| 层级 | 职责 | 组件 |
|------|------|------|
| **Controller** | 处理HTTP请求/响应 | UsersController |
| **Service** | 业务逻辑 | UsersService |
| **Repository** | 数据访问 | UsersRepository |
| **Entity** | 数据模型 | User Entity |

### 依赖注入示例

```
Controller → Service → Repository → TypeORM → Database
   ↓
Response
```

---

## 推荐：Clean Architecture

```
src/
├── domain/           # 领域层（核心业务规则）
│   ├── entities/
│   ├── repositories/  # 接口定义
│   └── services/     # 接口定义
├── application/      # 应用层（用例）
│   ├── dto/
│   └── use-cases/
├── infrastructure/   # 基础设施层
│   ├── repositories/ # 接口实现
│   └── services/     # 接口实现
└── presentation/     # 表现层
    ├── controllers/
    └── guards/
```

这种架构更适合大型项目，核心业务与框架解耦。
