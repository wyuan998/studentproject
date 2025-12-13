-- ========================================
-- 示例数据种子脚本
-- 用于开发和测试环境
-- ========================================

-- 检查是否为开发环境
SET @is_development = (SELECT @@version LIKE '%dev%' OR @@hostname LIKE '%dev%');

-- 仅在开发环境执行
-- 生产环境会自动跳过
SET @execute_sample_data = IF(@is_development = 1, 1, 0);

-- ========================================
-- 创建示例用户
-- ========================================

-- 批量创建教师
INSERT INTO users (id, username, email, password_hash, role, status, email_verified, created_at, updated_at)
SELECT
    UUID(),
    CONCAT('teacher', LPAD(num, 2, '0')),
    CONCAT('teacher', LPAD(num, 2, '0'), '@example.com'),
    '$2b$12$YourHashedPasswordHere',  -- 实际部署时需要使用正确哈希
    'teacher',
    'active',
    TRUE,
    NOW(),
    NOW()
FROM (
    SELECT 1 AS num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) AS teacher_numbers
WHERE @execute_sample_data = 1;

-- 批量创建学生
INSERT INTO users (id, username, email, password_hash, role, status, email_verified, created_at, updated_at)
SELECT
    UUID(),
    CONCAT('student', LPAD(num, 3, '0')),
    CONCAT('student', LPAD(num, 3, '0'), '@example.com'),
    '$2b$12$YourHashedPasswordHere',  -- 实际部署时需要使用正确哈希
    'student',
    'active',
    TRUE,
    NOW(),
    NOW()
FROM (
    SELECT 1 AS num UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
) AS student_numbers
WHERE @execute_sample_data = 1;

-- ========================================
-- 创建用户资料
-- ========================================

-- 教师资料
INSERT INTO user_profiles (id, user_id, first_name, last_name, phone, department, created_at, updated_at)
SELECT
    UUID(),
    u.id,
    CASE
        WHEN u.username = 'teacher01' THEN '张'
        WHEN u.username = 'teacher02' THEN '李'
        WHEN u.username = 'teacher03' THEN '王'
        WHEN u.username = 'teacher04' THEN '刘'
        WHEN u.username = 'teacher05' THEN '陈'
    END,
    CASE
        WHEN u.username = 'teacher01' THEN '伟'
        WHEN u.username = 'teacher02' THEN '明'
        WHEN u.username = 'teacher03' THEN '芳'
        WHEN u.username = 'teacher04' THEN '强'
        WHEN u.username = 'teacher05' THEN '敏'
    END,
    CONCAT('138', LPAD(ROW_NUMBER() OVER (ORDER BY u.id), 8, '0')),
    CASE
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 3) = 1 THEN '计算机科学系'
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 3) = 2 THEN '软件工程系'
        ELSE '信息工程系'
    END,
    NOW(),
    NOW()
FROM users u
WHERE u.role = 'teacher'
AND @execute_sample_data = 1;

-- 学生资料
INSERT INTO user_profiles (id, user_id, first_name, last_name, phone, birthday, gender, created_at, updated_at)
SELECT
    UUID(),
    u.id,
    CASE
        WHEN u.username = 'student001' THEN '张'
        WHEN u.username = 'student002' THEN '李'
        WHEN u.username = 'student003' THEN '王'
        WHEN u.username = 'student004' THEN '刘'
        WHEN u.username = 'student005' THEN '陈'
        WHEN u.username = 'student006' THEN '赵'
        WHEN u.username = 'student007' THEN '孙'
        WHEN u.username = 'student008' THEN '周'
        WHEN u.username = 'student009' THEN '吴'
        WHEN u.username = 'student010' THEN '郑'
    END,
    CASE
        WHEN u.username = 'student001' THEN '伟'
        WHEN u.username = 'student002' THEN '静'
        WHEN u.username = 'student003' THEN '强'
        WHEN u.username = 'student004' THEN '芳'
        WHEN u.username = 'student005' THEN '敏'
        WHEN u.username = 'student006' THEN '磊'
        WHEN u.username = 'student007' THEN '婷'
        WHEN u.username = 'student008' THEN '磊'
        WHEN u.username = 'student009' THEN '娜'
        WHEN u.username = 'student010' THEN '洋'
    END,
    CONCAT('139', LPAD(ROW_NUMBER() OVER (ORDER BY u.id), 8, '0')),
    CASE
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 4) = 0 THEN DATE('2004-03-15')
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 4) = 1 THEN DATE('2004-05-20')
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 4) = 2 THEN DATE('2004-08-10')
        ELSE DATE('2004-11-25')
    END,
    CASE
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 2) = 0 THEN 'male'
        ELSE 'female'
    END,
    NOW(),
    NOW()
