# ========================================
# 学生信息管理系统 - 数据导入导出API
# ========================================

from flask import request, current_app, send_file, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_
from datetime import datetime
import os
import tempfile
import pandas as pd
import json
from werkzeug.utils import secure_filename

from models import User, Student, Teacher, Course, Enrollment, Grade, db
from schemas import UserSchema, StudentSchema, TeacherSchema, CourseSchema, EnrollmentSchema, GradeSchema
from utils.responses import success_response, error_response, validation_error_response
from utils.decorators import require_permission
from utils.audit import log_action

api = Namespace('data-import-export', description='数据导入导出')

# 导入模型定义
import_model = api.model('ImportPreview', {
    'type': fields.String(required=True, description='导入类型'),
    'data': fields.List(fields.Raw(), required=True, description='导入数据'),
    'mapping': fields.Raw(description='字段映射配置')
})

# 导出配置模型
export_config_model = api.model('ExportConfig', {
    'type': fields.String(required=True, description='导出类型'),
    'format': fields.String(required=True, enum=['xlsx', 'csv', 'json'], description='导出格式'),
    'filters': fields.Raw(description='筛选条件'),
    'fields': fields.List(fields.String(), description='导出字段')
})

class DataImportExporter:
    """数据导入导出处理器"""

    @staticmethod
    def validate_file(file):
        """验证上传文件"""
        if not file:
            raise ValidationError("请选择文件")

        filename = secure_filename(file.filename)
        if not filename:
            raise ValidationError("文件名无效")

        # 检查文件类型
        allowed_extensions = {'xlsx', 'xls', 'csv', 'json'}
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            raise ValidationError("仅支持Excel、CSV和JSON文件")

        # 检查文件大小（10MB限制）
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > 10 * 1024 * 1024:
            raise ValidationError("文件大小不能超过10MB")

        return True

    @staticmethod
    def read_file(file, file_type=None):
        """读取文件数据"""
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        try:
            if ext in ['xlsx', 'xls']:
                # 读取Excel文件
                df = pd.read_excel(file, sheet_name=0)
            elif ext == 'csv':
                # 读取CSV文件
                df = pd.read_csv(file, encoding='utf-8-sig')
            elif ext == 'json':
                # 读取JSON文件
                content = file.read().decode('utf-8-sig')
                data = json.loads(content)
                return data
            else:
                raise ValidationError("不支持的文件格式")

            # 转换为字典列表
            return df.to_dict('records')

        except Exception as e:
            raise ValidationError(f"文件读取失败: {str(e)}")

    @staticmethod
    def export_data(data, export_format, filename):
        """导出数据"""
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{export_format}')

            if export_format == 'xlsx':
                # 导出为Excel
                df = pd.DataFrame(data)
                with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)

            elif export_format == 'csv':
                # 导出为CSV
                df = pd.DataFrame(data)
                df.to_csv(temp_file.name, index=False, encoding='utf-8-sig')

            elif export_format == 'json':
                # 导出为JSON
                with open(temp_file.name, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            return temp_file.name

        except Exception as e:
            raise ValidationError(f"导出失败: {str(e)}")

    @staticmethod
    def get_import_schema(data_type):
        """获取导入数据结构"""
        schemas = {
            'users': {
                'fields': ['username', 'email', 'password_hash', 'role', 'is_active'],
                'required': ['username', 'email', 'role']
            },
            'students': {
                'fields': ['student_id', 'user_id', 'first_name', 'last_name', 'gender', 'birthday', 'major'],
                'required': ['student_id', 'user_id', 'first_name', 'last_name']
            },
            'teachers': {
                'fields': ['teacher_id', 'user_id', 'first_name', 'last_name', 'gender', 'department', 'title'],
                'required': ['teacher_id', 'user_id', 'first_name', 'last_name']
            },
            'courses': {
                'fields': ['course_code', 'name', 'description', 'credits', 'teacher_id'],
                'required': ['course_code', 'name', 'teacher_id']
            },
            'enrollments': {
                'fields': ['student_id', 'course_id', 'enrollment_date', 'status'],
                'required': ['student_id', 'course_id']
            },
            'grades': {
                'fields': ['student_id', 'course_id', 'grade', 'grade_type', 'exam_date', 'remarks'],
                'required': ['student_id', 'course_id', 'grade']
            }
        }

        return schemas.get(data_type)

    @staticmethod
    def validate_import_data(data, schema):
        """验证导入数据"""
        errors = []
        valid_data = []

        for i, item in enumerate(data, 1):
            item_errors = []
            valid_item = {}

            # 检查必填字段
            for field in schema['required']:
                if field not in item or item[field] in [None, '', 'null']:
                    item_errors.append(f"第{i}行: 必填字段 '{field}' 不能为空")

            # 检查字段格式
            for field in schema['fields']:
                if field in item and item[field] not in [None, '', 'null']:
                    valid_item[field] = item[field]

            if not item_errors:
                valid_data.append(valid_item)
            else:
                errors.extend(item_errors)

        return valid_data, errors

@api.route('/import/preview')
class ImportPreviewResource(Resource):
    @api.doc('preview_import')
    @api.expect(import_model)
    @jwt_required()
    @require_permission('data_import')
    def post(self):
        """预览导入数据"""
        try:
            data = request.get_json()
            import_type = data.get('type')
            import_data = data.get('data', [])

            if not import_type or not import_data:
                return error_response("导入类型和数据不能为空", 400)

            # 获取数据结构
            schema = DataImportExporter.get_import_schema(import_type)
            if not schema:
                return error_response("不支持的导入类型", 400)

            # 验证数据
            valid_data, errors = DataImportExporter.validate_import_data(import_data, schema)

            return success_response({
                'total_rows': len(import_data),
                'valid_rows': len(valid_data),
                'error_count': len(errors),
                'errors': errors[:10],  # 只返回前10个错误
                'preview_data': valid_data[:5],  # 预览前5行
                'schema': schema
            })

        except Exception as e:
            current_app.logger.error(f"导入预览失败: {str(e)}")
            return error_response(str(e), 500)

@api.route('/import/execute')
class ImportExecuteResource(Resource):
    @api.doc('execute_import')
    @api.expect(import_model)
    @jwt_required()
    @require_permission('data_import')
    def post(self):
        """执行数据导入"""
        try:
            data = request.get_json()
            import_type = data.get('type')
            import_data = data.get('data', [])

            if not import_type or not import_data:
                return error_response("导入类型和数据不能为空", 400)

            current_user_id = get_jwt_identity()
            success_count = 0
            errors = []

            # 获取对应的模型和Schema
            model_map = {
                'users': (User, UserSchema(exclude=['id', 'created_at', 'updated_at'])),
                'students': (Student, StudentSchema(exclude=['id', 'created_at', 'updated_at'])),
                'teachers': (Teacher, TeacherSchema(exclude=['id', 'created_at', 'updated_at'])),
                'courses': (Course, CourseSchema(exclude=['id', 'created_at', 'updated_at'])),
                'enrollments': (Enrollment, EnrollmentSchema(exclude=['id', 'created_at', 'updated_at'])),
                'grades': (Grade, GradeSchema(exclude=['id', 'created_at', 'updated_at']))
            }

            if import_type not in model_map:
                return error_response("不支持的导入类型", 400)

            model_class, schema = model_map[import_type]

            # 批量导入数据
            for i, item_data in enumerate(import_data, 1):
                try:
                    # 检查数据是否已存在（基于唯一字段）
                    existing = None
                    if import_type == 'users':
                        existing = model_class.query.filter_by(username=item_data.get('username')).first()
                    elif import_type == 'students':
                        existing = model_class.query.filter_by(student_id=item_data.get('student_id')).first()
                    elif import_type == 'teachers':
                        existing = model_class.query.filter_by(teacher_id=item_data.get('teacher_id')).first()
                    elif import_type == 'courses':
                        existing = model_class.query.filter_by(course_code=item_data.get('course_code')).first()

                    if existing:
                        errors.append(f"第{i}行: 数据已存在")
                        continue

                    # 创建新记录
                    schema_instance = schema()
                    validated_data = schema_instance.load(item_data)

                    new_record = model_class(**validated_data)
                    db.session.add(new_record)
                    success_count += 1

                except Exception as e:
                    errors.append(f"第{i}行: {str(e)}")
                    db.session.rollback()

            # 提交事务
            if success_count > 0:
                db.session.commit()

            # 记录审计日志
            log_action(
                user_id=current_user_id,
                action='data_import',
                resource_type=import_type,
                description=f"导入 {import_type} 数据，成功 {success_count} 条，失败 {len(errors)} 条"
            )

            return success_response({
                'total_rows': len(import_data),
                'success_count': success_count,
                'error_count': len(errors),
                'errors': errors[:20]  # 只返回前20个错误
            }, f"导入完成，成功 {success_count} 条，失败 {len(errors)} 条")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"数据导入失败: {str(e)}")
            return error_response(str(e), 500)

