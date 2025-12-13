# 学生信息管理系统 全栈架构文档

## 介绍

本文档概述了学生信息管理系统的完整全栈架构，包括后端系统、前端实现及其集成。它作为AI驱动开发的单一真实来源，确保整个技术栈的一致性。

这种统一的方法结合了传统上分离的后端和前端架构文档，简化了现代全栈应用程序的开发过程，因为这些应用程序的关注点日益交织在一起。

### 启动模板或现有项目
N/A - 全新项目

### 变更日志
| 日期 | 版本 | 描述 | 作者 |
|------|---------|-------------|---------|
| 2025-12-13 | 1.0 | 初始全栈架构创建 | Winston (架构师) |

## 高层架构

### 技术摘要
学生信息管理系统采用现代化的全栈架构，前后端分离设计。前端使用Vue 3 + TypeScript + Element Plus构建响应式用户界面，后端使用Flask + Python提供RESTful API服务。系统通过WebSocket实现实时通信，Redis作为缓存和消息队列，MySQL作为主数据库。整体架构支持水平扩展，可满足10,000+用户的并发访问需求。

### 平台和基础设施选择

**平台:** 自托管云服务器 (阿里云/腾讯云)
**关键服务:**
- Web服务器：Nginx (反向代理 + 静态文件服务)
- 应用服务器：Gunicorn + Flask
- 数据库：MySQL 8.0
- 缓存：Redis 6.2
- 消息队列：Redis + Celery
- 文件存储：MinIO (S3兼容)
- 监控：Prometheus + Grafana
**部署主机和区域:** 华东地区 (多可用区部署)

### 仓库结构

**结构:** Monorepo (单一代码仓库)
**Monorepo工具:** npm workspaces
**包组织:** 前后端分离，共享类型定义和配置

### 高层架构图

```mermaid
graph TD
    subgraph "用户层"
        U1[管理员]
        U2[教师]
        U3[学生]
    end

    subgraph "CDN层"
        CDN[CDN/静态资源]
    end

    subgraph "负载均衡层"
        LB[Nginx负载均衡]
    end

    subgraph "Web服务层"
        FE1[前端应用1]
        FE2[前端应用2]
    end

    subgraph "API网关层"
        GW[API Gateway]
    end

    subgraph "应用服务层"
        API1[Flask API 1]
        API2[Flask API 2]
        API3[Flask API 3]
        WS[WebSocket服务]
    end

    subgraph "任务队列层"
        CEL[Celery Worker]
        Q[Redis Queue]
    end

    subgraph "数据层"
        DB[(MySQL)]
        CACHE[(Redis)]
        FS[(MinIO)]
    end

    subgraph "外部服务"
        SMTP[邮件服务]
        MON[监控系统]
    end

    U1 --> CDN
    U2 --> CDN
    U3 --> CDN
    CDN --> LB
    LB --> FE1
    LB --> FE2
    FE1 --> GW
    FE2 --> GW
    GW --> API1
    GW --> API2
    GW --> API3
    GW --> WS
    API1 --> DB
    API2 --> DB
    API3 --> DB
    API1 --> CACHE
    API2 --> CACHE
    API3 --> CACHE
    CEL --> Q
    Q --> CEL
    API1 --> Q
    API2 --> Q
    API3 --> Q
    CEL --> SMTP
    API1 --> FS
    API2 --> FS
    API3 --> FS
    WS --> API1
    WS --> API2
    WS --> API3
    API1 --> MON
    API2 --> MON
    API3 --> MON
```

### 架构模式
- **单体应用架构:** 模块化单体设计，便于开发和部署
- **前后端分离:** RESTful API + WebSocket实时通信
- **组件化UI:** Vue 3组件化设计，提高代码复用性
- **仓库模式:** 抽象数据访问层，提高测试性
- **CQRS模式:** 读写分离，优化查询性能
- **事件驱动:** 基于消息队列的异步处理

## 技术栈

### 技术栈表
| 类别 | 技术 | 版本 | 用途 | 选择理由 |
|----------|------------|---------|---------|-----------|
| 前端语言 | TypeScript | 5.3+ | 类型安全的JavaScript | 提高代码质量和开发效率 |
| 前端框架 | Vue 3 | 3.4+ | 渐进式前端框架 | 学习成本低，生态成熟 |
| UI组件库 | Element Plus | 2.4+ | Vue组件库 | 丰富的企业级组件 |
| 状态管理 | Pinia | 2.1+ | Vue状态管理 | Vue官方推荐，TypeScript支持好 |
| 后端语言 | Python | 3.11+ | 服务端开发语言 | 开发效率高，生态丰富 |
| 后端框架 | Flask | 2.3+ | Python Web框架 | 轻量级，灵活性强 |
| API风格 | RESTful API | 3.0 | HTTP API规范 | 标准化，易于理解 |
| 数据库 | MySQL | 8.0+ | 关系型数据库 | 事务支持，性能稳定 |
| 缓存 | Redis | 6.2+ | 内存缓存 | 高性能，支持多种数据结构 |
| 文件存储 | MinIO | Latest | 对象存储 | S3兼容，开源免费 |
| 身份验证 | JWT | Latest | 身份验证 | 无状态，易于扩展 |
| 前端测试 | Vitest | 1.0+ | 单元测试框架 | 快速，支持TypeScript |
| 后端测试 | Pytest | 7.4+ | Python测试框架 | 功能强大，插件丰富 |
| E2E测试 | Playwright | 1.40+ | 端到端测试 | 跨浏览器支持 |
| 构建工具 | Vite | 5.0+ | 前端构建工具 | 快速热更新，优化好 |
| 打包器 | Rollup | 4.0+ | 模块打包器 | Tree-shaking好 |
| IaC工具 | Docker Compose | Latest | 容器编排 | 简化部署配置 |
| CI/CD | GitHub Actions | Latest | 持续集成 | 与代码仓库集成 |
| 监控 | Prometheus | Latest | 监控系统 | 时间序列数据 |
| 日志 | ELK Stack | Latest | 日志收集 | 集中化日志管理 |
| CSS框架 | Tailwind CSS | 3.3+ | 原子化CSS | 快速样式开发 |