FROM users u
WHERE u.role = 'student'
AND @execute_sample_data = 1;

-- ========================================
-- 创建教师和学生记录
-- ========================================

-- 创建教师记录
INSERT INTO teachers (id, user_id, teacher_id, title, department, office, specialization, hire_date, status, created_at, updated_at)
SELECT
    UUID(),
    u.id,
    CONCAT('T', LPAD(ROW_NUMBER() OVER (ORDER BY u.id), 4, '0')),
    CASE
        WHEN ROW_NUMBER() OVER (ORDER BY u.id) <= 2 THEN '教授'
        WHEN ROW_NUMBER() OVER (ORDER BY u.id) <= 4 THEN '副教授'
        ELSE '讲师'
    END,
    CASE
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 3) = 1 THEN '计算机科学系'
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 3) = 2 THEN '软件工程系'
        ELSE '信息工程系'
    END,
    CONCAT('教学楼', LPAD(ROW_NUMBER() OVER (ORDER BY u.id), 3, '0'), '室'),
    CASE
        WHEN ROW_NUMBER() OVER (ORDER BY u.id) = 1 THEN '人工智能,机器学习'
        WHEN ROW_NUMBER() OVER (ORDER BY u.id) = 2 THEN '数据库系统,数据仓库'
        WHEN ROW_NUMBER() OVER (ORDER BY u.id) = 3 THEN '软件工程,项目管理'
        WHEN ROW_NUMBER() OVER (ORDER BY u.id) = 4 THEN '网络安全,密码学'
        ELSE 'Web开发,前端框架'
    END,
    DATE('2020-09-01'),
    'active',
    NOW(),
    NOW()
FROM users u
WHERE u.role = 'teacher'
AND @execute_sample_data = 1;

-- 创建学生记录
INSERT INTO students (id, user_id, student_id, grade, class, major, enrollment_date, academic_status, gpa, credits_earned, created_at, updated_at)
SELECT
    UUID(),
    u.id,
    CONCAT(2024, LPAD(ROW_NUMBER() OVER (ORDER BY u.id), 4, '0')),
    '2024',
    CONCAT('计算机', LPAD((ROW_NUMBER() OVER (ORDER BY u.id) + 2) % 3 + 1), '班'),
    CASE
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 5) = 1 THEN '计算机科学与技术'
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 5) = 2 THEN '软件工程'
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 5) = 3 THEN '网络工程'
        WHEN MOD(ROW_NUMBER() OVER (ORDER BY u.id), 5) = 4 THEN '信息安全'
        ELSE '人工智能'
    END,
    DATE('2024-09-01'),
    'enrolled',
    ROUND(3.0 + (RAND() * 0.8), 2),
    ROUND(30 + (RAND() * 40), 2),
    NOW(),
    NOW()
FROM users u
WHERE u.role = 'student'
AND @execute_sample_data = 1;

-- ========================================
-- 创建示例课程
-- ========================================

