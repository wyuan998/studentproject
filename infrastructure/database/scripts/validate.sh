#!/bin/bash

# ========================================
# 学生信息管理系统数据库验证脚本
# 用途: 验证数据库的完整性、性能和安全
# 使用方法: ./validate.sh [检查类型]
# 检查类型: integrity, performance, security, all
# ========================================

set -e

# 配置变量
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-student_management}
DB_USER=${DB_USER:-readonly}
DB_PASSWORD=${DB_PASSWORD:-sms_readonly_2024}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# 检查数据库连接
check_connection() {
    if ! mysqladmin ping -h$DB_HOST -P$DB_PORT --silent 2>/dev/null; then
        log_error "无法连接到数据库 ($DB_HOST:$DB_PORT)"
        exit 1
    fi

    if ! mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "USE $DB_NAME" 2>/dev/null; then
        log_error "无法访问数据库 $DB_NAME"
        exit 1
    fi
}

# 检查数据完整性
check_integrity() {
    log "=== 数据完整性检查 ==="

    local errors=0

    # 检查表结构完整性
    log "检查表结构完整性..."

    local expected_tables=(
        "users"
        "user_profiles"
        "students"
        "teachers"
        "admins"
        "courses"
        "enrollments"
        "grades"
        "messages"
        "message_templates"
        "audit_logs"
        "system_configs"
    )

    for table in "${expected_tables[@]}"; do
        if ! mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "DESCRIBE $table" $DB_NAME >/dev/null 2>&1; then
            log_error "  缺少表: $table"
            ((errors++))
        else
            log "  表 $table 存在 ✓"
        fi
    done

    # 检查外键完整性
    log "检查外键完整性..."
    local fk_count=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema = '$DB_NAME' AND constraint_type = 'FOREIGN KEY'" $DB_NAME 2>/dev/null | tail -1)
    log "  外键约束数量: $fk_count"

    # 检查唯一索引
    log "检查唯一索引完整性..."
    local uk_count=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = '$DB_NAME' AND non_unique = 0 AND index_name LIKE '%uk_%'" $DB_NAME 2>/dev/null | tail -1)
    log "  唯一索引数量: $uk_count"

    # 检查数据一致性
    log "检查数据一致性..."

    # 检查用户资料完整性
    local missing_profiles=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM users u
        LEFT JOIN user_profiles up ON u.id = up.user_id
        WHERE up.user_id IS NULL
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$missing_profiles" -gt 0 ]; then
        log_error "  有 $missing_profiles 个用户没有资料记录"
        ((errors++))
    else
        log "  所有用户都有资料记录 ✓"
    fi

    # 检查学生用户关联
    local orphaned_students=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM students s
        LEFT JOIN users u ON s.user_id = u.id
        WHERE u.id IS NULL
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$orphaned_students" -gt 0 ]; then
        log_error "  有 $orphaned_students 个学生记录没有关联用户"
        ((errors++))
    else
        log "  所有学生都关联到用户 ✓"
    fi

    # 检查课程学生人数
    local invalid_enrollments=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM enrollments e
        LEFT JOIN students s ON e.student_id = s.id
        LEFT JOIN courses c ON e.course_id = c.id
        WHERE s.id IS NULL OR c.id IS NULL
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$invalid_enrollments" -gt 0 ]; then
        log_error "  有 $invalid_enrollments 条选课记录关联了不存在的学生或课程"
        ((errors++))
    else
        log "  所有选课记录都有效 ✓"
    fi

    # 检查成绩记录
    local invalid_grades=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM grades g
        LEFT JOIN students s ON g.student_id = s.id
        LEFT JOIN courses c ON g.course_id = c.id
        WHERE s.id IS NULL OR c.id IS NULL
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$invalid_grades" -gt 0 ]; then
        log_error "  有 $invalid_grades 条成绩记录关联了不存在的学生或课程"
        ((errors++))
    else
        log "  所有成绩记录都有效 ✓"
    fi

    # 检查消息关联
    local invalid_messages=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM messages m
        LEFT JOIN users s ON m.sender_id = s.id
        LEFT JOIN users r ON m.receiver_id = r.id
        WHERE s.id IS NULL OR r.id IS NULL
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$invalid_messages" -gt 0 ]; then
        log_error "  有 $invalid_messages 条消息关联了不存在的用户"
        ((errors++))
    else
        log "  所有消息都有效 ✓"
    fi

    # 检查数据值范围
    log "检查数据值范围..."
    local out_of_range=0

    # 检查成绩范围
    local out_of_range_grades=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM grades
        WHERE score < 0 OR score > 100
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$out_of_range_grades" -gt 0 ]; then
        log_error "  有 $out_of_range_grades 条记录的成绩超出范围(0-100)"
        ((out_of_range++))
    fi

    # 检查学分范围
    local out_of_range_credits=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM courses
        WHERE credits < 0 OR credits > 10
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$out_of_range_credits" -gt 0 ]; then
        log_error "  有 $out_of_range_credits 个课程的学分超出范围(0-10)"
        ((out_of_range++))
    fi

    # 检查GPA范围
    local out_of_range_gpa=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM students
        WHERE gpa IS NOT NULL AND (gpa < 0 OR gpa > 4.0)
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$out_of_range_gpa" -gt 0 ]; then
        log_error "  有 $out_of_range_gpa 个学生的GPA超出范围(0.0-4.0)"
        ((out_of_range++))
    fi

    if [ $((errors + out_of_range)) -gt 0 ]; then
        log_error "数据完整性检查发现问题，请查看上述错误"
        return 1
    else
        log "数据完整性检查通过 ✓"
        return 0
    fi
}