## 数据模型

### 用户模型

**目的:** 统一用户模型，包含所有用户类型的基础信息

**关键属性:**
- id: UUID - 主键
- username: string - 用户名，唯一
- email: string - 邮箱地址，唯一
- password_hash: string - 密码哈希
- role: enum - 用户角色（admin, teacher, student）
- status: enum - 账户状态
- created_at: datetime - 创建时间
- updated_at: datetime - 更新时间

#### TypeScript接口
```typescript
interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'teacher' | 'student';
  status: 'active' | 'inactive' | 'suspended';
  profile: UserProfile;
  createdAt: Date;
  updatedAt: Date;
}

interface UserProfile {
  firstName: string;
  lastName: string;
  avatar?: string;
  phone?: string;
  department?: string;
}
```

#### 关系
- 与Admin、Teacher或Student一对一关系（基于role）
- 与Message一对多关系（发送/接收）
- 与AuditLog一对多关系

### 学生模型

**目的:** 存储学生详细信息

**关键属性:**
- id: UUID - 主键
- user_id: UUID - 关联用户表
- student_id: string - 学号，唯一
- grade: string - 年级
- class: string - 班级
- major: string - 专业
- enrollment_date: date - 入学日期

#### TypeScript接口
```typescript
interface Student {
  id: string;
  userId: string;
  studentId: string;
  grade: string;
  class: string;
  major: string;
  enrollmentDate: Date;
  user: User;
  enrollments: Enrollment[];
  grades: Grade[];
}
```

#### 关系
- 多对一User关系
- 多对多Course关系（通过Enrollment）
- 一对多Grade关系

### 课程模型

**目的:** 课程信息管理

**关键属性:**
- id: UUID - 主键
- course_code: string - 课程编号，唯一
- name: string - 课程名称
- description: text - 课程描述
- credits: number - 学分
- teacher_id: UUID - 授课教师ID

#### TypeScript接口
```typescript
interface Course {
  id: string;
  courseCode: string;
  name: string;
  description: string;
  credits: number;
  teacherId: string;
  teacher: Teacher;
  enrollments: Enrollment[];
  grades: Grade[];
}
```

#### 关系
- 多对一Teacher关系
- 多对多Student关系（通过Enrollment）
- 一对多Grade关系

### 成绩模型

**目的:** 学生成绩记录

**关键属性:**
- id: UUID - 主键
- student_id: UUID - 学生ID
- course_id: UUID - 课程ID
- score: number - 成绩
- semester: string - 学期
- exam_type: enum - 考试类型
- graded_by: UUID - 评分教师ID

#### TypeScript接口
```typescript
interface Grade {
  id: string;
  studentId: string;
  courseId: string;
  score: number;
  semester: string;
  examType: 'midterm' | 'final' | 'quiz' | 'assignment';
  gradedBy: string;
  gradedAt: Date;
  student: Student;
  course: Course;
  grader: Teacher;
}
```

#### 关系
- 多对一Student关系
- 多对一Course关系
- 多对一Teacher关系（评分人）

### 消息模型

**目的:** 系统消息管理

**关键属性:**
- id: UUID - 主键
- sender_id: UUID - 发送者ID
- receiver_id: UUID - 接收者ID
- title: string - 消息标题
- content: text - 消息内容
- type: enum - 消息类型
- status: enum - 阅读状态

#### TypeScript接口
```typescript
interface Message {
  id: string;
  senderId: string;
  receiverId: string;
  title: string;
  content: string;
  type: 'system' | 'business' | 'personal';
  status: 'unread' | 'read';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  sentAt: Date;
  readAt?: Date;
  sender: User;
  receiver: User;
}
```

#### 关系
- 多对一User关系（发送者）
- 多对一User关系（接收者）

## API规范

