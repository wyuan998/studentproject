# ========================================
# 学生信息管理系统 - Flask应用配置
# ========================================

import os
from datetime import timedelta
from typing import Optional

class Config:
    """基础配置类"""

    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 数据库配置
    MYSQL_HOST = os.environ.get('DB_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('DB_PORT') or 3306)
    MYSQL_USER = os.environ.get('DB_USER') or 'sms_user'
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD') or 'sms_password_2024'
    MYSQL_DATABASE = os.environ.get('DB_NAME') or 'student_management'
    MYSQL_CHARSET = 'utf8mb4'

    # SQLALCHEMY配置
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@'
        f'{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset={MYSQL_CHARSET}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
    }

    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = int(os.environ.get('REDIS_DB') or 0)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080']

    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'}

    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # 缓存配置
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300

    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'app.log')

    # API配置
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'

    # 系统配置
    SYSTEM_NAME = '学生信息管理系统'
    SYSTEM_VERSION = '1.0.0'
    SYSTEM_DESCRIPTION = '基于Flask和Vue.js的学生信息管理系统'

    # 安全配置
    BCRYPT_LOG_ROUNDS = 12
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100/hour"

    # WebSocket配置
    SOCKETIO_ASYNC_MODE = 'gevent'
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS

    # 任务队列配置
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'

    # 业务配置
    MIN_PASSWORD_LENGTH = 6
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_ATTEMPT_WINDOW = 300  # 5分钟

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建上传目录
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        # 创建日志目录
        log_dir = os.path.dirname(Config.LOG_FILE)
        os.makedirs(log_dir, exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""

    DEBUG = True
    TESTING = False

    # 开发环境使用更宽松的安全设置
    SECRET_KEY = 'dev-secret-key-for-development-only'
    JWT_SECRET_KEY = 'dev-jwt-secret-key-for-development-only'

    # 开发环境显示SQL
    SQLALCHEMY_ECHO = True

    # 开发环境CORS允许所有来源
    CORS_ORIGINS = ['*']

    # 开发环境邮件配置
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025  # 使用debug mail server

    # 开发环境Redis配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379

    # 开发环境限流更宽松
    RATELIMIT_DEFAULT = "1000/hour"

class TestingConfig(Config):
    """测试环境配置"""

    TESTING = True
    DEBUG = True

    # 测试数据库
    MYSQL_DATABASE = 'test_student_management'
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@'
        f'{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/test_student_management'
        f'?charset={Config.MYSQL_CHARSET}'
    )

    # 测试环境Redis
    REDIS_DB = 1

    # 禁用CSRF保护
    WTF_CSRF_ENABLED = False

    # 测试环境JWT过期时间更短
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)

    # 测试环境不发送邮件
    MAIL_SUPPRESS_SEND = True

    # 测试环境文件上传到临时目录
    UPLOAD_FOLDER = '/tmp/uploads'

class ProductionConfig(Config):
    """生产环境配置"""

    DEBUG = False
    TESTING = False

    # 生产环境强制设置安全密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")
    if not JWT_SECRET_KEY:
        raise ValueError("生产环境必须设置JWT_SECRET_KEY环境变量")

    # 生产环境SQLAlchemy配置
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30,
        'pool_timeout': 30,
    }

    # 生产环境安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 生产环境限流更严格
    RATELIMIT_DEFAULT = "60/hour"

    # 生产环境日志级别
    LOG_LEVEL = 'WARNING'

class StagingConfig(Config):
    """预发布环境配置"""

    DEBUG = False
    TESTING = False

    # 预发布环境数据库
    MYSQL_DATABASE = 'staging_student_management'

    # 预发布环境Redis
    REDIS_DB = 2

    # 预发布环境日志级别
    LOG_LEVEL = 'INFO'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """获取配置对象"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config.get(config_name, config['default'])