-- ========================================
-- 创建默认管理员用户
-- ========================================

-- 默认超级管理员
-- 用户名: admin
-- 密码: 123456 (生产环境请立即修改)
INSERT INTO users (
    id,
    username,
    email,
    password_hash,
    role,
    status,
    email_verified,
    created_at,
    updated_at
) VALUES (
    UUID(),
    'admin',
    'admin@example.com',
    '$2b$12$YourHashedPasswordHere',  -- 实际部署时需要使用正确哈希
    'admin',
    'active',
    TRUE,
    NOW(),
    NOW()
);

-- 获取刚创建的管理员ID
SET @admin_user_id = LAST_INSERT_ID();

-- 创建管理员资料
INSERT INTO user_profiles (
    id,
    user_id,
    first_name,
    last_name,
    department,
    created_at,
    updated_at
) VALUES (
    UUID(),
    @admin_user_id,
    '系统',
    '管理员',
    '信息技术部',
    NOW(),
    NOW()
);

-- 创建管理员记录
INSERT INTO admins (
    id,
    user_id,
    admin_id,
    permissions,
    is_super_admin,
    department,
    created_at,
    updated_at
) VALUES (
    UUID(),
    @admin_user_id,
    'ADMIN001',
    JSON_OBJECT(
        'user_management', TRUE,
        'student_management', TRUE,
        'teacher_management', TRUE,
        'course_management', TRUE,
        'grade_management', TRUE,
        'system_config', TRUE,
        'data_import_export', TRUE,
        'reports', TRUE,
        'audit_logs', TRUE,
        'message_management', TRUE
    ),
    TRUE,
    '信息技术部',
    NOW(),
    NOW()
);

-- ========================================
-- 创建示例用户（仅开发环境）
-- ========================================

-- 开发环境检查
SET @is_development = (SELECT @@version LIKE '%dev%' OR @@hostname LIKE '%dev%');

-- 仅在开发环境创建示例数据
-- 生产环境会跳过这部分
INSERT INTO users (
    id,
    username,
    email,
    password_hash,
    role,
    status,
    email_verified,
    created_at,
    updated_at
) SELECT
    UUID(),
    CASE idx WHEN 1 THEN 'teacher01' WHEN 2 THEN 'student01' END,
    CASE idx WHEN 1 THEN 'teacher01@example.com' WHEN 2 THEN 'student01@example.com' END,
    '$2b$12$YourHashedPasswordHere',  -- 实际部署时需要使用正确哈希
    CASE idx WHEN 1 THEN 'teacher' WHEN 2 THEN 'student' END,
    'active',
    TRUE,
    NOW(),
    NOW()
FROM (
    SELECT 1 AS idx UNION SELECT 2
) AS numbers
WHERE @is_development = 1;

-- 创建教师资料（仅开发环境）
INSERT INTO user_profiles (
    id,
    user_id,
    first_name,
    last_name,
    department,
    created_at,
    updated_at
) SELECT
    UUID(),
    u.id,
    CASE WHEN u.role = 'teacher' THEN '张' ELSE '李' END,
    CASE WHEN u.role = 'teacher' THEN '老师' ELSE '同学' END,
    CASE WHEN u.role = 'teacher' THEN '计算机科学系' ELSE '计算机科学与技术' END,
    NOW(),
    NOW()
FROM users u
WHERE u.role = 'teacher'
AND @is_development = 1;

-- 创建教师记录（仅开发环境）
INSERT INTO teachers (
    id,
    user_id,
    teacher_id,
    title,
    department,
    created_at,
    updated_at
) SELECT
    UUID(),
    u.id,
    CONCAT('T', LPAD((ROW_NUMBER() OVER (ORDER BY u.id)), 4, '0')),
    '副教授',
    '计算机科学系',
    NOW(),
    NOW()
FROM users u
WHERE u.role = 'teacher'
AND @is_development = 1;

-- 创建学生信息（仅开发环境）
INSERT INTO students (
    id,
    user_id,
    student_id,
    grade,
    class,
    major,
    enrollment_date,
    academic_status,
    created_at,
    updated_at
) SELECT
    UUID(),
    u.id,
    CONCAT(2024, LPAD((ROW_NUMBER() OVER (ORDER BY u.id)), 4, '0')),
    '2024',
    '1班',
    '计算机科学与技术',
    DATE('2024-09-01'),
    'enrolled',
    NOW(),
    NOW()
FROM users u
WHERE u.role = 'student'
AND @is_development = 1;

-- 创建示例课程（仅开发环境）
INSERT INTO courses (
    id,
    course_code,
    name,
    description,
    credits,
    hours_per_week,
    course_type,
    semester,
    max_students,
    current_students,
    status,
    teacher_id,
    created_at,
    updated_at
) VALUES
(
    UUID(),
    'CS101',
    '计算机科学导论',
    '计算机科学的基础入门课程，涵盖计算机的基本概念、编程基础和信息系统概论。',
    3.0,
    3,
    'required',
    '2024秋季',
    50,
    0,
    'active',
    (SELECT id FROM users WHERE username = 'teacher01' LIMIT 1),
    NOW(),
    NOW()
)
WHERE @is_development = 1;

-- 创建示例消息模板
INSERT INTO message_templates (
    id,
    name,
    title_template,
    content_template,
    type,
    variables,
    is_active,
    created_by,
    created_at,
    updated_at
) VALUES
(
    UUID(),
    '欢迎新用户',
    '欢迎加入{system_name}',
    '亲爱的{first_name}{last_name}，欢迎加入{system_name}！\n\n您的账户已成功创建：\n用户名：{username}\n邮箱：{email}\n\n请妥善保管您的登录信息，如有任何问题，请联系管理员。\n\n祝您使用愉快！',
    'system',
    JSON_OBJECT(
        'system_name', '系统名称',
        'first_name', '用户名',
        'last_name', '姓名',
        'username', '用户名',
        'email', '邮箱'
    ),
    TRUE,
    @admin_user_id,
    NOW(),
    NOW()
);

-- 创建消息通知模板
INSERT INTO message_templates (
    id,
    name,
    title_template,
    content_template,
    type,
    variables,
    is_active,
    created_by,
    created_at,
    updated_at
) VALUES
(
    UUID(),
    '成绩发布通知',
    '成绩发布通知',
    '尊敬的{student_name}同学，\n\n您的{course_name}课程{exam_type}成绩已经发布：\n\n成绩：{score}分\n（满分：{max_score}分）\n\n请登录系统查看详情。',
    'notification',
    JSON_OBJECT(
        'student_name', '学生姓名',
        'course_name', '课程名称',
        'exam_type', '考试类型',
        'score', '成绩',
        'max_score', '满分'
    ),
    TRUE,
    @admin_user_id,
    NOW(),
    NOW()
);

-- ========================================
-- 输出种子数据创建完成信息
-- ========================================

SELECT 'Seed data creation completed!' as status,
       (SELECT COUNT(*) FROM users) as total_users,
       (SELECT COUNT(*) FROM users WHERE role = 'admin') as admin_users,
       (SELECT COUNT(*) FROM users WHERE role = 'teacher') as teacher_users,
       (SELECT COUNT(*) FROM users WHERE role = 'student') as student_users,
       (SELECT COUNT(*) FROM courses) as courses,
       NOW() as completion_time
FROM dual;