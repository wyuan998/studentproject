from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import desc, or_
from datetime import datetime, timedelta
import json

from ..models import SystemConfig, User, AuditLog, db
from ..utils.responses import success_response, error_response
from ..utils.decorators import require_permission
from ..schemas.system_config import SystemConfigSchema, SystemConfigCreateSchema, SystemConfigUpdateSchema

api = Namespace('system-config', description='系统配置管理')

# Swagger模型定义
system_config_model = api.model('SystemConfig', {
    'key': fields.String(required=True, description='配置键'),
    'value': fields.String(required=True, description='配置值'),
    'value_type': fields.String(required=True, description='值类型'),
    'description': fields.String(description='配置描述'),
    'category': fields.String(required=True, description='配置分类'),
    'is_encrypted': fields.Boolean(description='是否加密存储'),
    'is_public': fields.Boolean(description='是否公开访问'),
    'validation_rule': fields.String(description='验证规则'),
    'sort_order': fields.Integer(description='排序顺序'),
    'is_active': fields.Boolean(description='是否激活')
})

config_batch_model = api.model('ConfigBatch', {
    'configs': fields.List(fields.Raw, required=True, description='配置列表'),
    'category': fields.String(description='配置分类')
})

# 初始化Schema
config_schema = SystemConfigSchema()
configs_schema = SystemConfigSchema(many=True)
config_create_schema = SystemConfigCreateSchema()
config_update_schema = SystemConfigUpdateSchema()

@api.route('')
class SystemConfigList(Resource):
    @api.doc('list_system_configs')
    @api.param('category', '配置分类')
    @api.param('is_active', '是否激活')
    @api.param('page', '页码', type=int, default=1)
    @api.param('per_page', '每页数量', type=int, default=20)
    @jwt_required()
    @require_permission('system_config:read')
    def get(self):
        """获取系统配置列表"""
        try:
            category = request.args.get('category')
            is_active = request.args.get('is_active', type=bool)
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)

            # 构建查询
            query = SystemConfig.query

            if category:
                query = query.filter(SystemConfig.category == category)

            if is_active is not None:
                query = query.filter(SystemConfig.is_active == is_active)

            # 分页
            pagination = query.order_by(SystemConfig.category, SystemConfig.sort_order, SystemConfig.key)\
                            .paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'configs': configs_schema.dump(pagination.items),
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            })

        except Exception as e:
            current_app.logger.error(f"获取系统配置列表失败: {str(e)}")
            return error_response("获取系统配置列表失败")

    @api.doc('create_system_config')
    @api.expect(system_config_model)
    @jwt_required()
    @require_permission('system_config:create')
    def post(self):
        """创建系统配置"""
        try:
            data = request.get_json()

            # 验证输入数据
            try:
                validated_data = config_create_schema.load(data)
            except ValidationError as err:
                return error_response("数据验证失败", 400, err.messages)

            # 检查配置键是否已存在
            existing_config = SystemConfig.query.filter_by(key=validated_data['key']).first()
            if existing_config:
                return error_response(f"配置键 {validated_data['key']} 已存在")

            # 创建配置
            config = SystemConfig(**validated_data)
            db.session.add(config)

            # 记录操作日志
            current_user_id = get_jwt_identity()
            audit_log = AuditLog(
                user_id=current_user_id,
                action='create_system_config',
                resource_type='system_config',
                resource_id=config.id,
                details={
                    'key': config.key,
                    'category': config.category,
                    'description': config.description
                }
            )
            db.session.add(audit_log)
            db.session.commit()

            return success_response(config_schema.dump(config), "系统配置创建成功")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建系统配置失败: {str(e)}")
            return error_response("创建系统配置失败")

