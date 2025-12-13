-- ========================================
-- 学生信息管理系统数据库初始化脚本
-- 版本: 1.0
-- 创建时间: 2024-12-13
-- ========================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS student_management
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE student_management;

-- 设置时区
SET time_zone = '+08:00';

-- ========================================
-- 创建用户和权限
-- ========================================

-- 创建应用用户
CREATE USER IF NOT EXISTS 'sms_app'@'%' IDENTIFIED BY 'sms_app_password_2024';
CREATE USER IF NOT EXISTS 'sms_app'@'localhost' IDENTIFIED BY 'sms_app_password_2024';

-- 创建只读用户（用于报表和监控）
CREATE USER IF NOT EXISTS 'sms_readonly'@'%' IDENTIFIED BY 'sms_readonly_2024';
CREATE USER IF NOT EXISTS 'sms_readonly'@'localhost' IDENTIFIED BY 'sms_readonly_2024';

-- 创建备份用户
CREATE USER IF NOT EXISTS 'sms_backup'@'localhost' IDENTIFIED BY 'sms_backup_2024';

-- 授予权限
GRANT SELECT, INSERT, UPDATE, DELETE ON student_management.* TO 'sms_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON student_management.* TO 'sms_app'@'localhost';
GRANT SELECT ON student_management.* TO 'sms_readonly'@'%';
GRANT SELECT ON student_management.* TO 'sms_readonly'@'localhost';
GRANT SELECT, LOCK TABLES, SHOW VIEW ON student_management.* TO 'sms_backup'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- ========================================
-- 设置系统配置
-- ========================================

-- 启用性能模式（可选）
SET GLOBAL innodb_file_per_table = ON;
SET GLOBAL innodb_file_format = Barracuda;
SET GLOBAL innodb_large_prefix = ON;

-- 设置字符集
SET GLOBAL character_set_server = utf8mb4;
SET GLOBAL collation_server = utf8mb4_unicode_ci;

-- ========================================
-- 创建基础表结构
-- ========================================