# 检查性能
check_performance() {
    log "=== 性能检查 ==="

    # 检查表大小
    log "检查表大小..."
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT
            table_name AS '表名',
            ROUND(((data_length + index_length) / 1024 / 1024), 2) AS '大小(MB)',
            table_rows AS '行数',
            ROUND(data_length / 1024 / 1024, 2) AS '数据大小(MB)',
            ROUND(index_length / 1024 / 1024, 2) AS '索引大小(MB)'
        FROM information_schema.tables
        WHERE table_schema = '$DB_NAME'
        ORDER BY (data_length + index_length) DESC
    " $DB_NAME 2>/dev/null

    # 检查索引使用情况
    log "检查索引使用情况..."
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT
            table_name AS '表名',
            index_name AS '索引名',
            cardinality AS '基数',
            CASE
                WHEN sub_part IS NOT NULL THEN '部分索引'
                WHEN non_unique = 0 THEN '唯一索引'
                ELSE '普通索引'
            END AS '索引类型',
            CASE
                WHEN cardinality / table_rows < 0.1 THEN '选择性低'
                WHEN cardinality / table_rows < 0.5 THEN '选择性中'
                ELSE '选择性高'
            END AS '选择性'
        FROM information_schema.statistics s
        JOIN information_schema.tables t ON s.table_schema = t.table_name AND s.table_name = t.table_name
        WHERE s.table_schema = '$DB_NAME'
        AND s.index_name != 'PRIMARY'
        ORDER BY table_name, seq_in_index
    " $DB_NAME 2>/dev/null

    # 检查慢查询（如果启用了慢查询日志）
    if [ -d "/var/log/mysql" ] && [ -f "/var/log/mysql/mysql-slow.log" ]; then
        log "检查慢查询日志（最近24小时）"
        local slow_queries=$(mktemp)
        grep "$(date -d '1 day ago' '+%Y-%m-%d %H:%M:%S')" /var/log/mysql/mysql-slow.log | wc -l)

        if [ "$slow_queries" -gt 0 ]; then
            log_warn "  发现 $slow_queries 个慢查询（最近24小时）"
            echo
            grep "$(date -d '1 day ago' '+%Y-%m-%d %H:%M:%S')" /var/log/mysql/mysql-s.log | tail -20
        else
            log "  没有慢查询记录"
        fi
    fi

    # 检查表统计信息
    log "检查表统计信息..."
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT
            '表名' as name,
            ROUND(AVG_ROW_LENGTH, 2) as '平均行长度',
            ROUND(DATA_LENGTH / 1024 / 1024, 2) as '数据大小(MB)',
            ROUND(INDEX_LENGTH / 1024 / 1024, 2) as '索引大小(MB)',
            ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) as '总大小(MB)',
            TABLE_ROWS as '行数',
            ROUND(DATA_FREE / (DATA_LENGTH + INDEX_LENGTH) * 100, 2) as '碎片率(%)'
        FROM information_schema.TABLES
        WHERE table_schema = '$DB_NAME'
        AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC
    " $DB_NAME 2>/dev/null
}