@api.route('/batch')
class SystemConfigBatch(Resource):
    @api.doc('batch_create_configs')
    @api.expect(config_batch_model)
    @jwt_required()
    @require_permission('system_config:create')
    def post(self):
        """批量创建系统配置"""
        try:
            data = request.get_json()
            configs = data.get('configs', [])
            category = data.get('category')

            if not configs:
                return error_response("配置列表不能为空")

            created_configs = []
            errors = []

            for i, config_data in enumerate(configs):
                try:
                    # 设置分类
                    if category:
                        config_data['category'] = category

                    # 验证数据
                    validated_data = config_create_schema.load(config_data)

                    # 检查是否已存在
                    existing_config = SystemConfig.query.filter_by(key=validated_data['key']).first()
                    if existing_config:
                        errors.append(f"第{i+1}行: 配置键 {validated_data['key']} 已存在")
                        continue

                    # 创建配置
                    config = SystemConfig(**validated_data)
                    db.session.add(config)
                    created_configs.append(config)

                except ValidationError as err:
                    errors.append(f"第{i+1}行: 数据验证失败")
                except Exception as e:
                    errors.append(f"第{i+1}行: {str(e)}")

            if created_configs:
                # 记录操作日志
                current_user_id = get_jwt_identity()
                audit_log = AuditLog(
                    user_id=current_user_id,
                    action='batch_create_configs',
                    resource_type='system_config',
                    details={
                        'created_count': len(created_configs),
                        'error_count': len(errors),
                        'category': category
                    }
                )
                db.session.add(audit_log)
                db.session.commit()

                return success_response({
                    'created_configs': configs_schema.dump(created_configs),
                    'created_count': len(created_configs),
                    'errors': errors
                }, f"批量创建完成，成功 {len(created_configs)} 个，失败 {len(errors)} 个")
            else:
                db.session.rollback()
                return error_response("批量创建失败", 400, {'errors': errors})

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"批量创建系统配置失败: {str(e)}")
            return error_response("批量创建系统配置失败")

    @api.doc('batch_update_configs')
    @api.expect(config_batch_model)
    @jwt_required()
    @require_permission('system_config:update')
    def put(self):
        """批量更新系统配置"""
        try:
            data = request.get_json()
            configs = data.get('configs', [])

            if not configs:
                return error_response("配置列表不能为空")

            updated_configs = []
            errors = []

            for i, config_data in enumerate(configs):
                try:
                    key = config_data.get('key')
                    if not key:
                        errors.append(f"第{i+1}行: 配置键不能为空")
                        continue

                    # 查找配置
                    config = SystemConfig.query.filter_by(key=key).first()
                    if not config:
                        errors.append(f"第{i+1}行: 配置键 {key} 不存在")
                        continue

                    # 验证并更新数据
                    validated_data = config_update_schema.load(config_data, partial=True)
                    for field, value in validated_data.items():
                        setattr(config, field, value)

                    updated_configs.append(config)

                except ValidationError as err:
                    errors.append(f"第{i+1}行: 数据验证失败")
                except Exception as e:
                    errors.append(f"第{i+1}行: {str(e)}")

            if updated_configs:
                # 记录操作日志
                current_user_id = get_jwt_identity()
                audit_log = AuditLog(
                    user_id=current_user_id,
                    action='batch_update_configs',
                    resource_type='system_config',
                    details={
                        'updated_count': len(updated_configs),
                        'error_count': len(errors)
                    }
                )
                db.session.add(audit_log)
                db.session.commit()

                return success_response({
                    'updated_configs': configs_schema.dump(updated_configs),
                    'updated_count': len(updated_configs),
                    'errors': errors
                }, f"批量更新完成，成功 {len(updated_configs)} 个，失败 {len(errors)} 个")
            else:
                db.session.rollback()
                return error_response("批量更新失败", 400, {'errors': errors})

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"批量更新系统配置失败: {str(e)}")
            return error_response("批量更新系统配置失败")

@api.route('/categories')
class SystemConfigCategories(Resource):
    @api.doc('get_config_categories')
    @jwt_required()
    @require_permission('system_config:read')
    def get(self):
        """获取配置分类列表"""
        try:
            categories = db.session.query(SystemConfig.category,
                                         db.func.count(SystemConfig.id).label('count'))\
                                 .filter(SystemConfig.is_active == True)\
                                 .group_by(SystemConfig.category)\
                                 .order_by(SystemConfig.category)\
                                 .all()

            category_list = [
                {
                    'category': cat[0],
                    'config_count': cat[1]
                }
                for cat in categories
            ]

            return success_response(category_list)

        except Exception as e:
            current_app.logger.error(f"获取配置分类失败: {str(e)}")
            return error_response("获取配置分类失败")

@api.route('/public')
class PublicSystemConfig(Resource):
    @api.doc('get_public_configs')
    def get(self):
        """获取公开配置（无需认证）"""
        try:
            configs = SystemConfig.query.filter_by(is_public=True, is_active=True)\
                                     .order_by(SystemConfig.category, SystemConfig.sort_order)\
                                     .all()

            # 格式化配置为键值对
            config_dict = {}
            for config in configs:
                config_dict[config.key] = config.get_value()

            return success_response(config_dict)

        except Exception as e:
            current_app.logger.error(f"获取公开配置失败: {str(e)}")
            return error_response("获取公开配置失败")

