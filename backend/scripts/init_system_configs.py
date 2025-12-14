# ========================================
# 学生信息管理系统 - 初始化系统配置
# ========================================

from datetime import datetime
from models.system_config import SystemConfig, ConfigType, ConfigValueType
from extensions import db

def init_default_system_configs():
    """初始化默认系统配置"""

    default_configs = [
        # 基本设置
        {
            'key': 'system.name',
            'name': '系统名称',
            'description': '系统显示名称',
            'category': 'basic',
            'config_type': ConfigType.SYSTEM,
            'value_type': ConfigValueType.STRING,
            'value': '学生信息管理系统',
            'is_public': True,
            'sort_order': 1
        },
        {
            'key': 'system.description',
            'name': '系统描述',
            'description': '系统功能描述',
            'category': 'basic',
            'config_type': ConfigType.SYSTEM,
            'value_type': ConfigValueType.STRING,
            'value': '一个功能完善的学生信息管理平台',
            'is_public': True,
            'sort_order': 2
        },
        {
            'key': 'system.version',
            'name': '系统版本',
            'description': '当前系统版本号',
            'category': 'basic',
            'config_type': ConfigType.SYSTEM,
            'value_type': ConfigValueType.STRING,
            'value': '1.0.0',
            'is_editable': False,
            'is_public': True,
            'sort_order': 3
        },
        {
            'key': 'system.maintenance_mode',
            'name': '维护模式',
            'description': '是否开启系统维护模式',
            'category': 'basic',
            'config_type': ConfigType.SYSTEM,
            'value_type': ConfigValueType.BOOLEAN,
            'value': False,
            'sort_order': 4
        },
        {
            'key': 'system.maintenance_message',
            'name': '维护通知',
            'description': '系统维护期间显示的通知信息',
            'category': 'basic',
            'config_type': ConfigType.SYSTEM,
            'value_type': ConfigValueType.STRING,
            'value': '系统正在维护中，请稍后访问',
            'sort_order': 5
        },
        {
            'key': 'system.timezone',
            'name': '时区设置',
            'description': '系统默认时区',
            'category': 'basic',
            'config_type': ConfigType.SYSTEM,
            'value_type': ConfigValueType.STRING,
            'value': 'Asia/Shanghai',
            'allowed_values': ['Asia/Shanghai', 'UTC', 'America/New_York'],
            'sort_order': 6
        },
        {
            'key': 'system.language',
            'name': '语言设置',
            'description': '系统默认语言',
            'category': 'basic',
            'config_type': ConfigType.SYSTEM,
            'value_type': ConfigValueType.STRING,
            'value': 'zh-CN',
            'allowed_values': ['zh-CN', 'en-US'],
            'sort_order': 7
        },

        # 安全设置
        {
            'key': 'security.password_policy',
            'name': '密码策略',
            'description': '用户密码复杂度要求',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.ARRAY,
            'value': ['length', 'number'],
            'sort_order': 10
        },
        {
            'key': 'security.password_expiry',
            'name': '密码过期天数',
            'description': '用户密码过期天数，0表示永不过期',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.INTEGER,
            'value': 90,
            'min_value': 0,
            'max_value': 365,
            'sort_order': 11
        },
        {
            'key': 'security.login_lockout',
            'name': '登录失败锁定',
            'description': '是否启用登录失败锁定功能',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.BOOLEAN,
            'value': True,
            'sort_order': 12
        },
        {
            'key': 'security.lockout_threshold',
            'name': '锁定阈值',
            'description': '连续登录失败次数达到此值将锁定账户',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.INTEGER,
            'value': 5,
            'min_value': 3,
            'max_value': 10,
            'sort_order': 13
        },
        {
            'key': 'security.lockout_duration',
            'name': '锁定时间',
            'description': '账户锁定时长（分钟）',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.INTEGER,
            'value': 30,
            'min_value': 5,
            'max_value': 1440,
            'sort_order': 14
        },
        {
            'key': 'security.session_timeout',
            'name': '会话超时',
            'description': '用户无操作自动退出时间（分钟）',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.INTEGER,
            'value': 120,
            'min_value': 30,
            'max_value': 1440,
            'sort_order': 15
        },
        {
            'key': 'security.force_https',
            'name': '强制HTTPS',
            'description': '是否强制使用HTTPS访问',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.BOOLEAN,
            'value': False,
            'sort_order': 16
        },
        {
            'key': 'security.ip_whitelist',
            'name': 'IP白名单',
            'description': '允许访问的IP地址列表，每行一个',
            'category': 'security',
            'config_type': ConfigType.SECURITY,
            'value_type': ConfigValueType.STRING,
            'value': '',
            'sort_order': 17
        },

        # 邮件设置
        {
            'key': 'email.smtp_host',
            'name': 'SMTP服务器',
            'description': '邮件发送服务器地址',
            'category': 'email',
            'config_type': ConfigType.EMAIL,
            'value_type': ConfigValueType.STRING,
            'value': '',
            'sort_order': 20
        },
        {
            'key': 'email.smtp_port',
            'name': 'SMTP端口',
            'description': '邮件服务器端口',
            'category': 'email',
            'config_type': ConfigType.EMAIL,
            'value_type': ConfigValueType.INTEGER,
            'value': 587,
            'min_value': 1,
            'max_value': 65535,
            'sort_order': 21
        },
        {
            'key': 'email.encryption',
            'name': '加密方式',
            'description': '邮件传输加密方式',
            'category': 'email',
            'config_type': ConfigType.EMAIL,
            'value_type': ConfigValueType.STRING,
            'value': 'tls',
            'allowed_values': ['none', 'ssl', 'tls'],
            'sort_order': 22
        },
        {
            'key': 'email.from_email',
            'name': '发件人邮箱',
            'description': '系统邮件发送邮箱地址',
            'category': 'email',
            'config_type': ConfigType.EMAIL,
            'value_type': ConfigValueType.STRING,
            'value': '',
            'validation_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'sort_order': 23
        },
        {
            'key': 'email.from_name',
            'name': '发件人名称',
            'description': '系统邮件发送者名称',
            'category': 'email',
            'config_type': ConfigType.EMAIL,
            'value_type': ConfigValueType.STRING,
            'value': '系统通知',
            'sort_order': 24
        },
        {
            'key': 'email.username',
            'name': '邮箱用户名',
            'description': 'SMTP服务器认证用户名',
            'category': 'email',
            'config_type': ConfigType.EMAIL,
            'value_type': ConfigValueType.STRING,
            'value': '',
            'sort_order': 25
        },
        {
            'key': 'email.password',
            'name': '邮箱密码',
            'description': 'SMTP服务器认证密码',
            'category': 'email',
            'config_type': ConfigType.EMAIL,
            'value_type': ConfigValueType.STRING,
            'value': '',
            'sort_order': 26
        },

        # 通知设置
        {
            'key': 'notification.system_notification',
            'name': '系统通知',
            'description': '是否启用系统通知',
            'category': 'notification',
            'config_type': ConfigType.NOTIFICATION,
            'value_type': ConfigValueType.BOOLEAN,
            'value': True,
            'sort_order': 30
        },
        {
            'key': 'notification.email_notification',
            'name': '邮件通知',
            'description': '是否启用邮件通知',
            'category': 'notification',
            'config_type': ConfigType.NOTIFICATION,
            'value_type': ConfigValueType.BOOLEAN,
            'value': True,
            'sort_order': 31
        },
        {
            'key': 'notification.events',
            'name': '通知事件',
            'description': '需要发送通知的事件类型',
            'category': 'notification',
            'config_type': ConfigType.NOTIFICATION,
            'value_type': ConfigValueType.ARRAY,
            'value': ['system_error', 'security_alert'],
            'sort_order': 32
        }
    ]

    for config_data in default_configs:
        existing_config = SystemConfig.query.filter_by(key=config_data['key']).first()
        if not existing_config:
            # 创建新配置
            config = SystemConfig(**config_data)
            config.add_change_log("初始化系统配置", None, config_data['value'])
            db.session.add(config)
            print(f"创建配置: {config_data['key']}")
        else:
            print(f"配置已存在: {config_data['key']}")

    try:
        db.session.commit()
        print("系统配置初始化完成")
    except Exception as e:
        db.session.rollback()
        print(f"系统配置初始化失败: {str(e)}")

if __name__ == '__main__':
    init_default_system_configs()