# 检查安全性
check_security() {
    log "=== 安全检查 ==="

    # 检查用户权限
    log "检查用户权限..."
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT user, host, Select_priv, Insert_priv, Update_priv, Delete_priv
        FROM mysql.user
        WHERE user IN ('root', '$DB_USER')
    " 2>/dev/null

    # 检查是否有弱密码用户
    log "检查默认密码或弱密码用户..."
    local weak_passwords=$(mysql -h$DB_HOST -p$DB_PORT -u $DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM mysql.user
        WHERE authentication_string IN ('password', '123456', 'root', 'admin', 'test')
        OR LENGTH(password) < 8
        OR password = ''
    " 2>/dev/null | tail -1)

    if [ "$weak_passwords" -gt 0 ]; then
        log_error "  发现 $weak_passwords 个弱密码用户"
        log_error "  建议立即修改弱密码"
    else
        log "  未发现明显的弱密码用户 ✓"
    fi

    # 检查数据库权限
    log "检查数据库权限..."
    local db_privileges=$(mysql -h$DB_HOST -p$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT SHOW GRANTS FOR CURRENT_USER
    " 2>/dev/null)

    log "  当前用户权限:"
    echo "$db_privileges"

    # 检查敏感数据
    log "检查敏感数据保护..."

    # 检查明文密码存储
    local plaintext_passwords=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = '$DB_NAME'
        AND column_name LIKE '%password%'
        AND column_name != 'password_hash'
    " 2>/dev/null | tail -1)

    if [ "$plaintext_passwords" -gt 0 ]; then
        log_error "  发现 $plaintext_passwords 个可能的明文密码字段"
    else
        log "  未发现明文密码存储 ✓"
    fi

    # 检查是否有必要的权限控制
    local missing_acl=0

    # 检查是否有超级管理员
    local super_admins=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM admins WHERE is_super_admin = 1
    " $DB_NAME 2>/dev/null | tail -1)

    if [ "$super_admins" -eq 0 ]; then
        log_warn "  未发现超级管理员账户"
        ((missing_acl++))
    else
        log "  发现 $super_admins 个超级管理员账户"
    fi

    # 检查审计日志是否启用
    local audit_logs_exist=$(mysql -h$DB_HOST -P$DB_PORT -u $DB_USER -p$DB_PASSWORD -e "
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = '$DB_NAME'
        AND table_name = 'audit_logs'
    " 2>/dev/null | tail -1)

    if [ "$audit_logs_exist" -eq 0 ]; then
        log_warn "  未找到审计日志表"
        ((missing_acl++))
    else
        log "  审计日志表已启用 ✓"
    fi

    if [ $((missing_acl)) -gt 0 ]; then
        log_error "安全检查发现权限控制问题"
        return 1
    else
        log "安全检查通过 ✓"
        return 0
    fi
}

# 生成报告
generate_report() {
    local report_file="validation_report_$(date +%Y%m%d_%H%M%S).html"

    log "生成验证报告..."

    cat > "$report_file" << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据库验证报告 - $(date +'%Y-%m-%d %H:%M:%S')</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .section {
            margin-bottom: 30px;
            padding: 15px;
            border-left: 4px solid #007bff;
            background: #f8f9fa;
        }
        .error {
            color: #721c24;
            border-left-color: #f44336;
            background: #fdf2f2;
        }
        .success {
            color: #155724;
            border-left-color: #28a745;
            background: #f0fff0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            color: #6c757d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>学生信息管理系统 - 数据库验证报告</h1>
        <p style="color: #666; margin-bottom: 20px;">
            报告时间: $(date +'%Y-%m-%d %H:%M:%S')<br>
            数据库: $DB_NAME ($DB_HOST:$DB_PORT)
        </p>

EOF

    # 添加完整性检查结果
    echo '<div class="section">' >> "$report_file"
    if [ "${1:-all}" == "all" ] || [ "${1:-all}" == "integrity" ]; then
        echo '<h2>数据完整性</h2>' >> "$report_file"

        integrity_errors=$(check_integrity 2>&1 || true)
        if [ $integrity_errors -eq 0 ]; then
            echo '<div class="success">数据完整性检查通过 ✓</div>' >> "$report_file"
        else
            echo '<div class="error">数据完整性检查失败！</div>' >> "$report_file"
        fi
    fi
    echo '</div>' >> "$report_file"

    # 添加性能检查结果
    if [ "${1:-all}" == "all" ] || [ "${1:-all}" == "performance" ]; then
        echo '<div class="section">' >> "$report_file"
        echo '<h2>性能检查</h2>' >> "$report_file"
        check_performance >> "$report_file" 2>&1 || true
        echo '</div>' >> "$report_file"
    fi

    # 添加安全检查结果
    if [ "${1:-all}" == "all" ] || [ "${1:-all}" == "security" ]; then
        echo '<div class="section">' >> "$report_file"
        echo '<h2>安全检查</h2>' >> "$report_file"
        security_errors=$(check_security 2>&1 || true)
        if [ $security_errors -eq 0 ]; then
            echo '<div class="success">安全检查通过 ✓</div>' >> "$report_file"
        else
            echo '<div class="error">安全检查发现隐患！</div>' >> "$report_file"
        fi
        echo '</div>' >> "$report_file"
    fi

    # 添加数据库统计
    echo '<div class="section">' >> "$report_file"
    echo '<h2>数据库统计</h2>' >> "$report_file"
    echo '<div class="stats">' >> "$report_file"

    # 用户统计
    echo '<div class="stat-card">' >> "$report_file"
    local total_users=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM users" $DB_NAME 2>/dev/null | tail -1)
    echo '<div class="stat-value">' >> "$report_file"
    echo "$total_users" >> "$report_file"
    echo '</div>' >> "$report_file"
    echo '<div class="stat-label">用户总数</div>' >> "$file"_" >> "$report_file"
    echo '</div>' >> "$report_file"

    # 数据统计
    local student_count=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM students" $DB_NAME 2>/dev/null | tail -1)
    echo '<div class="stat-card">' >> "$report_file"
    echo '<div class="stat-value">' >> "$report_file"
    echo "$student_count" >> "$report_file"
    echo '</div>' >> "$report_file"
    echo '<div class="stat-label">学生数</div>' >> "$file_" >> "$report_file"
    echo '</div>' >> "$report_file"

    # 课程统计
    local course_count=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM courses WHERE status = 'active'" $DB_NAME 2>/dev/null | tail -1)
    echo '<div class="stat-card">' >> "$report_file"
    echo '<div class="stat-value">' >> "$report_file"
    echo "$course_count" >> "$report_file"
    echo '</div>' >> "$report_file"
    echo '<div class="stat-label">活跃课程</div>' >> "$file_" >> "$report_file"
    echo '</div>' >> "$report_file"

    # 消息统计
    local message_count=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM messages WHERE status = 'unread'" $DB_NAME 2>/dev/null | tail -1)
    echo '<div class="stat-card">' >> "$report_file"
    echo '<div class="stat-value">' >> "$report_file"
    echo "$message_count" >> "$report_file"
    echo '</div>' >> "$report_file"
    echo '<div class="stat-label">未读消息</div>' >> "$file_" >> "$report_file"
    echo '</div>' >> "$report_file"

    echo '</div>' >> "$report_file"

    echo '</div>' >> "$report_file"
    echo '<footer style="margin-top: 30px; text-align: center; color: #666; font-size: 14px;">'
    echo '<p>报告由数据库验证脚本生成 | 生成时间: '$(date)</p>'
    echo '</footer>' >> "$report_file"

    echo '</body>' >> "$report_file"
    echo '</html>' >> "$report_file"

    log "验证报告已生成: $report_file"

    # 在浏览器中打开报告（如果可能）
    if command -v xdg-open &> /dev/null; then
        xdg-open "$report_file" 2>/dev/null &
    elif command -v open &> /dev/null; then
        open "$report_file" 2>/dev/null &
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
学生信息管理系统数据库验证脚本

用法: $0 [检查类型] [输出文件]

检查类型:
    integrity   - 检查数据完整性和一致性
    performance - 检查数据库性能和统计信息
    security   - 检查安全配置和权限设置
    all        - 执行所有检查项

输出文件:
    --output-file  - 指定HTML格式的报告文件（默认：自动生成带时间戳的文件）
    - 无此参数时，结果输出到控制台

环境变量:
    DB_HOST     - 数据库主机 (默认: localhost)
    DB_PORT     - 数据库端口 (默认: 3306)
    DB_NAME     - 数据库名称 (默认: student_management)
    DB_USER     - 验证用户 (默认: readonly)
    DB_PASSWORD - 验证用户密码 (默认: sms_readonly_2024)

示例:
    $0 integrity            # 检查数据完整性
    $0 performance           # 检查性能
    $0 security            # 检查安全性
    $0 all                 # 执行所有检查
    $0 all --output-file=report.html  # 生成HTML报告

EOF
}

# 主函数
main() {
    local check_type="${1:-all}"

    case "${check_type}" in
        "integrity")
            check_connection
            check_integrity
            ;;
        "performance")
            check_connection
            check_performance
            ;;
        "security")
            check_connection
            check_security
            ;;
        "all")
            check_connection
            generate_report
            ;;
        "help"|"--help"|"-h")
            show_help
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
}

# 解析命令行参数
while [ $# -gt 0 ]; do
    case "$1" in
        --output-file)
            REPORT_FILE="$2"
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

# 执行主函数
main "$check_type"

exit 0