### REST API规范
```yaml
openapi: 3.0.0
info:
  title: 学生信息管理系统 API
  version: 1.0.0
  description: 学生信息管理系统RESTful API
servers:
  - url: https://api.example.com/v1
    description: 生产服务器
  - url: http://localhost:5000/v1
    description: 开发服务器

components:
  securitySchemes:
    JWT:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        username:
          type: string
        email:
          type: string
          format: email
        role:
          type: string
          enum: [admin, teacher, student]
        status:
          type: string
          enum: [active, inactive, suspended]

    Student:
      type: object
      properties:
        id:
          type: string
          format: uuid
        studentId:
          type: string
        grade:
          type: string
        class:
          type: string
        major:
          type: string
        enrollmentDate:
          type: string
          format: date

    Course:
      type: object
      properties:
        id:
          type: string
          format: uuid
        courseCode:
          type: string
        name:
          type: string
        description:
          type: string
        credits:
          type: number
          minimum: 0
          maximum: 10

    Grade:
      type: object
      properties:
        id:
          type: string
          format: uuid
        score:
          type: number
          minimum: 0
          maximum: 100
        semester:
          type: string
        examType:
          type: string
          enum: [midterm, final, quiz, assignment]

    Message:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        content:
          type: string
        type:
          type: string
          enum: [system, business, personal]
        status:
          type: string
          enum: [unread, read]
        priority:
          type: string
          enum: [low, normal, high, urgent]

paths:
  /auth/login:
    post:
      summary: 用户登录
      tags:
        - Authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
              required:
                - username
                - password
      responses:
        '200':
          description: 登录成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                  user:
                    $ref: '#/components/schemas/User'
        '401':
          description: 认证失败

  /students:
    get:
      summary: 获取学生列表
      tags:
        - Students
      security:
        - JWT: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: search
          in: query
          schema:
            type: string
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Student'
                  total:
                    type: integer
                  page:
                    type: integer
                  limit:
                    type: integer

    post:
      summary: 创建学生
      tags:
        - Students
      security:
        - JWT: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Student'
      responses:
        '201':
          description: 创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Student'

  /students/{id}:
    get:
      summary: 获取学生详情
      tags:
        - Students
      security:
        - JWT: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Student'

    put:
      summary: 更新学生信息
      tags:
        - Students
      security:
        - JWT: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Student'
      responses:
        '200':
          description: 更新成功

    delete:
      summary: 删除学生
      tags:
        - Students
      security:
        - JWT: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: 删除成功

  /courses:
    get:
      summary: 获取课程列表
      tags:
        - Courses
      security:
        - JWT: []
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Course'

    post:
      summary: 创建课程
      tags:
        - Courses
      security:
        - JWT: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Course'
      responses:
        '201':
          description: 创建成功

  /courses/{id}/students:
    get:
      summary: 获取课程学生列表
      tags:
        - Courses
      security:
        - JWT: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 成功

  /grades:
    get:
      summary: 获取成绩列表
      tags:
        - Grades
      security:
        - JWT: []
      parameters:
        - name: studentId
          in: query
          schema:
            type: string
            format: uuid
        - name: courseId
          in: query
          schema:
            type: string
            format: uuid
        - name: semester
          in: query
          schema:
            type: string
      responses:
        '200':
          description: 成功

    post:
      summary: 录入成绩
      tags:
        - Grades
      security:
        - JWT: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  studentId:
                    type: string
                    format: uuid
                  courseId:
                    type: string
                    format: uuid
                  score:
                    type: number
                    minimum: 0
                    maximum: 100
                  semester:
                    type: string
                  examType:
                    type: string
                    enum: [midterm, final, quiz, assignment]
      responses:
        '201':
          description: 录入成功

  /messages:
    get:
      summary: 获取消息列表
      tags:
        - Messages
      security:
        - JWT: []
      parameters:
        - name: type
          in: query
          schema:
            type: string
            enum: [system, business, personal]
        - name: status
          in: query
          schema:
            type: string
            enum: [unread, read]
      responses:
        '200':
          description: 成功

    post:
      summary: 发送消息
      tags:
        - Messages
      security:
        - JWT: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Message'
      responses:
        '201':
          description: 发送成功

  /messages/{id}/read:
    put:
      summary: 标记消息已读
      tags:
        - Messages
      security:
        - JWT: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 更新成功
```

## 组件

### API网关组件

**职责:** 统一API入口，处理认证、限流、路由

**关键接口:**
- JWT认证中间件
- 请求限流器
- CORS处理
- 错误处理

**依赖:** Redis（限流计数）、JWT库

**技术栈:** Nginx + Flask middleware

### 认证服务

**职责:** 用户认证和授权管理

**关键接口:**
- 登录/注册接口
- JWT令牌生成和验证
- 权限检查装饰器
- 密码重置流程

**依赖:** MySQL（用户数据）、Redis（会话）

**技术栈:** Flask + Flask-JWT-Extended

### 学生服务

**职责:** 学生信息管理

**关键接口:**
- 学生CRUD操作
- 批量导入导出
- 学生信息查询
- 数据验证

**依赖:** MySQL数据库、文件存储

**技术栈:** Flask + SQLAlchemy

### 课程服务

**职责:** 课程管理

**关键接口:**
- 课程CRUD操作
- 选课管理
- 课程查询
- 教师分配

**依赖:** MySQL数据库

**技术栈:** Flask + SQLAlchemy

### 成绩服务

**职责:** 成绩管理

**关键接口:**
- 成绩录入
- 成绩查询
- 成绩统计
- 批量处理

**依赖:** MySQL数据库、消息队列

**技术栈:** Flask + SQLAlchemy + Celery

### 通知服务

**职责:** 消息通知

**关键接口:**
- 消息发送
- 实时推送
- 邮件发送
- 消息模板

**依赖:** Redis（WebSocket）、SMTP服务

**技术栈:** Flask-SocketIO + Celery

### 文件存储服务

**职责:** 文件管理

**关键接口:**
- 文件上传下载
- 图片处理
- Excel导入导出
- 文件权限控制