@api.route('/export')
class ExportResource(Resource):
    @api.doc('export_data')
    @api.expect(export_config_model)
    @jwt_required()
    @require_permission('data_export')
    def post(self):
        """导出数据"""
        try:
            data = request.get_json()
            export_type = data.get('type')
            export_format = data.get('format', 'xlsx')
            filters = data.get('filters', {})
            fields = data.get('fields')

            if not export_type:
                return error_response("导出类型不能为空", 400)

            current_user_id = get_jwt_identity()

            # 获取数据
            model_map = {
                'users': User,
                'students': Student,
                'teachers': Teacher,
                'courses': Course,
                'enrollments': Enrollment,
                'grades': Grade
            }

            if export_type not in model_map:
                return error_response("不支持的导出类型", 400)

            model_class = model_map[export_type]
            query = model_class.query

            # 应用筛选条件
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key):
                        if isinstance(value, list):
                            query = query.filter(getattr(model_class, key).in_(value))
                        else:
                            query = query.filter(getattr(model_class, key) == value)

            # 获取数据
            records = query.all()

            # 序列化数据
            schema_map = {
                'users': UserSchema,
                'students': StudentSchema,
                'teachers': TeacherSchema,
                'courses': CourseSchema,
                'enrollments': EnrollmentSchema,
                'grades': GradeSchema
            }

            schema = schema_map[export_type]()
            data = schema.dump(records, many=True)

            # 字段过滤
            if fields:
                filtered_data = []
                for record in data:
                    filtered_record = {k: v for k, v in record.items() if k in fields}
                    filtered_data.append(filtered_record)
                data = filtered_data

            # 导出文件
            filename = f"{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            temp_file = DataImportExporter.export_data(data, export_format, filename)

            # 记录审计日志
            log_action(
                user_id=current_user_id,
                action='data_export',
                resource_type=export_type,
                description=f"导出 {export_type} 数据，共 {len(data)} 条记录"
            )

            # 返回文件
            return send_file(
                temp_file,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )

        except Exception as e:
            current_app.logger.error(f"数据导出失败: {str(e)}")
            return error_response(str(e), 500)

