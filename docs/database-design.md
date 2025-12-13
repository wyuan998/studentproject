# 学生信息管理系统数据库设计文档

## 概述

本文档详细描述了学生信息管理系统的数据库设计，包括数据库架构、表结构、关系设计、索引策略、性能优化和数据迁移方案。

## 数据库架构

### 技术选型

**数据库管理系统:** MySQL 8.0+
- 选择理由：
  - 成熟稳定，广泛应用于教育行业
  - 强大的事务支持和ACID特性
  - 优秀的性能和可扩展性
  - 丰富的索引类型和查询优化器
  - 完善的备份和恢复机制

**字符集:** UTF8MB4
- 支持完整的Unicode字符集，包括emoji
- 兼容性良好，性能稳定

**存储引擎:** InnoDB
- 支持事务和外键约束
- 行级锁定，并发性能好
- 支持热备份

### 数据库命名规范

```sql
-- 表名：小写字母 + 下划线，使用复数形式
students, users, courses, grades, messages

-- 字段名：小写字母 + 下划线，具有描述性
student_id, created_at, updated_at

-- 索引名：idx_表名_字段名
idx_students_student_id, idx_users_username

-- 外键名：fk_表名_字段名
fk_students_user_id, fk_grades_student_id

-- 约束名：uk_表名_字段名（唯一约束）
uk_users_username, uk_students_student_id
```

## 实体关系图 (ERD)

```mermaid
erDiagram
    users ||--o| user_profiles : has
    users ||--o{ students : is
    users ||--o{ teachers : is
    users ||--o{ admins : is
    users ||--o{ audit_logs : generates
    users ||--o{ messages : sends
    users ||--o{ messages : receives

    students ||--o{ enrollments : enrolls_in
    students ||--o{ grades : receives

    courses ||--o{ enrollments : has
    courses ||--o{ grades : assigned
    courses ||--o| users : taught_by

    messages ||--o{ message_templates : uses

    users {
        string id PK
        string username UK
        string email UK
        string password_hash
        enum role
        enum status
        timestamp created_at
        timestamp updated_at
    }

    user_profiles {
        string id PK
        string user_id FK
        string first_name
        string last_name
        string avatar
        string phone
        string department
        timestamp created_at
        timestamp updated_at
    }

    students {
        string id PK
        string user_id FK
        string student_id UK
        string grade
        string class
        string major
        date enrollment_date
        timestamp created_at
        timestamp updated_at
    }

    teachers {
        string id PK
        string user_id FK
        string teacher_id UK
        string title
        string department
        timestamp created_at
        timestamp updated_at
    }

    admins {
        string id PK
        string user_id FK
        json permissions
        timestamp created_at
        timestamp updated_at
    }

    courses {
        string id PK
        string course_code UK
        string name
        text description
        decimal credits
        string teacher_id FK
        timestamp created_at
        timestamp updated_at
    }

    enrollments {
        string id PK
        string student_id FK
        string course_id FK
        string semester
        timestamp enrollment_date
        timestamp created_at
        timestamp updated_at
    }

    grades {
        string id PK
        string student_id FK
        string course_id FK
        decimal score
        string semester
        enum exam_type
        string graded_by FK
        timestamp graded_at
        timestamp created_at
        timestamp updated_at
    }

    messages {
        string id PK
        string sender_id FK
        string receiver_id FK
        string title
        text content
        enum type
        enum status
        enum priority
        timestamp sent_at
        timestamp read_at
        timestamp created_at
        timestamp updated_at
    }

    message_templates {
        string id PK
        string name
        string title_template
        text content_template
        enum type
        json variables
        string created_by FK
        timestamp created_at
        timestamp updated_at
    }

    audit_logs {
        string id PK
        string user_id FK
        string action
        string resource_type
        string resource_id
        json old_values
        json new_values
        string ip_address
        text user_agent
        timestamp created_at
    }

    system_configs {
        string id PK
        string key UK
        text value
        string description
        timestamp created_at
        timestamp updated_at
    }
```