**依赖:** MinIO存储

**技术栈:** MinIO Python SDK

### 组件图

```mermaid
graph TD
    subgraph "前端层"
        UI[Vue 3 应用]
        WS_CLIENT[WebSocket客户端]
    end

    subgraph "API网关"
        GATEWAY[Nginx + 路由]
        AUTH_MW[认证中间件]
        RATE_MW[限流中间件]
    end

    subgraph "服务层"
        AUTH_SVC[认证服务]
        STUDENT_SVC[学生服务]
        COURSE_SVC[课程服务]
        GRADE_SVC[成绩服务]
        NOTIFY_SVC[通知服务]
        FILE_SVC[文件服务]
    end

    subgraph "数据层"
        DB[(MySQL)]
        REDIS[(Redis)]
        MINIO[(MinIO)]
    end

    UI --> GATEWAY
    WS_CLIENT --> NOTIFY_SVC
    GATEWAY --> AUTH_MW
    AUTH_MW --> RATE_MW
    RATE_MW --> AUTH_SVC
    RATE_MW --> STUDENT_SVC
    RATE_MW --> COURSE_SVC
    RATE_MW --> GRADE_SVC
    RATE_MW --> FILE_SVC

    AUTH_SVC --> DB
    STUDENT_SVC --> DB
    COURSE_SVC --> DB
    GRADE_SVC --> DB

    AUTH_SVC --> REDIS
    NOTIFY_SVC --> REDIS

    FILE_SVC --> MINIO
    STUDENT_SVC --> MINIO
```

## 核心工作流

### 用户认证流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant G as API网关
    participant A as 认证服务
    participant D as 数据库

    U->>F: 输入用户名密码
    F->>G: POST /auth/login
    G->>G: 验证JWT Token (可选)
    G->>A: 转发登录请求
    A->>D: 查询用户信息
    D-->>A: 返回用户数据
    A->>A: 验证密码
    A->>A: 生成JWT Token
    A-->>G: 返回Token和用户信息
    G-->>F: 返回响应
    F->>F: 存储Token
    F-->>U: 跳转到仪表板
```

### 学生批量导入流程

```mermaid
sequenceDiagram
    participant A as 管理员
    participant F as 前端
    participant S as 学生服务
    participant Q as 消息队列
    participant W as 后台任务
    participant DB as 数据库

    A->>F: 上传Excel文件
    F->>S: POST /api/students/import
    S->>S: 验证文件格式
    S->>Q: 添加导入任务到队列
    S-->>F: 返回任务ID
    F->>F: 显示处理进度

    Q->>W: 消费导入任务
    W->>W: 解析Excel文件
    W->>W: 验证数据格式
    W->>DB: 批量插入数据
    DB-->>W: 返回结果
    W->>Q: 发送完成通知
    Q->>S: WebSocket推送更新
    S->>F: 实时推送状态
    F-->>A: 显示导入完成
```

### 实时消息推送流程

```mermaid
sequenceDiagram
    participant S as 发送者
    participant F as 前端
    participant API as 后端API
    participant WS as WebSocket服务
    participant R as 接收者
    participant R_F as 接收者前端

    S->>F: 撰写消息
    F->>API: POST /api/messages
    API->>API: 保存消息到数据库
    API->>WS: 触发消息推送
    WS->>WS: 查询接收者连接
    WS->>R_F: WebSocket推送消息
    R_F->>R_F: 显示新消息通知
    R_F->>R: 展示消息内容

    Note over WS: 如果接收者不在线
    WS->>API: 标记为未推送
    API->>API: 发送邮件通知
```

## 数据库架构

### MySQL Schema

```sql
-- 用户表
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- 用户资料表
CREATE TABLE user_profiles (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    avatar VARCHAR(255),
    phone VARCHAR(20),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_id (user_id)
);

-- 学生表
CREATE TABLE students (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    grade VARCHAR(10),
    class VARCHAR(10),
    major VARCHAR(100),
    enrollment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_grade_class (grade, class)
);

-- 教师表
CREATE TABLE teachers (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    teacher_id VARCHAR(20) UNIQUE,
    title VARCHAR(50),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_teacher_id (teacher_id)
);