@api.route('/templates')
class TemplateResource(Resource):
    @api.doc('get_templates')
    @jwt_required()
    def get(self):
        """获取导入模板"""
        try:
            templates = {}

            # 各类型的模板结构
            template_schemas = {
                'users': {
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'password_hash': 'hashed_password',
                    'role': 'admin',
                    'is_active': True
                },
                'students': {
                    'student_id': 'S001',
                    'user_id': 1,
                    'first_name': '张',
                    'last_name': '三',
                    'gender': 'male',
                    'birthday': '2000-01-01',
                    'major': '计算机科学'
                },
                'teachers': {
                    'teacher_id': 'T001',
                    'user_id': 2,
                    'first_name': '李',
                    'last_name': '四',
                    'gender': 'male',
                    'department': '计算机学院',
                    'title': '教授'
                },
                'courses': {
                    'course_code': 'CS101',
                    'name': '计算机基础',
                    'description': '计算机基础课程',
                    'credits': 3,
                    'teacher_id': 'T001'
                },
                'enrollments': {
                    'student_id': 'S001',
                    'course_id': 1,
                    'enrollment_date': '2023-09-01',
                    'status': 'active'
                },
                'grades': {
                    'student_id': 'S001',
                    'course_id': 1,
                    'grade': 85.5,
                    'grade_type': 'final',
                    'exam_date': '2023-12-20',
                    'remarks': '良好'
                }
            }

            for data_type, example in template_schemas.items():
                # 获取schema信息
                schema = DataImportExporter.get_import_schema(data_type)

                templates[data_type] = {
                    'schema': schema,
                    'example': example,
                    'description': f'{data_type} 数据导入模板'
                }

            return success_response(templates)

        except Exception as e:
            current_app.logger.error(f"获取模板失败: {str(e)}")
            return error_response(str(e), 500)