-- 用户基础信息表
CREATE TABLE IF NOT EXISTS users (
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

    UNIQUE KEY uk_users_username (username),
    UNIQUE KEY uk_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_status (status),
    INDEX idx_users_last_login (last_login_at),

    CONSTRAINT chk_users_role CHECK (role IN ('admin', 'teacher', 'student')),
    CONSTRAINT chk_users_status CHECK (status IN ('active', 'inactive', 'suspended')),
    CONSTRAINT chk_users_email_verified CHECK (email_verified IN (TRUE, FALSE)),
    CONSTRAINT chk_users_failed_attempts CHECK (failed_login_attempts >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户基础信息表';

-- 用户资料表
CREATE TABLE IF NOT EXISTS user_profiles (
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

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_profiles_user_id (user_id),
    INDEX idx_user_profiles_phone (phone),
    INDEX idx_user_profiles_department (department),
    INDEX idx_user_profiles_gender (gender),

    CONSTRAINT chk_user_profiles_gender CHECK (gender IN ('male', 'female', 'other'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户资料表';

-- 学生信息表
CREATE TABLE IF NOT EXISTS students (
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

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_students_student_id (student_id),
    INDEX idx_students_user_id (user_id),
    INDEX idx_students_grade_class (grade, class),
    INDEX idx_students_major (major),
    INDEX idx_students_academic_status (academic_status),
    INDEX idx_students_enrollment_date (enrollment_date),

    CONSTRAINT chk_students_academic_status CHECK (academic_status IN ('enrolled', 'graduated', 'suspended', 'withdrawn')),
    CONSTRAINT chk_students_gpa CHECK (gpa IS NULL OR (gpa >= 0 AND gpa <= 4.0)),
    CONSTRAINT chk_students_credits_earned CHECK (credits_earned >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生信息表';

-- 教师信息表
CREATE TABLE IF NOT EXISTS teachers (
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

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_teachers_teacher_id (teacher_id),
    INDEX idx_teachers_user_id (user_id),
    INDEX idx_teachers_department (department),
    INDEX idx_teachers_title (title),
    INDEX idx_teachers_status (status),

    CONSTRAINT chk_teachers_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师信息表';

-- 管理员表
CREATE TABLE IF NOT EXISTS admins (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL COMMENT '关联用户ID',
    admin_id VARCHAR(20) NULL COMMENT '管理员编号',
    permissions JSON NULL COMMENT '权限配置',
    is_super_admin BOOLEAN DEFAULT FALSE COMMENT '是否超级管理员',
    department VARCHAR(100) NULL COMMENT '负责部门',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_admins_user_id (user_id),
    UNIQUE KEY uk_admins_admin_id (admin_id),
    INDEX idx_admins_is_super_admin (is_super_admin),
    INDEX idx_admins_department (department),

    CONSTRAINT chk_admins_is_super_admin CHECK (is_super_admin IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- 课程表
CREATE TABLE IF NOT EXISTS courses (
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

    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY uk_courses_course_code (course_code),
    INDEX idx_courses_teacher_id (teacher_id),
    INDEX idx_courses_course_type (course_type),
    INDEX idx_courses_semester (semester),
    INDEX idx_courses_status (status),
    INDEX idx_courses_name (name),

    CONSTRAINT chk_courses_credits CHECK (credits >= 0 AND credits <= 10),
    CONSTRAINT chk_courses_hours_per_week CHECK (hours_per_week >= 0),
    CONSTRAINT chk_courses_max_students CHECK (max_students > 0),
    CONSTRAINT chk_courses_current_students CHECK (current_students >= 0),
    CONSTRAINT chk_courses_course_type CHECK (course_type IN ('required', 'elective', 'prerequisite')),
    CONSTRAINT chk_courses_status CHECK (status IN ('active', 'inactive', 'archived'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- 选课表
CREATE TABLE IF NOT EXISTS enrollments (
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

    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY uk_enrollments_student_course_semester (student_id, course_id, semester),
    INDEX idx_enrollments_student_id (student_id),
    INDEX idx_enrollments_course_id (course_id),
    INDEX idx_enrollments_semester (semester),
    INDEX idx_enrollments_status (status),
    INDEX idx_enrollments_enrollment_date (enrollment_date),

    CONSTRAINT chk_enrollments_status CHECK (status IN ('enrolled', 'dropped', 'completed')),
    CONSTRAINT chk_enrollments_grade CHECK (grade IS NULL OR (grade >= 0 AND grade <= 100)),
    CONSTRAINT chk_enrollments_credits_earned CHECK (credits_earned IS NULL OR credits_earned >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课表';

-- 成绩表
CREATE TABLE IF NOT EXISTS grades (
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

    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_grades_student_course (student_id, course_id),
    INDEX idx_grades_course_id (course_id),
    INDEX idx_grades_semester (semester),
    INDEX idx_grades_exam_type (exam_type),
    INDEX idx_grades_graded_by (graded_by),
    INDEX idx_grades_score (score),
    INDEX idx_grades_graded_at (graded_at),

    CONSTRAINT chk_grades_score CHECK (score >= 0 AND score <= max_score),
    CONSTRAINT chk_grades_max_score CHECK (max_score > 0),
    CONSTRAINT chk_grades_weight CHECK (weight > 0 AND weight <= 1),
    CONSTRAINT chk_grades_exam_type CHECK (exam_type IN ('midterm', 'final', 'quiz', 'assignment', 'project'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩表';

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
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

    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_messages_receiver_status (receiver_id, status),
    INDEX idx_messages_sender_id (sender_id),
    INDEX idx_messages_type (type),
    INDEX idx_messages_priority (priority),
    INDEX idx_messages_sent_at (sent_at),
    INDEX idx_messages_expires_at (expires_at),

    CONSTRAINT chk_messages_status CHECK (status IN ('unread', 'read', 'archived')),
    CONSTRAINT chk_messages_type CHECK (type IN ('system', 'business', 'personal', 'notification')),
    CONSTRAINT chk_messages_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    CONSTRAINT chk_messages_has_attachment CHECK (has_attachment IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- 消息模板表
CREATE TABLE IF NOT EXISTS message_templates (
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

    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_message_templates_name (name),
    INDEX idx_message_templates_type (type),
    INDEX idx_message_templates_is_active (is_active),
    INDEX idx_message_templates_created_by (created_by),

    CONSTRAINT chk_message_templates_type CHECK (type IN ('system', 'business', 'personal', 'notification')),
    CONSTRAINT chk_message_templates_is_active CHECK (is_active IN (TRUE, FALSE)),
    CONSTRAINT chk_message_templates_usage_count CHECK (usage_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息模板表';

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
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

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_audit_logs_user_action (user_id, action),
    INDEX idx_audit_logs_resource (resource_type, resource_id),
    INDEX idx_audit_logs_created_at (created_at),
    INDEX idx_audit_logs_ip_address (ip_address),
    INDEX idx_audit_logs_success (success),

    CONSTRAINT chk_audit_logs_success CHECK (success IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    `key` VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    value TEXT NULL COMMENT '配置值',
    description VARCHAR(255) NULL COMMENT '描述',
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string' COMMENT '配置类型',
    is_editable BOOLEAN DEFAULT TRUE COMMENT '是否可编辑',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_system_configs_key (`key`),
    INDEX idx_system_configs_is_editable (is_editable),

    CONSTRAINT chk_system_configs_config_type CHECK (config_type IN ('string', 'number', 'boolean', 'json')),
    CONSTRAINT chk_system_configs_is_editable CHECK (is_editable IN (TRUE, FALSE))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ========================================
-- 插入初始数据
-- ========================================

-- 插入系统配置
INSERT INTO system_configs (`key`, value, description, config_type, is_editable) VALUES
('system.name', '学生信息管理系统', '系统名称', 'string', FALSE),
('system.version', '1.0.0', '系统版本', 'string', FALSE),
('system.max_file_size', '10485760', '最大文件上传大小（字节）', 'number', TRUE),
('system.session_timeout', '3600', '会话超时时间（秒）', 'number', TRUE),
('system.password_min_length', '6', '密码最小长度', 'number', TRUE),
('system.allow_registration', 'false', '是否允许用户注册', 'boolean', TRUE),
('notification.email_enabled', 'true', '是否启用邮件通知', 'boolean', TRUE),
('notification.sms_enabled', 'false', '是否启用短信通知', 'boolean', TRUE);

-- ========================================
-- 创建触发器
-- ========================================

-- 更新选课人数触发器
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS tr_enrollments_after_insert
AFTER INSERT ON enrollments
FOR EACH ROW
BEGIN
    UPDATE courses
    SET current_students = (
        SELECT COUNT(*)
        FROM enrollments
        WHERE course_id = NEW.course_id
        AND status = 'enrolled'
    )
    WHERE id = NEW.course_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER IF NOT EXISTS tr_enrollments_after_update
AFTER UPDATE ON enrollments
FOR EACH ROW
BEGIN
    UPDATE courses
    SET current_students = (
        SELECT COUNT(*)
        FROM enrollments
        WHERE course_id = NEW.course_id
        AND status = 'enrolled'
    )
    WHERE id = NEW.course_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER IF NOT EXISTS tr_enrollments_after_delete
AFTER DELETE ON enrollments
FOR EACH ROW
BEGIN
    UPDATE courses
    SET current_students = (
        SELECT COUNT(*)
        FROM enrollments
        WHERE course_id = OLD.course_id
        AND status = 'enrolled'
    )
    WHERE id = OLD.course_id;
END$$
DELIMITER ;

-- 记录用户操作审计日志
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS tr_users_after_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    IF OLD.username != NEW.username OR OLD.email != NEW.email OR OLD.status != NEW.status THEN
        INSERT INTO audit_logs (
            user_id,
            action,
            resource_type,
            resource_id,
            old_values,
            new_values,
            ip_address,
            user_agent,
            session_id
        ) VALUES (
            NEW.id,
            'UPDATE',
            'user',
            NEW.id,
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
            CONNECTION_ID(),
            NULL,
            NULL
        );
    END IF;
END$$
DELIMITER ;

-- 更新修改时间触发器
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS tr_users_update_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER IF NOT EXISTS tr_students_update_timestamp
BEFORE UPDATE ON students
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER IF NOT EXISTS tr_courses_update_timestamp
BEFORE UPDATE ON courses
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

-- ========================================
-- 创建视图
-- ========================================

-- 学生详情视图
CREATE OR REPLACE VIEW v_student_details AS
SELECT
    s.id,
    s.student_id,
    s.grade,
    s.class,
    s.major,
    s.enrollment_date,
    s.academic_status,
    s.gpa,
    s.credits_earned,
    u.username,
    u.email,
    up.first_name,
    up.last_name,
    up.phone,
    up.department,
    s.created_at
FROM students s
JOIN users u ON s.user_id = u.id
JOIN user_profiles up ON s.user_id = up.user_id;

-- 课程详情视图（包含教师信息）
CREATE OR REPLACE VIEW v_course_details AS
SELECT
    c.id,
    c.course_code,
    c.name,
    c.description,
    c.credits,
    c.hours_per_week,
    c.course_type,
    c.semester,
    c.max_students,
    c.current_students,
    c.status,
    u.username as teacher_username,
    up.first_name as teacher_first_name,
    up.last_name as teacher_last_name,
    t.title as teacher_title,
    c.created_at
FROM courses c
LEFT JOIN users u ON c.teacher_id = u.id
LEFT JOIN user_profiles up ON c.teacher_id = up.user_id
LEFT JOIN teachers t ON c.teacher_id = t.user_id;

-- 成绩统计视图
CREATE OR REPLACE VIEW v_grade_statistics AS
SELECT
    s.student_id,
    s.student_name,
    c.course_code,
    c.course_name,
    g.semester,
    g.exam_type,
    g.score,
    g.graded_at,
    CASE
        WHEN g.score >= 90 THEN 'A'
        WHEN g.score >= 80 THEN 'B'
        WHEN g.score >= 70 THEN 'C'
        WHEN g.score >= 60 THEN 'D'
        ELSE 'F'
    END as grade_letter,
    c.credits
FROM grades g
JOIN students s ON g.student_id = s.id
JOIN courses c ON g.course_id = c.id;

-- ========================================
-- 输出初始化完成信息
-- ========================================

SELECT 'Database initialization completed successfully!' as status,
       NOW() as completion_time;