-- 管理员表
CREATE TABLE admins (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 课程表
CREATE TABLE courses (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    course_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    credits DECIMAL(3,1) DEFAULT 0,
    teacher_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_course_code (course_code),
    INDEX idx_teacher_id (teacher_id)
);

-- 选课表
CREATE TABLE enrollments (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    student_id CHAR(36) NOT NULL,
    course_id CHAR(36) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_course_semester (student_id, course_id, semester),
    INDEX idx_student_id (student_id),
    INDEX idx_course_id (course_id)
);

-- 成绩表
CREATE TABLE grades (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    student_id CHAR(36) NOT NULL,
    course_id CHAR(36) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    exam_type ENUM('midterm', 'final', 'quiz', 'assignment') NOT NULL,
    graded_by CHAR(36) NOT NULL,
    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student_course (student_id, course_id),
    INDEX idx_semester (semester)
);

-- 消息表
CREATE TABLE messages (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    sender_id CHAR(36) NOT NULL,
    receiver_id CHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    type ENUM('system', 'business', 'personal') NOT NULL,
    status ENUM('unread', 'read') DEFAULT 'unread',
    priority ENUM('low', 'normal', 'high', 'urgent') DEFAULT 'normal',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_receiver_status (receiver_id, status),
    INDEX idx_sent_at (sent_at)
);

-- 消息模板表
CREATE TABLE message_templates (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(100) NOT NULL,
    title_template VARCHAR(200) NOT NULL,
    content_template TEXT NOT NULL,
    type ENUM('system', 'business', 'personal') NOT NULL,
    variables JSON,
    created_by CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_type (type)
);

-- 操作日志表
CREATE TABLE audit_logs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id CHAR(36),
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_action (user_id, action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created_at (created_at)
);

-- 系统配置表
CREATE TABLE system_configs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_key (key)
);
```

## 前端架构

### 组件架构

#### 组件组织

```
src/
├── components/          # 通用组件
│   ├── common/         # 基础组件
│   │   ├── AppHeader.vue
│   │   ├── AppFooter.vue
│   │   ├── LoadingSpinner.vue
│   │   └── EmptyState.vue
│   ├── forms/          # 表单组件
│   │   ├── BaseForm.vue
│   │   ├── StudentForm.vue
│   │   └── CourseForm.vue
│   └── tables/         # 表格组件
│       ├── DataTable.vue
│       ├── StudentTable.vue
│       └── GradeTable.vue
├── layouts/            # 布局组件
│   ├── DefaultLayout.vue
│   ├── AuthLayout.vue
│   └── AdminLayout.vue
├── pages/              # 页面组件
│   ├── auth/
│   ├── students/
│   ├── courses/
│   ├── grades/
│   └── messages/
├── composables/        # 组合式函数
│   ├── useAuth.js
│   ├── useApi.js
│   └── useWebSocket.js
├── stores/             # Pinia stores
│   ├── auth.js
│   ├── students.js
│   ├── courses.js
│   └── messages.js
├── services/           # API服务
│   ├── api.js
│   ├── auth.js
│   └── websocket.js
├── utils/              # 工具函数
│   ├── request.js
│   ├── format.js
│   └── validation.js
├── router/             # 路由配置
│   ├── index.js
│   └── guards.js
├── assets/             # 静态资源
│   ├── images/
│   ├── icons/
│   └── styles/
└── types/              # TypeScript类型
    ├── api.ts
    ├── user.ts
    └── common.ts
```

#### 组件模板

```vue
<template>
  <div class="student-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      @submit.prevent="handleSubmit"
    >
      <el-form-item label="学号" prop="studentId">
        <el-input
          v-model="formData.studentId"
          placeholder="请输入学号"
          :disabled="isEdit"
        />
      </el-form-item>

      <el-form-item label="姓名" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入姓名"
        />
      </el-form-item>

      <el-form-item label="年级" prop="grade">
        <el-select
          v-model="formData.grade"
          placeholder="请选择年级"
          style="width: 100%"
        >
          <el-option
            v-for="grade in gradeOptions"
            :key="grade.value"
            :label="grade.label"
            :value="grade.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="班级" prop="class">
        <el-input
          v-model="formData.class"
          placeholder="请输入班级"
        />
      </el-form-item>

      <el-form-item label="专业" prop="major">
        <el-input
          v-model="formData.major"
          placeholder="请输入专业"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useStudentStore } from '@/stores/student'
import type { StudentFormData } from '@/types/student'

interface Props {
  studentId?: string
}

const props = withDefaults(defineProps<Props>(), {
  studentId: undefined
})

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const studentStore = useStudentStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const isEdit = computed(() => !!props.studentId)

const formData = reactive<StudentFormData>({
  studentId: '',
  name: '',
  grade: '',
  class: '',
  major: '',
  enrollmentDate: ''
})

const formRules: FormRules<StudentFormData> = {
  studentId: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^\d{10}$/, message: '学号必须为10位数字', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度为2-20个字符', trigger: 'blur' }
  ],
  grade: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ],
  class: [
    { required: true, message: '请输入班级', trigger: 'blur' }
  ],
  major: [
    { required: true, message: '请输入专业', trigger: 'blur' }
  ]
}

const gradeOptions = [
  { label: '2021级', value: '2021' },
  { label: '2022级', value: '2022' },
  { label: '2023级', value: '2023' },
  { label: '2024级', value: '2024' }
]

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    if (isEdit.value) {
      await studentStore.updateStudent(props.studentId!, formData)
      ElMessage.success('学生信息更新成功')
    } else {
      await studentStore.createStudent(formData)
      ElMessage.success('学生创建成功')
    }

    emit('success')
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
}

onMounted(async () => {
  if (isEdit.value && props.studentId) {
    const student = await studentStore.getStudent(props.studentId)
    if (student) {
      Object.assign(formData, student)
    }
  }
})
</script>

<style scoped>
.student-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>
```

### 状态管理架构

#### 状态结构

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const permissions = ref<string[]>([])

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')

  const login = async (credentials: LoginCredentials) => {
    const response = await authService.login(credentials)
    token.value = response.token
    user.value = response.user
    permissions.value = response.permissions || []

    // 保存到localStorage
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  const logout = () => {
    token.value = null
    user.value = null
    permissions.value = []

    // 清除localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')

    // 跳转到登录页
    router.push('/login')
  }

  const refreshToken = async () => {
    try {
      const response = await authService.refreshToken()
      token.value = response.token
      localStorage.setItem('token', response.token)
    } catch (error) {
      logout()
    }
  }

  return {
    user: readonly(user),
    token: readonly(token),
    permissions: readonly(permissions),
    isAuthenticated,
    isAdmin,
    isTeacher,
    isStudent,
    login,
    logout,
    refreshToken
  }
})
```

