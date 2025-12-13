#!/bin/bash

# ========================================
# 学生信息管理系统数据库备份脚本
# 用途: 自动备份数据库，支持全量和增量备份
# 使用方法: ./backup.sh [类型] [选项]
# 类型: full, incremental, restore
# 选项: --compress, --email, --clean
# ========================================

set -e

# 配置变量
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}
DB_NAME=${DB_NAME:-student_management}
DB_USER=${DB_USER:-backup}
DB_PASSWORD=${DB_PASSWORD:-backup_password_2024}
BACKUP_DIR=${BACKUP_DIR:-/backup/mysql/student_management}
RETENTION_DAYS=${RETENTION_DAYS:-30}
COMPRESS=${COMPRESS:-true}
EMAIL_NOTIFY=${EMAIL_NOTIFY:-false}
EMAIL_TO=${EMAIL_TO:-admin@example.com}

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

# 创建备份目录
create_backup_dir() {
    local backup_type=$1

    case $backup_type in
        "full")
            local dir="$BACKUP_DIR/full"
            ;;
        "incremental")
            local dir="$BACKUP_DIR/incremental"
            ;;
        *)
            log_error "未知的备份类型: $backup_type"
            return 1
            ;;
    esac

    mkdir -p "$dir"
    echo "$dir"
}

# 执行全量备份
backup_full() {
    local backup_file="$1"
    local filename=$(basename "$backup_file")
    local start_time=$(date +%s)

    log "开始全量备份..."
    log "备份文件: $filename"

    if [ "$COMPRESS" = true ]; then
        mysqldump \
            --host=$DB_HOST \
            --port=$DB_PORT \
            --user=$DB_USER \
            --password=$DB_PASSWORD \
            --single-transaction \
            --routines \
            --triggers \
            --events \
            --hex-blob \
            --master-data=2 \
            --flush-logs \
            --databases $DB_NAME | gzip > "$backup_file"
    else
        mysqldump \
            --host=$DB_HOST \
            --port=$DB_PORT \
            --user=$DB_USER \
            --password=$DB_PASSWORD \
            --single-transaction \
            --routines \
            --triggers \
            --events \
            --hex-blob \
            --master-data=2 \
            --flush-logs \
            --databases $DB_NAME > "$backup_file"
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 验证备份文件
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local file_size=$(du -h "$backup_file" | cut -f1)
        log "全量备份完成!"
        log "文件大小: $file_size"
        log "耗时: ${duration}秒"

        # 创建备份信息文件
        local info_file="${backup_file}.info"
        cat > "$info_file" << EOF
备份类型: 全量备份
备份时间: $(date)
备份文件: $filename
文件大小: $(du -h "$backup_file" | cut -f1)
耗时: ${duration}秒
数据库: $DB_NAME
MySQL版本: $(mysql -V | awk '{print $5}')
EOF

        # 发送邮件通知
        if [ "$EMAIL_NOTIFY" = "true" ]; then
            send_backup_notification "全量备份" "$filename" "$file_size" "$duration"
        fi

        return 0
    else
        log_error "备份文件不存在或为空: $backup_file"
        return 1
    fi
}

# 执行增量备份
backup_incremental() {
    local backup_dir=$1

    log "开始增量备份..."

    # 获取最后一个二进制日志文件
    local last_binlog=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SHOW MASTER STATUS;" 2>/dev/null | awk 'NR==2 {print $1}')

    if [ -z "$last_binlog" ]; then
        log_error "无法获取二进制日志信息"
        return 1
    fi

    log "当前二进制日志: $last_binlog"

    # 复制二进制日志
    mysqlbinlog \
        --read-from-remote-server \
        --host=$DB_HOST \
        --port=$DB_PORT \
        --user=$DB_USER \
        --password=$DB_PASSWORD \
        --raw \
        --stop-never \
        --result-file="$backup_dir/binlog_$last_binlog" \
        $last_binlog

    # 创建备份信息文件
    local info_file="$backup_dir/incremental_$(date +%Y%m%d_%H%M%S).info"
    cat > "$info_file" << EOF
备份类型: 增量备份
备份时间: $(date)
起始日志: $last_binlog
数据库: $DB_NAME
MySQL版本: $(mysql -V | awk '{print $5}')
EOF

    log "增量备份完成!"
    log "起始日志: $last_binlog"

    # 发送邮件通知
    if [ "$EMAIL_NOTIFY" = "true" ]; then
        send_backup_notification "增量备份" "二进制日志" "N/A"
    fi

    return 0
}

# 恢复数据库
restore_database() {
    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi

    local filename=$(basename "$backup_file")
    log "开始恢复数据库..."
    log "备份文件: $filename"

    # 确认恢复操作
    read -p "警告：恢复操作将清空现有数据库，是否继续？[y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "操作已取消"
        return 1
    fi

    # 删除现有数据库
    log "删除现有数据库..."
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "DROP DATABASE IF EXISTS $DB_NAME"

    # 创建空数据库
    log "创建空数据库..."
    mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

    # 执行恢复
    log "开始恢复数据..."
    local start_time=$(date +%s)

    if [[ "$backup_file" == *.gz ]]; then
        # 压缩文件
        gunzip < "$backup_file" | mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME
    else
        # 未压缩文件
        mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME < "$backup_file"
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [ $? -eq 0 ]; then
        log "数据库恢复完成!"
        log "耗时: ${duration}秒"

        # 发送邮件通知
        if [ "$EMAIL_NOTIFY" = "true" ]; then
            send_backup_notification "数据库恢复" "$filename" "N/A" "$duration"
        fi

        return 0
    else
        log_error "数据库恢复失败"
        return 1
    fi
}