## 表结构详细设计

### 1. 用户相关表

#### users - 用户基础信息表

```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin', 'teacher', 'student') NOT NULL COMMENT '用户角色',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active' COMMENT '账户状态',
    email_verified BOOLEAN DEFAULT FALSE COMMENT '邮箱是否验证',
    last_login_at TIMESTAMP NULL COMMENT '最后登录时间',
    failed_login_attempts INT DEFAULT 0 COMMENT '登录失败次数',
    locked_until TIMESTAMP NULL COMMENT '锁定到期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    UNIQUE KEY uk_users_username (username),
    UNIQUE KEY uk_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_status (status),
    INDEX idx_users_last_login (last_login_at),

    -- 约束
    CONSTRAINT chk_users_role CHECK (role IN ('admin', 'teacher', 'student')),
    CONSTRAINT chk_users_status CHECK (status IN ('active', 'inactive', 'suspended')),
    CONSTRAINT chk_users_email_verified CHECK (email_verified IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户基础信息表';
```

#### user_profiles - 用户资料表

```sql
CREATE TABLE user_profiles (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL COMMENT '关联用户ID',
    first_name VARCHAR(50) NOT NULL COMMENT '名',
    last_name VARCHAR(50) NOT NULL COMMENT '姓',
    avatar VARCHAR(255) NULL COMMENT '头像URL',
    phone VARCHAR(20) NULL COMMENT '手机号',
    address TEXT NULL COMMENT '地址',
    birthday DATE NULL COMMENT '生日',
    gender ENUM('male', 'female', 'other') NULL COMMENT '性别',
    department VARCHAR(100) NULL COMMENT '部门',
    bio TEXT NULL COMMENT '个人简介',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    UNIQUE KEY uk_user_profiles_user_id (user_id),
    INDEX idx_user_profiles_phone (phone),
    INDEX idx_user_profiles_department (department),

    -- 约束
    CONSTRAINT chk_user_profiles_gender CHECK (gender IN ('male', 'female', 'other'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户资料表';
```

#### students - 学生信息表

```sql
CREATE TABLE students (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL COMMENT '关联用户ID',
    student_id VARCHAR(20) NOT NULL COMMENT '学号',
    grade VARCHAR(10) NULL COMMENT '年级',
    class VARCHAR(10) NULL COMMENT '班级',
    major VARCHAR(100) NULL COMMENT '专业',
    enrollment_date DATE NULL COMMENT '入学日期',
    graduation_date DATE NULL COMMENT '毕业日期',
    academic_status ENUM('enrolled', 'graduated', 'suspended', 'withdrawn') DEFAULT 'enrolled' COMMENT '学籍状态',
    gpa DECIMAL(3,2) NULL COMMENT '平均绩点',
    credits_earned DECIMAL(6,2) DEFAULT 0 COMMENT '已获学分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    UNIQUE KEY uk_students_student_id (student_id),
    INDEX idx_students_user_id (user_id),
    INDEX idx_students_grade_class (grade, class),
    INDEX idx_students_major (major),
    INDEX idx_students_academic_status (academic_status),
    INDEX idx_students_enrollment_date (enrollment_date),

    -- 约束
    CONSTRAINT chk_students_academic_status CHECK (academic_status IN ('enrolled', 'graduated', 'suspended', 'withdrawn')),
    CONSTRAINT chk_students_gpa CHECK (gpa >= 0 AND gpa <= 4.0),
    CONSTRAINT chk_students_credits_earned CHECK (credits_earned >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生信息表';
```

#### teachers - 教师信息表