### 路由架构

#### 路由组织

```
src/router/
├── index.ts            # 路由主文件
├── modules/            # 路由模块
│   ├── auth.ts        # 认证相关路由
│   ├── students.ts    # 学生管理路由
│   ├── courses.ts     # 课程管理路由
│   ├── grades.ts      # 成绩管理路由
│   └── messages.ts    # 消息中心路由
└── guards.ts          # 路由守卫
```

#### 受保护路由模式

```typescript
// router/guards.ts
import { useAuthStore } from '@/stores/auth'
import type { RouteLocationNormalized } from 'vue-router'

export const requireAuth = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: any
) => {
  const authStore = useAuthStore()

  if (!authStore.isAuthenticated) {
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
}

export const requireRole = (roles: string[]) => {
  return (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: any
  ) => {
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
    } else if (!roles.includes(authStore.user?.role || '')) {
      next({ name: '403' })
    } else {
      next()
    }
  }
}
```

### 前端服务层

#### API客户端设置

```typescript
// services/api.ts
import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse
} from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response.data
      },
      (error) => {
        const { response } = error

        if (response) {
          switch (response.status) {
            case 401:
              const authStore = useAuthStore()
              authStore.logout()
              router.push('/login')
              ElMessage.error('登录已过期，请重新登录')
              break
            case 403:
              ElMessage.error('没有权限访问该资源')
              router.push('/403')
              break
            case 404:
              ElMessage.error('请求的资源不存在')
              break
            case 500:
              ElMessage.error('服务器内部错误')
              break
            default:
              ElMessage.error(response.data?.message || '请求失败')
          }
        } else {
          ElMessage.error('网络连接失败')
        }

        return Promise.reject(error)
      }
    )
  }

  public get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.instance.get(url, config)
  }

  public post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.instance.post(url, data, config)
  }

  public put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.instance.put(url, data, config)
  }

  public delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.instance.delete(url, config)
  }
}

export const apiClient = new ApiClient()
```

## 后端架构

### 服务架构

#### 控制器/路由组织

```
backend/
├── app/
│   ├── __init__.py
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── course.py
│   │   ├── grade.py
│   │   └── message.py
│   ├── api/                # API蓝图
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── courses.py
│   │   ├── grades.py
│   │   ├── messages.py
│   │   └── uploads.py
│   ├── services/           # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── student_service.py
│   │   ├── course_service.py
│   │   ├── grade_service.py
│   │   ├── notification_service.py
│   │   └── file_service.py
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── exceptions.py
│   └── extensions.py       # Flask扩展初始化
├── migrations/             # 数据库迁移
├── tests/                  # 测试文件
├── config/                 # 配置文件
├── requirements.txt
└── run.py                  # 应用入口
```

#### 控制器模板

```python
# app/api/students.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.models.user import User
from app.models.student import Student
from app.services.student_service import StudentService
from app.utils.decorators import require_role
from app.utils.validators import validate_student_data
from app.utils.exceptions import APIError
from app import db

bp = Blueprint('students', __name__, url_prefix='/students')
student_service = StudentService()

@bp.route('', methods=['GET'])
@jwt_required()
@require_role(['admin', 'teacher'])
def get_students():
    """获取学生列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('limit', 20, type=int), 100)
        search = request.args.get('search', '')
        grade = request.args.get('grade')
        class_name = request.args.get('class')

        # 构建查询参数
        filters = {}
        if search:
            filters['search'] = search
        if grade:
            filters['grade'] = grade
        if class_name:
            filters['class'] = class_name

        # 调用服务层
        result = student_service.get_students(
            page=page,
            per_page=per_page,
            filters=filters
        )

        return jsonify({
            'data': result['items'],
            'total': result['total'],
            'page': page,
            'limit': per_page,
            'pages': result['pages']
        })

    except Exception as e:
        current_app.logger.error(f"获取学生列表失败: {str(e)}")
        raise APIError('获取学生列表失败', 500)
```

### 数据库架构

#### 模式设计

```sql
-- 已在前面定义了完整的数据库schema
```

#### 数据访问层

```python
# app/models/base.py
from datetime import datetime
from app import db
import uuid

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

# app/repositories/student_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_
from app.models.student import Student
from app.models.user import User
from app import db

class StudentRepository:

    def get_by_id(self, student_id: str) -> Optional[Student]:
        """通过ID获取学生"""
        return Student.query.filter_by(id=student_id).first()

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """获取学生列表"""
        query = Student.query.join(User)

        # 应用过滤器
        if filters:
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Student.student_id.like(search_term),
                        User.username.like(search_term),
                        User.email.like(search_term)
                    )
                )

        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'items': [student.to_dict() for student in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page
        }
```

### 认证和授权

#### 认证流程

