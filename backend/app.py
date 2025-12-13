# ========================================
# 学生信息管理系统 - Flask应用主文件
# ========================================

import os
from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_socketio import SocketIO
from celery import Celery
import logging
from logging.handlers import RotatingFileHandler
from config import get_config
from extensions import db, redis_client

def create_app(config_name: str = None):
    """创建Flask应用工厂"""

    app = Flask(__name__)

    # 加载配置
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # 初始化配置
    config_class.init_app(app)

    # 初始化扩展
    init_extensions(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 注册上下文处理器
    register_template_context(app)

    # 配置日志
    configure_logging(app)

    # 注册CLI命令
    register_cli_commands(app)

    return app

def init_extensions(app):
    """初始化Flask扩展"""

    # 数据库
    db.init_app(app)

    # Redis
    redis_client.init_app(app)

    # 跨域
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # 密码加密
    bcrypt = Bcrypt(app)

    # JWT认证
    jwt = JWTManager(app)

    # Marshmallow序列化
    ma = Marshmallow(app)

    # 数据库迁移
    migrate = Migrate(app, db)

    # 缓存
    cache = Cache(app)

    # 限流
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )

    # 邮件
    mail = Mail(app)

    # WebSocket
    socketio = SocketIO(
        app,
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS']
    )

    # Celery
    celery = Celery(
        app.name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    # 将扩展添加到app上下文
    app.extensions['bcrypt'] = bcrypt
    app.extensions['jwt'] = jwt
    app.extensions['ma'] = ma
    app.extensions['migrate'] = migrate
    app.extensions['cache'] = cache
    app.extensions['limiter'] = limiter
    app.extensions['mail'] = mail
    app.extensions['socketio'] = socketio
    app.extensions['celery'] = celery

def register_blueprints(app):
    """注册蓝图"""

    from api import api_bp
    app.register_blueprint(api_bp, url_prefix=app.config['API_PREFIX'])

def register_error_handlers(app):
    """注册错误处理器"""

    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad Request', 'message': str(error)}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': '请先登录'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': '权限不足'}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': '资源不存在'}, 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'error': 'Method Not Allowed', 'message': '请求方法不允许'}, 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        if hasattr(error, 'data'):
            return {'error': 'Validation Error', 'messages': error.data['messages']}, 422
        return {'error': 'Unprocessable Entity', 'message': str(error)}, 422

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': 'Too Many Requests', 'message': '请求过于频繁，请稍后再试'}, 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal Server Error', 'message': '服务器内部错误'}, 500

def register_template_context(app):
    """注册模板上下文处理器"""

    @app.context_processor
    def inject_config():
        """注入配置到模板上下文"""
        return {
            'SYSTEM_NAME': app.config['SYSTEM_NAME'],
            'SYSTEM_VERSION': app.config['SYSTEM_VERSION'],
            'API_PREFIX': app.config['API_PREFIX']
        }

def configure_logging(app):
    """配置日志"""

    if not app.debug and not app.testing:
        # 生产环境配置文件日志
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)

        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info(f'{app.config["SYSTEM_NAME"]} 启动')

def register_cli_commands(app):
    """注册CLI命令"""

    @app.cli.command()
    def init_db():
        """初始化数据库"""
        from models import User
        db.create_all()
        print('数据库初始化完成')

    @app.cli.command()
    def create_admin():
        """创建管理员用户"""
        from models import User
        from extensions import bcrypt

        username = 'admin'
        password = '123456'
        email = 'admin@example.com'

        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            print(f'用户 {username} 已存在')
            return

        # 创建管理员用户
        admin_user = User(
            username=username,
            email=email,
            role='admin',
            status='active',
            email_verified=True
        )
        admin_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        db.session.add(admin_user)
        db.session.commit()

        print(f'管理员用户 {username} 创建成功')

    @app.cli.command()
    def seed_data():
        """填充种子数据"""
        print('正在填充种子数据...')
        # 这里可以调用种子数据脚本
        print('种子数据填充完成')

    @app.cli.command()
    def test_data():
        """创建测试数据"""
        print('正在创建测试数据...')
        # 这里可以调用测试数据脚本
        print('测试数据创建完成')

# 创建应用实例
app = create_app()

# 导入模型（确保在app创建后）
from models import *

# 导入API路由
from api import *

if __name__ == '__main__':
    socketio = app.extensions['socketio']
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)