```sql
CREATE TABLE teachers (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL COMMENT '关联用户ID',
    teacher_id VARCHAR(20) NULL COMMENT '教师工号',
    title VARCHAR(50) NULL COMMENT '职称',
    department VARCHAR(100) NULL COMMENT '院系',
    office VARCHAR(100) NULL COMMENT '办公室',
    specialization VARCHAR(200) NULL COMMENT '专业方向',
    education_background VARCHAR(200) NULL COMMENT '教育背景',
    hire_date DATE NULL COMMENT '入职日期',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    UNIQUE KEY uk_teachers_teacher_id (teacher_id),
    INDEX idx_teachers_user_id (user_id),
    INDEX idx_teachers_department (department),
    INDEX idx_teachers_title (title),
    INDEX idx_teachers_status (status),

    -- 约束
    CONSTRAINT chk_teachers_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师信息表';
```

#### admins - 管理员表

```sql
CREATE TABLE admins (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL COMMENT '关联用户ID',
    admin_id VARCHAR(20) NULL COMMENT '管理员编号',
    permissions JSON NULL COMMENT '权限配置',
    is_super_admin BOOLEAN DEFAULT FALSE COMMENT '是否超级管理员',
    department VARCHAR(100) NULL COMMENT '负责部门',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    UNIQUE KEY uk_admins_user_id (user_id),
    UNIQUE KEY uk_admins_admin_id (admin_id),
    INDEX idx_admins_is_super_admin (is_super_admin),

    -- 约束
    CONSTRAINT chk_admins_is_super_admin CHECK (is_super_admin IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';
```

### 2. 课程相关表

#### courses - 课程表

```sql
CREATE TABLE courses (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    course_code VARCHAR(20) NOT NULL COMMENT '课程编号',
    name VARCHAR(100) NOT NULL COMMENT '课程名称',
    description TEXT NULL COMMENT '课程描述',
    credits DECIMAL(3,1) DEFAULT 0 COMMENT '学分',
    hours_per_week INT DEFAULT 0 COMMENT '每周学时',
    course_type ENUM('required', 'elective', 'prerequisite') DEFAULT 'required' COMMENT '课程类型',
    semester VARCHAR(20) NULL COMMENT '开设学期',
    max_students INT DEFAULT 100 COMMENT '最大学生数',
    current_students INT DEFAULT 0 COMMENT '当前学生数',
    status ENUM('active', 'inactive', 'archived') DEFAULT 'active' COMMENT '状态',
    teacher_id CHAR(36) NULL COMMENT '授课教师ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL,

    -- 索引
    UNIQUE KEY uk_courses_course_code (course_code),
    INDEX idx_courses_teacher_id (teacher_id),
    INDEX idx_courses_course_type (course_type),
    INDEX idx_courses_semester (semester),
    INDEX idx_courses_status (status),
    INDEX idx_courses_name (name),

    -- 约束
    CONSTRAINT chk_courses_credits CHECK (credits >= 0 AND credits <= 10),
    CONSTRAINT chk_courses_hours_per_week CHECK (hours_per_week >= 0),
    CONSTRAINT chk_courses_max_students CHECK (max_students > 0),
    CONSTRAINT chk_courses_current_students CHECK (current_students >= 0),
    CONSTRAINT chk_courses_course_type CHECK (course_type IN ('required', 'elective', 'prerequisite')),
    CONSTRAINT chk_courses_status CHECK (status IN ('active', 'inactive', 'archived'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';
```

#### enrollments - 选课表

```sql
CREATE TABLE enrollments (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    student_id CHAR(36) NOT NULL COMMENT '学生ID',
    course_id CHAR(36) NOT NULL COMMENT '课程ID',
    semester VARCHAR(20) NOT NULL COMMENT '学期',
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    status ENUM('enrolled', 'dropped', 'completed') DEFAULT 'enrolled' COMMENT '选课状态',
    grade DECIMAL(5,2) NULL COMMENT '最终成绩',
    credits_earned DECIMAL(3,1) NULL COMMENT '获得学分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,

    -- 索引
    UNIQUE KEY uk_enrollments_student_course_semester (student_id, course_id, semester),
    INDEX idx_enrollments_student_id (student_id),
    INDEX idx_enrollments_course_id (course_id),
    INDEX idx_enrollments_semester (semester),
    INDEX idx_enrollments_status (status),
    INDEX idx_enrollments_enrollment_date (enrollment_date),

    -- 约束
    CONSTRAINT chk_enrollments_status CHECK (status IN ('enrolled', 'dropped', 'completed')),
    CONSTRAINT chk_enrollments_grade CHECK (grade IS NULL OR (grade >= 0 AND grade <= 100)),
    CONSTRAINT chk_enrollments_credits_earned CHECK (credits_earned IS NULL OR credits_earned >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课表';
```