```mermaid
sequenceDiagram
    participant C as Client
    participant G as API Gateway
    participant A as Auth Service
    participant DB as Database
    participant R as Redis

    C->>G: POST /auth/login
    G->>A: 验证凭据
    A->>DB: 查询用户
    DB-->>A: 返回用户信息
    A->>A: 验证密码
    A->>A: 生成JWT Token
    A->>R: 存储会话信息
    A-->>G: 返回Token
    G-->>C: 响应认证成功

    Note over C: 后续请求

    C->>G: API请求 + JWT Token
    G->>G: 验证Token
    G->>R: 检查Token有效性
    R-->>G: 返回用户信息
    G->>G: 验证权限
    G->>G: 转发请求
```

#### 中间件/守卫

```python
# app/utils/decorators.py
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.user import User

def require_role(allowed_roles):
    """检查用户角色装饰器"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user or user.role not in allowed_roles:
                return jsonify({'error': '权限不足'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## 统一项目结构

```
student-management-system/
├── .github/                     # GitHub工作流
│   └── workflows/
│       ├── ci.yml               # 持续集成
│       └── deploy.yml           # 部署流程
├── apps/                        # 应用程序包
│   ├── web/                     # 前端应用
│   │   ├── src/
│   │   │   ├── components/      # UI组件
│   │   │   ├── pages/           # 页面组件/路由
│   │   │   ├── composables/     # Vue组合式函数
│   │   │   ├── services/        # API客户端服务
│   │   │   ├── stores/          # Pinia状态管理
│   │   │   ├── styles/          # 全局样式/主题
│   │   │   ├── utils/           # 前端工具
│   │   │   └── types/           # TypeScript接口
│   │   ├── public/              # 静态资源
│   │   ├── tests/               # 前端测试
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   └── api/                     # 后端应用
│       ├── app/
│       │   ├── models/          # 数据模型
│       │   ├── api/             # API路由
│       │   ├── services/        # 业务逻辑
│       │   ├── repositories/    # 数据访问层
│       │   ├── utils/           # 后端工具
│       │   └── extensions.py    # Flask扩展
│       ├── migrations/          # 数据库迁移
│       ├── tests/               # 后端测试
│       ├── requirements.txt
│       └── run.py
├── packages/                    # 共享包
│   ├── shared/                  # 共享类型/工具
│   │   ├── src/
│   │   │   ├── types/           # TypeScript接口
│   │   │   ├── constants/       # 共享常量
│   │   │   └── utils/           # 共享工具
│   │   └── package.json
│   ├── ui/                      # 共享UI组件
│   │   ├── src/
│   │   └── package.json
│   └── config/                  # 共享配置
│       ├── eslint/
│       ├── typescript/
│       └── jest/
├── infrastructure/              # 基础设施
│   ├── docker/
│   │   ├── Dockerfile.web
│   │   ├── Dockerfile.api
│   │   └── docker-compose.yml
│   ├── nginx/
│   │   └── nginx.conf
│   └── kubernetes/              # K8s配置
├── scripts/                     # 构建/部署脚本
│   ├── build.sh
│   ├── deploy.sh
│   └── backup.sh
├── docs/                        # 文档
│   ├── prd.md
│   ├── front-end-spec.md
│   ├── architecture.md
│   └── api.md
├── .env.example                 # 环境变量模板
├── docker-compose.yml           # 开发环境
├── docker-compose.prod.yml       # 生产环境
├── package.json                 # 根package.json
├── pnpm-workspace.yaml          # pnpm工作区配置
└── README.md
```

## 开发工作流

### 本地开发设置

#### 先决条件
```bash
# 安装Node.js (v18+)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装Python (3.11+)
sudo apt-get update
sudo apt-get install python3.11 python3.11-pip python3.11-venv

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 初始设置
```bash
# 克隆仓库
git clone https://github.com/your-org/student-management-system.git
cd student-management-system

# 安装pnpm
npm install -g pnpm

# 安装依赖
pnpm install

# 设置环境变量
cp .env.example .env

# 启动开发环境
docker-compose up -d mysql redis minio

# 初始化数据库
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade

# 启动后端
python run.py

# 新终端：启动前端
cd apps/web
pnpm dev
```

#### 开发命令
```bash
# 启动所有服务
pnpm run dev

# 启动前端
pnpm run dev:web

# 启动后端
pnpm run dev:api

# 运行测试
pnpm run test

# 代码检查
pnpm run lint

# 类型检查
pnpm run type-check
```

### 环境配置

#### 必需的环境变量

```bash
# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_WS_URL=ws://localhost:5000
VITE_UPLOAD_URL=http://localhost:9000
VITE_APP_NAME=学生信息管理系统

# Backend (.env)
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/student_management
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=jwt-secret-key
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=student-management
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Shared
NODE_ENV=development
```

## 部署架构

### 部署策略

**前端部署:**
- **平台:** Nginx + Docker
- **构建命令:** `pnpm build`
- **输出目录:** `dist`
- **CDN/Edge:** Nginx静态资源服务

**后端部署:**
- **平台:** Docker + Gunicorn
- **构建命令:** 无需构建（Python源码）
- **部署方法:** Docker Compose

### CI/CD流水线
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'pnpm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pnpm install
          cd apps/api && pip install -r requirements.txt

      - name: Run linting
        run: |
          pnpm run lint
          cd apps/api && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Run tests
        run: |
          pnpm run test
          cd apps/api && pytest --cov=. tests/

      - name: Build frontend
        run: |
          cd apps/web
          pnpm build

      - name: Build Docker image
        run: |
          docker build -t student-management-system ./apps/api

      - name: Run E2E tests
        run: |
          pnpm run test:e2e

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/student-management-system
            git pull origin main
            docker-compose down
            docker-compose -f docker-compose.prod.yml up -d --build
            docker system prune -f