INSERT INTO courses (
    id, course_code, name, description, credits, hours_per_week,
    course_type, semester, max_students, status,
    created_at, updated_at
) VALUES
(
    UUID(),
    'CS101', '计算机科学导论',
    '计算机科学的基础课程，涵盖计算机系统、编程基础和算法基础',
    3.0, 3, 'required', '2024秋季', 50, 'active',
    NOW(), NOW()
),
(
    UUID(),
    'CS102', '程序设计基础',
    '学习C语言程序设计的基本概念、语法和编程技巧',
    4.0, 4, 'required', '2024秋季', 40, 'active',
    NOW(), NOW()
),
(
    UUID(),
    'CS201', '数据结构与算法',
    '学习常用的数据结构和算法，提高程序设计能力',
    4.0, 4, 'required', '2024春季', 35, 'active',
    NOW(), NOW()
),
(
    UUID(),
    'CS202', '数据库系统',
    '学习数据库原理、SQL语言和数据库设计',
    3.0, 3, 'required', '2024春季', 45, 'active',
    NOW(), NOW()
),
(
    UUID(),
    'CS301', '操作系统',
    '学习操作系统的基本原理和设计方法',
    4.0, 4, 'required', '2024秋季', 30, 'active',
    NOW(), NOW()
),
(
    UUID(),
    'CS302', '计算机网络',
    '学习计算机网络协议、网络编程和网络安全',
    3.0, 3, 'required', '2024秋季', 40, 'active',
    NOW(), NOW()
),
(
    UUID(),
    'CS303', '软件工程',
    '学习软件开发方法论、项目管理和质量保证',
    3.0, 3, 'required', '2024春季', 35, 'active',
    NOW(), NOW()
),
(
    UUID(),
    'CS401', '人工智能导论',
    '介绍人工智能的基本概念、方法和应用',
    3.0, 3, 'elective', '2024秋季', 25, 'active',
    NOW(), NOW()
)
WHERE @execute_sample_data = 1;

-- 更新课程的授课教师
UPDATE courses
SET teacher_id = (SELECT id FROM users WHERE username = 'teacher01' LIMIT 1)
WHERE course_code IN ('CS101', 'CS102')
AND @execute_sample_data = 1;

UPDATE courses
SET teacher_id = (SELECT id FROM users WHERE username = 'teacher02' LIMIT 1)
WHERE course_code IN ('CS201', 'CS202')
AND @execute_sample_data = 1;

UPDATE courses
SET teacher_id = (SELECT id FROM users WHERE username = 'teacher03' LIMIT 1)
WHERE course_code IN ('CS301', 'CS302')
AND @execute_sample_data = 1;

UPDATE courses
SET teacher_id = (SELECT id FROM users WHERE username = 'teacher04' LIMIT 1)
WHERE course_code IN ('CS303', 'CS401')
AND @execute_sample_data = 1;

-- ========================================
-- 创建选课记录
-- ========================================

INSERT INTO enrollments (id, student_id, course_id, semester, enrollment_date, status, created_at, updated_at)
SELECT
    UUID(),
    s.id,
    c.id,
    '2024秋季',
    NOW(),
    'enrolled',
    NOW(),
    NOW()
FROM students s
CROSS JOIN courses c
WHERE c.status = 'active'
AND c.semester = '2024秋季'
AND s.grade = '2024'
AND @execute_sample_data = 1;

-- 更新课程选课人数
UPDATE courses
SET current_students = (
    SELECT COUNT(*)
    FROM enrollments e
    JOIN students s ON e.student_id = s.id
    WHERE e.course_id = courses.id
    AND e.status = 'enrolled'
)
WHERE @execute_sample_data = 1;

-- ========================================
-- 创建示例成绩
-- ========================================

INSERT INTO grades (
    id, student_id, course_id, score, semester, exam_type,
    max_score, weight, graded_by, graded_at, comments,
    created_at, updated_at
) SELECT
    UUID(),
    e.student_id,
    e.course_id,
    ROUND(60 + RAND() * 35, 2),  -- 60-95分
    '2024秋季',
    'midterm',
    100,
    0.3,
    c.teacher_id,
    NOW(),
    '期中考试成绩',
    NOW(),
    NOW()