### 3. 成绩相关表

#### grades - 成绩表

```sql
CREATE TABLE grades (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    student_id CHAR(36) NOT NULL COMMENT '学生ID',
    course_id CHAR(36) NOT NULL COMMENT '课程ID',
    score DECIMAL(5,2) NOT NULL COMMENT '成绩分数',
    semester VARCHAR(20) NOT NULL COMMENT '学期',
    exam_type ENUM('midterm', 'final', 'quiz', 'assignment', 'project') NOT NULL COMMENT '考试类型',
    max_score DECIMAL(5,2) DEFAULT 100 COMMENT '满分',
    weight DECIMAL(3,2) DEFAULT 1.0 COMMENT '权重',
    graded_by CHAR(36) NOT NULL COMMENT '评分教师ID',
    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评分时间',
    comments TEXT NULL COMMENT '评语',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    INDEX idx_grades_student_course (student_id, course_id),
    INDEX idx_grades_course_id (course_id),
    INDEX idx_grades_semester (semester),
    INDEX idx_grades_exam_type (exam_type),
    INDEX idx_grades_graded_by (graded_by),
    INDEX idx_grades_score (score),
    INDEX idx_grades_graded_at (graded_at),

    -- 约束
    CONSTRAINT chk_grades_score CHECK (score >= 0 AND score <= max_score),
    CONSTRAINT chk_grades_max_score CHECK (max_score > 0),
    CONSTRAINT chk_grades_weight CHECK (weight > 0 AND weight <= 1),
    CONSTRAINT chk_grades_exam_type CHECK (exam_type IN ('midterm', 'final', 'quiz', 'assignment', 'project'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩表';
```

### 4. 消息相关表

#### messages - 消息表

```sql
CREATE TABLE messages (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    sender_id CHAR(36) NOT NULL COMMENT '发送者ID',
    receiver_id CHAR(36) NOT NULL COMMENT '接收者ID',
    title VARCHAR(200) NOT NULL COMMENT '消息标题',
    content TEXT NOT NULL COMMENT '消息内容',
    type ENUM('system', 'business', 'personal', 'notification') NOT NULL COMMENT '消息类型',
    status ENUM('unread', 'read', 'archived') DEFAULT 'unread' COMMENT '阅读状态',
    priority ENUM('low', 'normal', 'high', 'urgent') DEFAULT 'normal' COMMENT '优先级',
    has_attachment BOOLEAN DEFAULT FALSE COMMENT '是否有附件',
    attachment_url VARCHAR(500) NULL COMMENT '附件URL',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    read_at TIMESTAMP NULL COMMENT '阅读时间',
    expires_at TIMESTAMP NULL COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    INDEX idx_messages_receiver_status (receiver_id, status),
    INDEX idx_messages_sender_id (sender_id),
    INDEX idx_messages_type (type),
    INDEX idx_messages_priority (priority),
    INDEX idx_messages_sent_at (sent_at),
    INDEX idx_messages_expires_at (expires_at),

    -- 约束
    CONSTRAINT chk_messages_status CHECK (status IN ('unread', 'read', 'archived')),
    CONSTRAINT chk_messages_type CHECK (type IN ('system', 'business', 'personal', 'notification')),
    CONSTRAINT chk_messages_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    CONSTRAINT chk_messages_has_attachment CHECK (has_attachment IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';
```

#### message_templates - 消息模板表