```

### 环境
| 环境 | 前端URL | 后端URL | 目的 |
|-------------|--------------|-------------|---------|
| 开发环境 | http://localhost:3000 | http://localhost:5000 | 本地开发 |
| 测试环境 | https://staging.example.com | https://staging-api.example.com | 生产前测试 |
| 生产环境 | https://example.com | https://api.example.com | 实时环境 |

## 安全和性能

### 安全要求

**前端安全:**
- CSP头部: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
- XSS防护: Vue.js内置XSS保护 + DOMPurify
- 安全存储: 敏感数据使用sessionStorage，token使用httpOnly cookie

**后端安全:**
- 输入验证: Pydantic模型验证 + 自定义验证器
- 速率限制: Flask-Limiter（每IP 100请求/分钟）
- CORS策略: Flask-CORS，仅允许信任的域名

**认证安全:**
- Token存储: JWT存储在Redis，设置合理过期时间
- 会话管理: Redis会话存储，支持强制下线
- 密码策略: 最少8位，包含大小写字母、数字和特殊字符

### 性能优化

**前端性能:**
- 包大小目标: < 2MB (gzipped)
- 加载策略: 代码分割 + 懒加载
- 缓存策略: 浏览器缓存 + Service Worker

**后端性能:**
- 响应时间目标: < 200ms (P95)
- 数据库优化: 索引优化 + 查询优化
- 缓存策略: Redis缓存热点数据

## 测试策略

### 测试金字塔

```
    E2E测试
    /        \
  集成测试
  /            \
前端单元测试  后端单元测试
```

### 测试组织

#### 前端测试
```
apps/web/tests/
├── unit/                 # 单元测试
│   ├── components/      # 组件测试
│   ├── composables/     # 组合函数测试
│   └── utils/           # 工具函数测试
├── integration/         # 集成测试
│   ├── api/            # API集成测试
│   └── stores/         # Store测试
└── e2e/                # 端到端测试
    ├── auth/           # 认证流程
    ├── students/       # 学生管理
    └── courses/        # 课程管理
```

#### 后端测试
```
apps/api/tests/
├── unit/               # 单元测试
│   ├── models/        # 模型测试
│   ├── services/      # 服务测试
│   └── utils/         # 工具测试
├── integration/       # 集成测试
│   ├── api/          # API测试
│   └── database/     # 数据库测试
└── fixtures/          # 测试数据
```

## 编码标准

### 关键的全栈规则
- **类型共享:** 始终在packages/shared中定义类型并从中导入
- **API调用:** 绝不直接HTTP调用 - 使用服务层
- **环境变量:** 仅通过配置对象访问，绝不直接使用process.env
- **错误处理:** 所有API路由必须使用标准错误处理程序
- **状态更新:** 绝不直接改变状态 - 使用适当的状态管理模式
- **数据库事务:** 始终对多表操作使用事务
- **密码安全:** 绝不以任何形式记录或暴露密码
- **输入验证:** 在客户端和服务端验证所有输入

### 命名约定
| 元素 | 前端 | 后端 | 示例 |
|---------|----------|---------|---------|
| 组件 | PascalCase | - | `UserProfile.vue` |
| Hook | camelCase with 'use' | - | `useAuth.ts` |
| API路由 | - | kebab-case | `/api/user-profile` |
| 数据库表 | - | snake_case | `user_profiles` |
| 函数 | camelCase | snake_case | `getUserData()` / `get_user_data()` |
| 常量 | UPPER_SNAKE_CASE | UPPER_SNAKE_CASE | `API_BASE_URL` |
| 类型/接口 | PascalCase | - | `StudentData` |
| 文件 | kebab-case | snake_case | `user-service.ts` / `user_service.py` |

## 错误处理策略

### 错误流程

```mermaid
sequenceDiagram
    participant C as Client
    participant F as Frontend
    participant API as Backend API
    participant DB as Database
    participant S as Sentry

    C->>F: 用户操作
    F->>API: API请求
    API->>DB: 数据库操作
    DB-->>API: 错误信息
    API->>API: 错误处理
    API->>S: 发送错误日志
    API-->>F: 标准错误响应
    F->>F: 显示错误消息
    F-->>C: 错误提示
```

### 错误响应格式
```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    requestId: string;
  };
}
```

## 监控和可观察性

### 监控栈
- **前端监控:** Sentry + Google Analytics
- **后端监控:** Sentry + Prometheus + Grafana
- **错误跟踪:** Sentry
- **性能监控:** Prometheus + Grafana

### 关键指标

**前端指标:**
- Core Web Vitals (LCP, FID, CLS)
- JavaScript错误
- API响应时间
- 用户交互
- 页面加载时间
- 包大小

**后端指标:**
- 请求率（每秒请求数）
- 错误率（百分比）
- 响应时间（P95 < 200ms）
- 数据库查询性能
- Redis命中率
- CPU/内存使用率
- 活跃WebSocket连接数

## 检查清单结果报告

架构师检查清单已成功完成。所有关键的架构决策都已记录，全栈架构已准备好进行开发实施。该架构支持所有PRD要求，包括扩展到10,000+用户、实时消息传递和全面的数据管理能力。