FROM enrollments e
JOIN courses c ON e.course_id = c.id
WHERE e.status = 'enrolled'
AND e.semester = '2024秋季'
AND @execute_sample_data = 1;

-- 期末成绩
INSERT INTO grades (
    id, student_id, course_id, score, semester, exam_type,
    max_score, weight, graded_by, graded_at, comments,
    created_at, updated_at
) SELECT
    UUID(),
    e.student_id,
    e.course_id,
    ROUND(65 + RAND() * 30, 2),  -- 65-95分
    '2024秋季',
    'final',
    100,
    0.7,
    c.teacher_id,
    NOW(),
    '期末考试成绩',
    NOW(),
    NOW()
FROM enrollments e
JOIN courses c ON e.course_id = c.id
WHERE e.status = 'enrolled'
AND e.semester = '2024秋季'
AND @execute_sample_data = 1;

-- 作业成绩
INSERT INTO grades (
    id, student_id, course_id, score, semester, exam_type,
    max_score, weight, graded_by, graded_at, comments,
    created_at, updated_at
) SELECT
    UUID(),
    e.student_id,
    e.course_id,
    ROUND(80 + RAND() * 20, 2),  -- 80-100分
    '2024秋季',
    'assignment',
    100,
    0.5,
    c.teacher_id,
    NOW(),
    '作业成绩',
    NOW(),
    NOW()
FROM enrollments e
JOIN courses c ON e.course_id = c.id
WHERE e.status = 'enrolled'
AND e.semester = '2024秋季'
AND RAND() > 0.5  -- 50%的学生有作业成绩
AND @execute_sample_data = 1;

-- ========================================
-- 创建示例消息
-- ========================================

-- 系统通知消息
INSERT INTO messages (
    id, sender_id, receiver_id, title, content, type, status,
    priority, sent_at, read_at, created_at, updated_at
) SELECT
    UUID(),
    (SELECT id FROM users WHERE username = 'admin' LIMIT 1),
    u.id,
    '欢迎加入学生信息管理系统',
    '欢迎您使用学生信息管理系统！请熟悉系统功能，如有问题请联系管理员。',
    'system',
    'read',
    'normal',
    DATE_SUB(NOW(), INTERVAL 30 DAY),  -- 30天前发送
    DATE_SUB(NOW(), INTERVAL 25 DAY),  -- 5天前阅读
    DATE_SUB(NOW(), INTERVAL 30 DAY),
    DATE_SUB(NOW(), INTERVAL 30 DAY)
FROM users u
WHERE u.role IN ('teacher', 'student')
AND @execute_sample_data = 1;

-- 业务通知消息
INSERT INTO messages (
    id, sender_id, receiver_id, title, content, type, status,
    priority, sent_at, created_at, updated_at
) VALUES
(
    UUID(),
    (SELECT id FROM users WHERE username = 'teacher01' LIMIT 1),
    (SELECT id FROM users WHERE username = 'student001' LIMIT 1),
    'CS101期中考试安排通知',
    'CS101课程的期中考试将于下周三下午2点在教A301举行，请准时参加。',
    'business',
    'unread',
    'high',
    NOW(),
    NOW(),
    NOW()
)
WHERE @execute_sample_data = 1;

-- ========================================
-- 输出创建完成统计
-- ========================================

SELECT 'Sample data creation completed!' as status,
       (SELECT COUNT(*) FROM users) as total_users,
       (SELECT COUNT(*) FROM users WHERE role = 'admin') as admin_users,
       (SELECT COUNT(*) FROM users WHERE role = 'teacher') as teacher_users,
       (SELECT COUNT(*) FROM users WHERE role = 'student') as student_users,
       (SELECT COUNT(*) FROM courses) as courses,
       (SELECT COUNT(*) FROM enrollments) as enrollments,
       (SELECT COUNT(*) FROM grades) as grades,
       (SELECT COUNT(*) FROM messages) as messages,
       NOW() as completion_time
FROM dual
WHERE @execute_sample_data = 1;