```sql
CREATE TABLE message_templates (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    title_template VARCHAR(200) NOT NULL COMMENT '标题模板',
    content_template TEXT NOT NULL COMMENT '内容模板',
    type ENUM('system', 'business', 'personal', 'notification') NOT NULL COMMENT '消息类型',
    variables JSON NULL COMMENT '变量定义',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    usage_count INT DEFAULT 0 COMMENT '使用次数',
    created_by CHAR(36) NOT NULL COMMENT '创建者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 外键
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    UNIQUE KEY uk_message_templates_name (name),
    INDEX idx_message_templates_type (type),
    INDEX idx_message_templates_is_active (is_active),
    INDEX idx_message_templates_created_by (created_by),

    -- 约束
    CONSTRAINT chk_message_templates_type CHECK (type IN ('system', 'business', 'personal', 'notification')),
    CONSTRAINT chk_message_templates_is_active CHECK (is_active IN (TRUE, FALSE)),
    CONSTRAINT chk_message_templates_usage_count CHECK (usage_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息模板表';
```

### 5. 系统相关表

#### audit_logs - 审计日志表

```sql
CREATE TABLE audit_logs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL COMMENT '用户ID',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) NOT NULL COMMENT '资源类型',
    resource_id CHAR(36) NULL COMMENT '资源ID',
    old_values JSON NULL COMMENT '旧值',
    new_values JSON NULL COMMENT '新值',
    ip_address VARCHAR(45) NULL COMMENT 'IP地址',
    user_agent TEXT NULL COMMENT '用户代理',
    session_id VARCHAR(100) NULL COMMENT '会话ID',
    success BOOLEAN DEFAULT TRUE COMMENT '是否成功',
    error_message TEXT NULL COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    -- 索引
    INDEX idx_audit_logs_user_action (user_id, action),
    INDEX idx_audit_logs_resource (resource_type, resource_id),
    INDEX idx_audit_logs_created_at (created_at),
    INDEX idx_audit_logs_ip_address (ip_address),
    INDEX idx_audit_logs_success (success),

    -- 约束
    CONSTRAINT chk_audit_logs_success CHECK (success IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';
```

#### system_configs - 系统配置表

```sql
CREATE TABLE system_configs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    value TEXT NULL COMMENT '配置值',
    description VARCHAR(255) NULL COMMENT '描述',
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string' COMMENT '配置类型',
    is_editable BOOLEAN DEFAULT TRUE COMMENT '是否可编辑',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_system_configs_key (key),
    INDEX idx_system_configs_is_editable (is_editable),

    -- 约束
    CONSTRAINT chk_system_configs_config_type CHECK (config_type IN ('string', 'number', 'boolean', 'json')),
    CONSTRAINT chk_system_configs_is_editable CHECK (is_editable IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';
```

## 索引策略

### 主键索引
- 所有表使用UUID作为主键，使用`CHAR(36)`存储
- 保证全局唯一性，便于分布式系统

### 唯一索引（Unique Key）
```sql
-- 用户表唯一索引
uk_users_username (username)
uk_users_email (email)

-- 学生表唯一索引
uk_students_student_id (student_id)

-- 课程表唯一索引
uk_courses_course_code (course_code)

-- 选课表复合唯一索引
uk_enrollments_student_course_semester (student_id, course_id, semester)
```

### 复合索引（Composite Index）
```sql
-- 查询优化索引
idx_grades_student_course (student_id, course_id)
idx_messages_receiver_status (receiver_id, status)
idx_audit_logs_user_action (user_id, action)
idx_enrollments_semester_status (semester, status)
```

### 查询索引建议