# 清理旧备份
clean_old_backups() {
    log "清理 ${RETENTION_DAYS}天前的备份文件..."

    local deleted_count=0
    deleted_count=$(find "$BACKUP_DIR" -name "*.sql" -o -name "*.sql.gz" -o -name "*.info" -type f -mtime +${RETENTION_DAYS} -delete -print | wc -l)

    if [ "$deleted_count" -gt 0 ]; then
        log "已删除 $deleted_count 个旧备份文件"
    else
        log "没有需要清理的备份文件"
    fi
}

# 发送备份通知邮件
send_backup_notification() {
    local backup_type=$1
    local filename=$2
    local size=$3
    local duration=${4:-N/A}

    if [ -z "$EMAIL_TO" ]; then
        log_warn "未配置邮件接收地址，跳过邮件通知"
        return 0
    fi

    # 检查mail命令是否可用
    if ! command -v mail &> /dev/null; then
        log_warn "mail命令不可用，跳过邮件通知"
        return 0
    fi

    local subject="[学生信息管理系统] $backup_type通知"
    local body="备份操作已完成。

备份详情:
- 备份类型: $backup_type
- 备份文件: $filename
- 文件大小: $size
- 耗时: ${duration}秒
- 备份时间: $(date)
- 数据库: $DB_NAME

请及时验证备份完整性。

此邮件由系统自动发送。"

    echo -e "$body" | mail -s "$subject" "$EMAIL_TO"
    if [ $? -eq 0 ]; then
        log "邮件通知已发送至: $EMAIL_TO"
    else
        log_warn "邮件发送失败"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
学生信息管理系统数据库备份脚本

用法: $0 [类型] [选项]

类型:
    full        - 执行全量备份
    incremental - 执行增量备份
    restore     - 恢复数据库
    clean       - 清理旧备份
    help        - 显示此帮助信息

选项:
    --compress  - 压缩备份文件（默认开启）
    --no-compress - 不压缩备份文件
    --email     - 发送邮件通知
    --clean     - 备份后清理旧文件

环境变量:
    DB_HOST     - 数据库主机 (默认: localhost)
    DB_PORT     - 数据库端口 (默认: 3306)
    DB_NAME     - 数据库名称 (默认: student_management)
    DB_USER     - 备份用户 (默认: backup)
    DB_PASSWORD - 备份密码
    BACKUP_DIR   - 备份目录 (默认: /backup/mysql/student_management)
    RETENTION_DAYS - 保留天数 (默认: 30)
    EMAIL_TO     - 邮件接收地址
    COMPRESS     - 是否压缩 (默认: true)
    EMAIL_NOTIFY - 是否发送邮件 (默认: false)

示例:
    $0 full                    # 全量备份
    $0 full --email             # 全量备份并发送邮件
    $0 incremental              # 增量备份
    $0 restore backup.sql        # 从备份恢复
    $0 clean                   # 清理旧备份

EOF
}

# 检查MySQL连接
check_mysql_connection() {
    if ! mysqladmin ping -h$DB_HOST -P$DB_PORT --silent 2>/dev/null; then
        log_error "无法连接到MySQL服务器 ($DB_HOST:$DB_PORT)"
        log_error "请检查MySQL服务是否运行以及连接参数是否正确"
        exit 1
    fi
}

# 显示备份统计信息
show_backup_stats() {
    log "备份目录统计:"
    echo
    echo "全量备份:"
    ls -lah "$BACKUP_DIR/full" 2>/dev/null | tail -n +2 || echo "  无备份文件"
    echo
    echo "增量备份:"
    ls -lah "$BACKUP_DIR/incremental" 2>/dev/null | tail -n +2 || echo "  无备份文件"
    echo
    echo "总计:"
    echo "  文件数: $(find "$BACKUP_DIR" -type f \( -name "*.sql" -o -name "*.sql.gz" -o -name "*.info" \) | wc -l)"
    echo "  总大小: $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
}

# 主函数
main() {
    case "${1:-help}" in
        "full")
            check_mysql_connection
            backup_dir=$(create_backup_dir "full")
            backup_file="$backup_dir/full_backup_$(date +%Y%m%d_%H%M%S).sql"

            backup_full "$backup_file"
            ;;
        "incremental")
            check_mysql_connection
            backup_dir=$(create_backup_dir "incremental")
            backup_incremental "$backup_dir"
            ;;
        "restore")
            backup_file="${2:-}"
            check_mysql_connection
            restore_database "$backup_file"
            ;;
        "clean")
            clean_old_backups
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "未知参数: $1"
            echo
            show_help
            exit 1
            ;;
    esac

    # 显示备份统计
    if [ "${1:-help}" != "help" ]; then
        show_backup_stats
    fi

    log "操作完成！"
}

# 处理参数
case "${1:-help}" in
    "help"|"--help"|"-h")
        show_help
        exit 0
        ;;
esac

# 解析命令行参数
while [ $# -gt 0 ]; do
    case "$1" in
        --no-compress)
            COMPRESS=false
            shift
            ;;
        --compress)
            COMPRESS=true
            shift
            ;;
        --email)
            EMAIL_NOTIFY=true
            shift
            ;;
        --clean)
            CLEAN_AFTER=true
            shift
            ;;
        *)
            # 将其他参数传递给主函数
            break
            ;;
    esac
done

# 执行主函数
main "$@" 2>&1 | tee -a backup.log

exit 0