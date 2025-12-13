#!/bin/bash

# ========================================
# 学生信息管理系统数据库初始化脚本
# 用途: 初始化数据库环境、创建表结构、插入种子数据
# 使用方法: ./setup.sh [环境]
# 环境参数: dev, test, prod
# ========================================

set -e

# 配置变量
ENVIRONMENT=${1:-dev}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-student_management}
DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查MySQL是否安装
check_mysql() {
    if ! command -v mysql &> /dev/null; then
        log_error "MySQL未安装，请先安装MySQL"
        exit 1
    fi

    if ! mysqladmin ping -h$DB_HOST -P$DB_PORT --silent 2>/dev/null; then
        log_error "MySQL服务未运行，请先启动MySQL服务"
        exit 1
    fi
}

# 检查数据库是否存在
check_database() {
    if mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "USE $DB_NAME" 2>/dev/null; then
        log_warn "数据库 $DB_NAME 已存在"
        return 0
    else
        log "数据库 $DB_NAME 不存在，将创建"
        return 1
    fi
}

# 创建数据库
create_database() {
    log "创建数据库: $DB_NAME"
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

    if [ $? -eq 0 ]; then
        log "数据库创建成功"
    else
        log_error "数据库创建失败"
        exit 1
    fi
}

# 执行初始化SQL
execute_init_sql() {
    local init_file="init.sql"

    if [ ! -f "$init_file" ]; then
        log_error "初始化文件 $init_file 不存在"
        exit 1
    fi

    log "执行数据库初始化脚本..."
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME < "$init_file"

    if [ $? -eq 0 ]; then
        log "数据库初始化完成"
    else
        log_error "数据库初始化失败"
        exit 1
    fi
}

# 执行种子数据
execute_seeds() {
    local seed_dir="seeds"
    local seed_admin="$seed_dir/seed_admin.sql"
    local seed_sample="$seed_dir/seed_sample_data.sql"

    # 执行管理员种子数据
    if [ -f "$seed_admin" ]; then
        log "执行管理员种子数据..."
        mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME < "$seed_admin"

        if [ $? -eq 0 ]; then
            log "管理员种子数据执行完成"
        else
            log_warn "管理员种子数据执行失败"
        fi
    fi

    # 仅在开发和测试环境执行示例数据
    if [ "$ENVIRONMENT" != "prod" ] && [ -f "$seed_sample" ]; then
        log "执行示例种子数据..."
        mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME < "$seed_sample"

        if [ $? -eq 0 ]; then
            log "示例种子数据执行完成"
        else
            log_warn "示例种子数据执行失败"
        fi
    fi
}

# 验证安装
verify_installation() {
    log "验证数据库安装..."

    # 检查表数量
    local table_count=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME'" 2>/dev/null | tail -1)

    if [ "$table_count" -ge 11 ]; then
        log "表创建验证通过 ($table_count 个表)"
    else
        log_error "表创建验证失败 (只有 $table_count 个表)"
        exit 1
    fi

    # 检查基础数据
    local admin_count=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -N -e "SELECT COUNT(*) FROM users WHERE role = 'admin'" $DB_NAME 2>/dev/null | tail -1)

    if [ "$admin_count" -ge 1 ]; then
        log "管理员用户创建验证通过 ($admin_count 个)"
    else
        log_error "管理员用户创建验证失败"
        exit 1
    fi

    # 显示数据统计
    log "数据库统计信息:"
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "
        SELECT
            '用户总数' as item,
            COUNT(*) as count
        FROM users $DB_NAME

        UNION ALL

        SELECT
            '学生数',
            COUNT(*)
        FROM students $DB_NAME

        UNION ALL

        SELECT
            '教师数',
            COUNT(*)
        FROM teachers $DB_NAME

        UNION ALL

        SELECT
            '课程数',
            COUNT(*)
        FROM courses $DB_NAME

        UNION ALL

        SELECT
            '选课数',
            COUNT(*)
        FROM enrollments $DB_NAME
    " 2>/dev/null

    log "数据库安装验证完成!"
}

# 创建备份目录
create_backup_dir() {
    local backup_dir="../../backups/database"
    mkdir -p "$backup_dir"

    # 备份初始化SQL
    if [ -f "init.sql" ]; then
        local backup_file="$backup_dir/init_$(date +%Y%m%d_%H%M%S).sql"
        cp "init.sql" "$backup_file"
        log "已备份初始化SQL到 $backup_file"
    fi
}

# 主函数
main() {
    log "开始初始化学生信息管理系统数据库..."
    log "环境: $ENVIRONMENT"
    log "数据库主机: $DB_HOST:$DB_PORT"

    # 检查MySQL
    check_mysql

    # 检查并创建数据库
    if check_database; then
        log "使用现有数据库"
    else
        create_database
    fi

    # 执行初始化
    execute_init_sql

    # 执行种子数据
    execute_seeds

    # 验证安装
    verify_installation

    # 创建备份
    create_backup_dir

    # 显示连接信息
    log ""
    log "数据库连接信息:"
    log "  主机: $DB_HOST"
    log "  端口: $DB_PORT"
    log "  数据库: $DB_NAME"
    log "  用户: $DB_USER"
    log ""
    log "初始化完成！可以使用以下命令连接数据库："
    log "mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_NAME"

    # 根据环境显示额外信息
    if [ "$ENVIRONMENT" = "dev" ]; then
        log ""
        log "开发环境默认账户:"
        log "  管理员: admin / 123456"
        log "  注意: 生产环境请立即修改默认密码！"
    fi
}

# 执行主函数
main "$@" 2>&1 | tee -a setup.log

exit 0