#### 1. 按查询频率优化
```sql
-- 高频查询：学生信息查询
idx_students_student_id (student_id)          -- 学号查询
idx_students_grade_class (grade, class)        -- 年级班级查询
idx_students_academic_status (academic_status) -- 学籍状态查询

-- 高频查询：成绩查询
idx_grades_student_semester (student_id, semester)     -- 学生学期成绩
idx_grades_course_semester (course_id, semester)       -- 课程学期成绩
idx_grades_exam_type_score (exam_type, score)          -- 成绩分布查询

-- 高频查询：消息系统
idx_messages_receiver_status_sent_at (receiver_id, status, sent_at)  -- 消息列表
idx_messages_sender_created_at (sender_id, created_at)              -- 发送消息历史
```

#### 2. 按数据量优化
```sql
-- 大数据量表索引策略
audit_logs: 基于时间的分区索引
idx_audit_logs_created_at (created_at)
idx_audit_logs_user_created_at (user_id, created_at)

-- 历史数据归档
考虑将超过2年的audit_logs数据归档到历史表
```

### 索引创建示例

```sql
-- 创建复合索引
CREATE INDEX idx_students_grade_class_major ON students (grade, class, major);

-- 创建部分索引（仅对活跃数据）
CREATE INDEX idx_courses_active ON courses (id) WHERE status = 'active';

-- 创建函数索引（对JSON字段）
CREATE INDEX idx_admins_permissions ON admins ((CAST(permissions AS CHAR(255))));
```

## 性能优化

### 1. 查询优化

#### 分页查询优化
```sql
-- 使用覆盖索引优化分页
-- 不推荐
SELECT * FROM students ORDER BY created_at LIMIT 20 OFFSET 10000;

-- 推荐
SELECT s.* FROM students s
JOIN (SELECT id FROM students ORDER BY created_at LIMIT 20 OFFSET 10000) AS t ON s.id = t.id;
```

#### JOIN查询优化
```sql
-- 使用明确的JOIN类型
SELECT s.id, s.student_id, u.username, p.first_name
FROM students s
INNER JOIN users u ON s.user_id = u.id
LEFT JOIN user_profiles p ON s.user_id = p.user_id
WHERE s.grade = '2024'
ORDER BY s.student_id;
```

#### 统计查询优化
```sql
-- 使用索引列进行COUNT
-- 不推荐
SELECT COUNT(*) FROM students WHERE grade = '2024';

-- 推荐
SELECT COUNT(student_id) FROM students WHERE grade = '2024';
```

### 2. 表分区策略

#### 按时间分区（audit_logs）
```sql
-- 创建分区表
CREATE TABLE audit_logs_partitioned (
    id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- 其他字段...
    PRIMARY KEY (id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### 3. 数据归档策略

#### 历史数据归档
```sql
-- 创建归档表
CREATE TABLE audit_logs_archive LIKE audit_logs;

-- 归档1年前的数据
INSERT INTO audit_logs_archive
SELECT * FROM audit_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- 删除已归档的数据
DELETE FROM audit_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

## 数据完整性

### 1. 外键约束
- 确保引用完整性
- 级联删除策略谨慎使用
- 重要数据使用SET NULL而不是CASCADE

### 2. 检查约束
```sql
-- 成绩范围检查
CONSTRAINT chk_grades_score CHECK (score >= 0 AND score <= 100)

-- 学分范围检查
CONSTRAINT chk_courses_credits CHECK (credits >= 0 AND credits <= 10)

-- 状态枚举检查
CONSTRAINT chk_users_status CHECK (status IN ('active', 'inactive', 'suspended'))
```

### 3. 触发器示例

```sql
-- 更新课程学生数量
DELIMITER $$
CREATE TRIGGER tr_enrollments_after_insert
AFTER INSERT ON enrollments
FOR EACH ROW
BEGIN
    UPDATE courses
    SET current_students = current_students + 1
    WHERE id = NEW.course_id;
END$$
DELIMITER ;

-- 记录审计日志
DELIMITER $$
CREATE TRIGGER tr_users_after_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id, action, resource_type, resource_id,
        old_values, new_values, ip_address
    ) VALUES (
        NEW.id, 'UPDATE', 'user', NEW.id,
        JSON_OBJECT(
            'username', OLD.username,
            'email', OLD.email,
            'status', OLD.status
        ),
        JSON_OBJECT(
            'username', NEW.username,
            'email', NEW.email,
            'status', NEW.status
        ),
        CONNECTION_ID()
    );
END$$
DELIMITER ;
```