@api.route('/export')
class SystemConfigExport(Resource):
    @api.doc('export_configs')
    @api.param('category', '配置分类')
    @api.param('format', '导出格式', default='json')
    @jwt_required()
    @require_permission('system_config:export')
    def get(self):
        """导出系统配置"""
        try:
            category = request.args.get('category')
            export_format = request.args.get('format', 'json')

            # 构建查询
            query = SystemConfig.query
            if category:
                query = query.filter(SystemConfig.category == category)

            configs = query.order_by(SystemConfig.category, SystemConfig.sort_order).all()

            if export_format == 'json':
                # JSON格式导出
                export_data = {
                    'export_time': datetime.utcnow().isoformat(),
                    'category': category,
                    'configs': configs_schema.dump(configs)
                }
                return success_response(export_data)
            else:
                return error_response("不支持的导出格式")

        except Exception as e:
            current_app.logger.error(f"导出系统配置失败: {str(e)}")
            return error_response("导出系统配置失败")

@api.route('/<string:key>')
class SystemConfigDetail(Resource):
    @api.doc('get_system_config')
    @jwt_required()
    @require_permission('system_config:read')
    def get(self, key):
        """获取指定配置详情"""
        try:
            config = SystemConfig.query.filter_by(key=key).first()
            if not config:
                return error_response("配置不存在", 404)

            return success_response(config_schema.dump(config))

        except Exception as e:
            current_app.logger.error(f"获取系统配置详情失败: {str(e)}")
            return error_response("获取系统配置详情失败")

    @api.doc('update_system_config')
    @api.expect(system_config_model)
    @jwt_required()
    @require_permission('system_config:update')
    def put(self, key):
        """更新系统配置"""
        try:
            config = SystemConfig.query.filter_by(key=key).first()
            if not config:
                return error_response("配置不存在", 404)

            data = request.get_json()

            # 验证输入数据
            try:
                validated_data = config_update_schema.load(data, partial=True)
            except ValidationError as err:
                return error_response("数据验证失败", 400, err.messages)

            # 保存旧值用于审计
            old_value = config.value
            old_description = config.description

            # 更新字段
            for field, value in validated_data.items():
                setattr(config, field, value)

            config.updated_at = datetime.utcnow()

            # 记录操作日志
            current_user_id = get_jwt_identity()
            audit_log = AuditLog(
                user_id=current_user_id,
                action='update_system_config',
                resource_type='system_config',
                resource_id=config.id,
                details={
                    'key': config.key,
                    'category': config.category,
                    'old_value': old_value,
                    'new_value': config.value,
                    'changed_fields': list(validated_data.keys())
                }
            )
            db.session.add(audit_log)
            db.session.commit()

            return success_response(config_schema.dump(config), "系统配置更新成功")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新系统配置失败: {str(e)}")
            return error_response("更新系统配置失败")

    @api.doc('delete_system_config')
    @jwt_required()
    @require_permission('system_config:delete')
    def delete(self, key):
        """删除系统配置"""
        try:
            config = SystemConfig.query.filter_by(key=key).first()
            if not config:
                return error_response("配置不存在", 404)

            # 软删除
            config.is_active = False
            config.updated_at = datetime.utcnow()

            # 记录操作日志
            current_user_id = get_jwt_identity()
            audit_log = AuditLog(
                user_id=current_user_id,
                action='delete_system_config',
                resource_type='system_config',
                resource_id=config.id,
                details={
                    'key': config.key,
                    'category': config.category,
                    'value': config.value
                }
            )
            db.session.add(audit_log)
            db.session.commit()

            return success_response(None, "系统配置删除成功")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除系统配置失败: {str(e)}")
            return error_response("删除系统配置失败")

@api.route('/cache/clear')
class SystemConfigCache(Resource):
    @api.doc('clear_config_cache')
    @jwt_required()
    @require_permission('system_config:manage')
    def post(self):
        """清除配置缓存"""
        try:
            # 这里可以集成Redis缓存清除逻辑
            # 例如: redis_client.delete_pattern("config:*")

            # 记录操作日志
            current_user_id = get_jwt_identity()
            audit_log = AuditLog(
                user_id=current_user_id,
                action='clear_config_cache',
                resource_type='system_config',
                details={'action': 'clear_cache'}
            )
            db.session.add(audit_log)
            db.session.commit()

            return success_response(None, "配置缓存清除成功")

        except Exception as e:
            current_app.logger.error(f"清除配置缓存失败: {str(e)}")
            return error_response("清除配置缓存失败")