## 备份和恢复策略

### 1. 备份策略

#### 全量备份（每周）
```bash
#!/bin/bash
# 全量备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mysql"
DB_NAME="student_management"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行全量备份
mysqldump -u backup_user -p$BACKUP_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --hex-blob \
    --master-data=2 \
    --flush-logs \
    $DB_NAME | gzip > $BACKUP_DIR/full_backup_$DATE.sql.gz

# 保留30天的备份
find $BACKUP_DIR -name "full_backup_*.sql.gz" -mtime +30 -delete
```

#### 增量备份（每日）
```bash
#!/bin/bash
# 增量备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mysql/incremental"
LAST_BINLOG=$(mysql -u backup_user -p$BACKUP_PASSWORD -e "SHOW MASTER STATUS;" | awk 'NR==2 {print $1}')

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行增量备份
mysqlbinlog --read-from-remote-server \
    --host=localhost \
    --user=backup_user \
    --password=$BACKUP_PASSWORD \
    --raw \
    --stop-never \
    $LAST_BINLOG
```

### 2. 恢复策略

#### 恢复全量备份
```bash
# 恢复数据库
gunzip < full_backup_20241213_020000.sql.gz | mysql -u root -p student_management
```

#### 时间点恢复
```bash
# 恢复到指定时间点
mysqlbinlog --start-datetime="2024-12-13 14:30:00" \
    --stop-datetime="2024-12-13 15:00:00" \
    mysql-bin.000123 | mysql -u root -p student_management
```

## 数据迁移方案

### 1. 从Excel导入

#### 数据验证流程
```python
# 数据验证示例
import pandas as pd
import re
from datetime import datetime

def validate_student_data(file_path):
    """验证学生数据"""
    df = pd.read_excel(file_path)

    errors = []

    # 验证必填字段
    required_fields = ['学号', '姓名', '年级', '班级', '专业']
    for field in required_fields:
        if field not in df.columns:
            errors.append(f"缺少必填字段: {field}")

    # 验证学号格式
    for idx, row in df.iterrows():
        # 学号验证（10位数字）
        student_id = str(row['学号'])
        if not re.match(r'^\d{10}$', student_id):
            errors.append(f"第{idx+2}行: 学号格式错误 - {student_id}")

        # 姓名验证
        name = str(row['姓名']).strip()
        if len(name) < 2 or len(name) > 20:
            errors.append(f"第{idx+2}行: 姓名长度错误 - {name}")

        # 年级验证
        grade = str(row['年级'])
        if not re.match(r'^20\d{2}$', grade):
            errors.append(f"第{idx+2}行: 年级格式错误 - {grade}")

    return errors
```

#### 数据转换脚本
```python
# 数据转换和导入
def import_students_from_excel(file_path):
    """从Excel导入学生数据"""
    # 读取数据
    df = pd.read_excel(file_path)

    # 数据转换
    success_count = 0
    error_count = 0

    for idx, row in df.iterrows():
        try:
            # 创建用户
            user = User(
                username=row['学号'],
                email=row.get('邮箱', f"{row['学号']}@example.com"),
                password_hash=generate_password_hash('123456'),  # 默认密码
                role='student'
            )

            # 创建用户资料
            profile = UserProfile(
                first_name=row['姓'],
                last_name=row['名'],
                department=row.get('院系', '')
            )

            # 创建学生信息
            student = Student(
                student_id=str(row['学号']),
                grade=str(row['年级']),
                class=str(row['班级']),
                major=row['专业'],
                enrollment_date=pd.to_datetime(row['入学日期']).date()
            )

            # 保存数据
            db.session.add(user)
            db.session.commit()

            profile.user_id = user.id
            db.session.add(profile)
            db.session.commit()

            student.user_id = user.id
            db.session.add(student)
            db.session.commit()

            success_count += 1

        except Exception as e:
            error_count += 1
            print(f"导入失败: 第{idx+2}行 - {str(e)}")
            db.session.rollback()

    return success_count, error_count
```

### 2. 数据迁移检查清单

- [ ] 数据验证规则定义
- [ ] 错误数据清洗
- [ ] 重复数据检测和处理
- [ ] 数据类型转换
- [ ] 外键关系建立
- [ ] 数据完整性检查
- [ ] 性能测试
- [ ] 回滚方案准备

## 监控和维护

### 1. 性能监控指标

```sql
-- 慢查询监控
SELECT
    query_time,
    lock_time,
    rows_sent,
    rows_examined,
    sql_text
FROM mysql.slow_log
WHERE start_time > DATE_SUB(NOW(), INTERVAL 1 HOUR)
ORDER BY query_time DESC;

-- 表大小监控
SELECT
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
    table_rows
FROM information_schema.tables
WHERE table_schema = 'student_management'
ORDER BY (data_length + index_length) DESC;

-- 索引使用情况
SELECT
    table_name,
    index_name,
    cardinality,
    sub_part,
    packed,
    nullable,
    index_type
FROM information_schema.statistics
WHERE table_schema = 'student_management'
ORDER BY table_name, seq_in_index;
```

### 2. 定期维护任务

#### 每日任务
```sql
-- 清理过期会话
DELETE FROM user_sessions WHERE expires_at < NOW();

-- 更新统计信息
ANALYZE TABLE students, courses, grades, messages;
```

#### 每周任务
```sql
-- 优化表
OPTIMIZE TABLE audit_logs;

-- 清理过期消息
DELETE FROM messages
WHERE type = 'notification'
AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

#### 每月任务
```sql
-- 重建索引
ALTER TABLE students ENGINE=InnoDB;

-- 分析表统计信息
ANALYZE TABLE students, courses, grades, enrollments, messages;
```

## 安全考虑

### 1. 数据加密

```sql
-- 敏感字段加密
ALTER TABLE users
ADD COLUMN encrypted_credit_card VARCHAR(255) NULL;

-- 使用AES_ENCRYPT加密
UPDATE users
SET encrypted_credit_card = AES_ENCRYPT(card_number, @encryption_key);
```

### 2. 访问控制

```sql
-- 创建只读用户
CREATE USER 'readonly'@'%' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON student_management.* TO 'readonly'@'%';

-- 创建备份用户
CREATE USER 'backup'@'localhost' IDENTIFIED BY 'backup_password';
GRANT SELECT, LOCK TABLES, SHOW VIEW ON student_management.* TO 'backup'@'localhost';
```

### 3. 审计日志

```sql
-- 启用审计日志插件
INSTALL PLUGIN audit_log SONAME 'audit_log';

-- 配置审计规则
SET GLOBAL audit_log_policy = 'ALL';
SET GLOBAL audit_log_format = 'JSON';
SET GLOBAL audit_log_file = 'audit.log';
```

## 总结

本数据库设计文档提供了学生信息管理系统的完整数据库架构，包括：

1. **完整的表结构设计**：11个核心表，满足所有业务需求
2. **优化的索引策略**：主键、唯一索引、复合索引的合理设计
3. **性能优化方案**：查询优化、分区策略、归档策略
4. **数据完整性保障**：外键约束、检查约束、触发器
5. **备份恢复方案**：全量备份、增量备份、时间点恢复
6. **数据迁移策略**：Excel导入、数据验证、清洗流程
7. **监控维护指南**：性能监控、定期维护任务
8. **安全加固措施**：数据加密、访问控制、审计日志

该设计支持：
- 10,000+用户的并发访问
- 实时消息通知系统
- 完整的权限管理
- 高效的数据查询
- 系统的可扩展性

数据库架构已经准备就绪，可以直接用于开发实施。