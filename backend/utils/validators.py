# ========================================
# 学生信息管理系统 - 验证器工具类
# ========================================

import re
import phonenumbers
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from email.utils import parseaddr
import isbnlib
from urllib.parse import urlparse
import json

from flask import current_app


class BaseValidator:
    """基础验证器"""

    @staticmethod
    def is_required(value: Any, field_name: str = None) -> Dict[str, Any]:
        """
        验证必填字段

        Args:
            value: 要验证的值
            field_name: 字段名称

        Returns:
            Dict[str, Any]: 验证结果
        """
        if value is None or value == '':
            return {
                'valid': False,
                'message': f"{field_name or '字段'}不能为空"
            }
        return {'valid': True}

    @staticmethod
    def is_length(value: str, min_length: int = None, max_length: int = None, field_name: str = None) -> Dict[str, Any]:
        """
        验证字符串长度

        Args:
            value: 要验证的值
            min_length: 最小长度
            max_length: 最大长度
            field_name: 字段名称

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(value, str):
            value = str(value)

        length = len(value)

        if min_length is not None and length < min_length:
            return {
                'valid': False,
                'message': f"{field_name or '字段'}长度不能少于{min_length}个字符"
            }

        if max_length is not None and length > max_length:
            return {
                'valid': False,
                'message': f"{field_name or '字段'}长度不能超过{max_length}个字符"
            }

        return {'valid': True}

    @staticmethod
    def is_in_choices(value: Any, choices: List[Any], field_name: str = None) -> Dict[str, Any]:
        """
        验证值是否在选项列表中

        Args:
            value: 要验证的值
            choices: 选项列表
            field_name: 字段名称

        Returns:
            Dict[str, Any]: 验证结果
        """
        if value not in choices:
            return {
                'valid': False,
                'message': f"{field_name or '字段'}必须是以下选项之一: {', '.join(map(str, choices))}"
            }
        return {'valid': True}

    @staticmethod
    def is_regex_match(value: str, pattern: str, field_name: str = None) -> Dict[str, Any]:
        """
        验证正则表达式匹配

        Args:
            value: 要验证的值
            pattern: 正则表达式模式
            field_name: 字段名称

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not re.match(pattern, value):
            return {
                'valid': False,
                'message': f"{field_name or '字段'}格式不正确"
            }
        return {'valid': True}

    @staticmethod
    def is_numeric(value: Any, min_value: Union[int, float] = None, max_value: Union[int, float] = None, field_name: str = None) -> Dict[str, Any]:
        """
        验证数值

        Args:
            value: 要验证的值
            min_value: 最小值
            max_value: 最大值
            field_name: 字段名称

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return {
                'valid': False,
                'message': f"{field_name or '字段'}必须是数字"
            }

        if min_value is not None and num_value < min_value:
            return {
                'valid': False,
                'message': f"{field_name or '字段'}不能小于{min_value}"
            }

        if max_value is not None and num_value > max_value:
            return {
                'valid': False,
                'message': f"{field_name or '字段'}不能大于{max_value}"
            }

        return {'valid': True, 'value': num_value}


class PersonalInfoValidator(BaseValidator):
    """个人信息验证器"""

    @staticmethod
    def validate_email(email: str) -> Dict[str, Any]:
        """
        验证邮箱地址

        Args:
            email: 邮箱地址

        Returns:
            Dict[str, Any]: 验证结果
        """
        # 基础格式验证
        if not isinstance(email, str):
            return {'valid': False, 'message': '邮箱必须是字符串'}

        # 使用email.utils进行基础验证
        parsed = parseaddr(email)
        if not parsed[1] or '@' not in parsed[1]:
            return {'valid': False, 'message': '邮箱格式不正确'}

        # 更严格的正则表达式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {'valid': False, 'message': '邮箱格式不正确'}

        # 检查长度
        if len(email) > 254:  # RFC 5321 标准
            return {'valid': False, 'message': '邮箱长度不能超过254个字符'}

        # 检查域名部分
        domain = email.split('@')[1]
        if len(domain) > 253:
            return {'valid': False, 'message': '邮箱域名部分过长'}

        return {'valid': True, 'normalized': email.lower()}

    @staticmethod
    def validate_phone_number(phone: str, region: str = 'CN') -> Dict[str, Any]:
        """
        验证手机号码

        Args:
            phone: 手机号码
            region: 区域代码

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 清理输入
            phone = re.sub(r'[^\d+]', '', phone)

            # 使用phonenumbers库验证
            parsed_number = phonenumbers.parse(phone, region)

            if not phonenumbers.is_valid_number(parsed_number):
                return {'valid': False, 'message': '手机号码格式不正确'}

            # 格式化为国际标准格式
            formatted_number = phonenumbers.format_number(
                parsed_number,
                phonenumbers.PhoneNumberFormat.E164
            )

            return {
                'valid': True,
                'formatted': formatted_number,
                'national': phonenumbers.format_number(
                    parsed_number,
                    phonenumbers.PhoneNumberFormat.NATIONAL
                )
            }

        except Exception as e:
            # 简单的中国手机号验证作为后备
            if region == 'CN':
                chinese_phone_pattern = r'^1[3-9]\d{9}$'
                if re.match(chinese_phone_pattern, phone):
                    return {
                        'valid': True,
                        'formatted': f'+86{phone}',
                        'national': phone
                    }

            return {'valid': False, 'message': '手机号码格式不正确'}

    @staticmethod
    def validate_id_card(id_card: str) -> Dict[str, Any]:
        """
        验证身份证号码

        Args:
            id_card: 身份证号码

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(id_card, str):
            return {'valid': False, 'message': '身份证号码必须是字符串'}

        id_card = id_card.strip().upper()

        # 验证长度
        if len(id_card) not in [15, 18]:
            return {'valid': False, 'message': '身份证号码长度不正确'}

        # 18位身份证验证
        if len(id_card) == 18:
            pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'
            if not re.match(pattern, id_card):
                return {'valid': False, 'message': '18位身份证号码格式不正确'}

            # 校验码验证
            weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

            total = 0
            for i in range(17):
                total += int(id_card[i]) * weights[i]

            check_code = check_codes[total % 11]
            if id_card[-1] != check_code:
                return {'valid': False, 'message': '身份证号码校验码不正确'}

        # 15位身份证验证
        elif len(id_card) == 15:
            pattern = r'^[1-9]\d{5}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}$'
            if not re.match(pattern, id_card):
                return {'valid': False, 'message': '15位身份证号码格式不正确'}

        # 提取出生日期和性别
        try:
            if len(id_card) == 18:
                birth_date = datetime.strptime(id_card[6:14], '%Y%m%d').date()
                gender = '男' if int(id_card[16]) % 2 == 1 else '女'
            else:
                birth_date = datetime.strptime(f"19{id_card[6:12]}", '%Y%m%d').date()
                gender = '男' if int(id_card[14]) % 2 == 1 else '女'

            # 计算年龄
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            return {
                'valid': True,
                'birth_date': birth_date.strftime('%Y-%m-%d'),
                'age': age,
                'gender': gender,
                'region': id_card[:6]  # 地区代码
            }

        except Exception:
            return {'valid': False, 'message': '身份证号码信息解析失败'}

    @staticmethod
    def validate_name(name: str, min_length: int = 2, max_length: int = 50) -> Dict[str, Any]:
        """
        验证姓名

        Args:
            name: 姓名
            min_length: 最小长度
            max_length: 最大长度

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(name, str):
            return {'valid': False, 'message': '姓名必须是字符串'}

        name = name.strip()

        # 长度验证
        if len(name) < min_length:
            return {'valid': False, 'message': f'姓名长度不能少于{min_length}个字符'}

        if len(name) > max_length:
            return {'valid': False, 'message': f'姓名长度不能超过{max_length}个字符'}

        # 字符验证（允许中文、英文、空格、某些特殊字符）
        pattern = r'^[\u4e00-\u9fa5a-zA-Z\s\-\.]+$'
        if not re.match(pattern, name):
            return {'valid': False, 'message': '姓名只能包含中文、英文、空格、连字符和点'}

        # 检查是否包含数字
        if any(char.isdigit() for char in name):
            return {'valid': False, 'message': '姓名不能包含数字'}

        return {'valid': True, 'normalized': name.strip()}

    @staticmethod
    def validate_student_id(student_id: str) -> Dict[str, Any]:
        """
        验证学号

        Args:
            student_id: 学号

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(student_id, str):
            return {'valid': False, 'message': '学号必须是字符串'}

        student_id = student_id.strip().upper()

        # 基础格式验证
        pattern = r'^[A-Z0-9]{6,20}$'
        if not re.match(pattern, student_id):
            return {'valid': False, 'message': '学号格式不正确，应为6-20位大写字母和数字'}

        # 检查是否包含连续相同的字符
        if len(student_id) >= 3 and any(len(set(student_id[i:i+3])) == 1 for i in range(len(student_id)-2)):
            return {'valid': False, 'message': '学号不能包含连续相同的字符'}

        return {'valid': True, 'normalized': student_id}


class AcademicValidator(BaseValidator):
    """学术信息验证器"""

    @staticmethod
    def validate_course_code(course_code: str) -> Dict[str, Any]:
        """
        验证课程代码

        Args:
            course_code: 课程代码

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(course_code, str):
            return {'valid': False, 'message': '课程代码必须是字符串'}

        course_code = course_code.strip().upper()

        # 常见课程代码格式：ABC123 或 ABC-123 或 ABC1234
        pattern = r'^[A-Z]{2,4}[-]?\d{3,4}$'
        if not re.match(pattern, course_code):
            return {'valid': False, 'message': '课程代码格式不正确'}

        return {'valid': True, 'normalized': course_code.replace('-', '')}

    @staticmethod
    def validate_score(score: Union[str, int, float], max_score: float = 100) -> Dict[str, Any]:
        """
        验证分数

        Args:
            score: 分数
            max_score: 最高分

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            score_value = float(score)
        except (ValueError, TypeError):
            return {'valid': False, 'message': '分数必须是数字'}

        if score_value < 0:
            return {'valid': False, 'message': '分数不能为负数'}

        if score_value > max_score:
            return {'valid': False, 'message': f'分数不能超过{max_score}分'}

        # 检查小数位数（最多两位）
        if abs(score_value * 100 - round(score_value * 100)) > 0.01:
            return {'valid': False, 'message': '分数最多保留两位小数'}

        return {'valid': True, 'value': score_value}

    @staticmethod
    def validate_grade_level(grade_level: str) -> Dict[str, Any]:
        """
        验证年级

        Args:
            grade_level: 年级

        Returns:
            Dict[str, Any]: 验证结果
        """
        valid_grades = ['大一', '大二', '大三', '大四', '研一', '研二', '研三']

        if grade_level not in valid_grades:
            return {
                'valid': False,
                'message': f'年级必须是以下选项之一: {", ".join(valid_grades)}'
            }

        return {'valid': True}

    @staticmethod
    def validate_semester(semester: str) -> Dict[str, Any]:
        """
        验证学期

        Args:
            semester: 学期

        Returns:
            Dict[str, Any]: 验证结果
        """
        pattern = r'^\d{4}-(春|秋|夏)季学期$'
        if not re.match(pattern, semester):
            return {
                'valid': False,
                'message': '学期格式不正确，应为 YYYY-(春|秋|夏)季学期'
            }

        # 验证年份合理性
        year = int(semester.split('-')[0])
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:
            return {'valid': False, 'message': '学期年份不合理'}

        return {'valid': True}

    @staticmethod
    def validate_credits(credits: Union[str, int, float]) -> Dict[str, Any]:
        """
        验证学分

        Args:
            credits: 学分

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            credits_value = float(credits)
        except (ValueError, TypeError):
            return {'valid': False, 'message': '学分必须是数字'}

        if credits_value <= 0:
            return {'valid': False, 'message': '学分必须大于0'}

        if credits_value > 10:
            return {'valid': False, 'message': '学分不能超过10'}

        # 检查是否为0.5的倍数
        if abs(credits_value * 2 - round(credits_value * 2)) > 0.01:
            return {'valid': False, 'message': '学分必须是0.5的倍数'}

        return {'valid': True, 'value': credits_value}


class BusinessValidator(BaseValidator):
    """业务逻辑验证器"""

    @staticmethod
    def validate_url(url: str, allowed_schemes: List[str] = None) -> Dict[str, Any]:
        """
        验证URL

        Args:
            url: URL地址
            allowed_schemes: 允许的协议

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(url, str):
            return {'valid': False, 'message': 'URL必须是字符串'}

        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {'valid': False, 'message': 'URL格式不正确'}

            if allowed_schemes and parsed.scheme not in allowed_schemes:
                return {
                    'valid': False,
                    'message': f'URL协议必须是以下之一: {", ".join(allowed_schemes)}'
                }

            return {'valid': True, 'scheme': parsed.scheme, 'domain': parsed.netloc}

        except Exception:
            return {'valid': False, 'message': 'URL格式不正确'}

    @staticmethod
    def validate_isbn(isbn: str) -> Dict[str, Any]:
        """
        验证ISBN号

        Args:
            isbn: ISBN号

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(isbn, str):
            return {'valid': False, 'message': 'ISBN必须是字符串'}

        isbn = isbn.replace('-', '').replace(' ', '').strip()

        try:
            # 使用isbnlib验证
            if isbnlib.is_isbn10(isbn):
                isbn13 = isbnlib.to_isbn13(isbn)
                return {
                    'valid': True,
                    'type': 'ISBN-10',
                    'isbn13': isbn13,
                    'normalized': isbn13
                }
            elif isbnlib.is_isbn13(isbn):
                return {
                    'valid': True,
                    'type': 'ISBN-13',
                    'isbn13': isbn,
                    'normalized': isbn
                }
            else:
                return {'valid': False, 'message': 'ISBN号格式不正确'}
        except Exception:
            return {'valid': False, 'message': 'ISBN号验证失败'}

    @staticmethod
    def validate_json(json_str: str) -> Dict[str, Any]:
        """
        验证JSON字符串

        Args:
            json_str: JSON字符串

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(json_str, str):
            return {'valid': False, 'message': '必须是JSON字符串'}

        try:
            parsed_json = json.loads(json_str)
            return {
                'valid': True,
                'parsed': parsed_json,
                'type': type(parsed_json).__name__
            }
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'message': f'JSON格式错误: {str(e)}'
            }

    @staticmethod
    def validate_date_range(start_date: str, end_date: str, date_format: str = '%Y-%m-%d') -> Dict[str, Any]:
        """
        验证日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期
            date_format: 日期格式

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            start = datetime.strptime(start_date, date_format)
            end = datetime.strptime(end_date, date_format)

            if start >= end:
                return {'valid': False, 'message': '开始日期必须早于结束日期'}

            return {
                'valid': True,
                'days_difference': (end - start).days,
                'start_date': start,
                'end_date': end
            }

        except ValueError as e:
            return {'valid': False, 'message': f'日期格式错误: {str(e)}'}

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        验证密码强度

        Args:
            password: 密码

        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(password, str):
            return {'valid': False, 'message': '密码必须是字符串'}

        score = 0
        issues = []

        # 长度检查
        if len(password) < 8:
            issues.append('密码长度不能少于8位')
        else:
            score += 1

        # 字符类型检查
        if not re.search(r'[a-z]', password):
            issues.append('密码应包含小写字母')
        else:
            score += 1

        if not re.search(r'[A-Z]', password):
            issues.append('密码应包含大写字母')
        else:
            score += 1

        if not re.search(r'\d', password):
            issues.append('密码应包含数字')
        else:
            score += 1

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            issues.append('密码应包含特殊字符')
        else:
            score += 1

        # 强度等级
        if score <= 2:
            strength = 'weak'
        elif score <= 3:
            strength = 'medium'
        elif score <= 4:
            strength = 'strong'
        else:
            strength = 'very_strong'

        return {
            'valid': score >= 3,
            'strength': strength,
            'score': score,
            'issues': issues
        }


class CompositeValidator:
    """复合验证器"""

    def __init__(self):
        self.errors = []

    def add_validation(self, validator_func, *args, **kwargs) -> 'CompositeValidator':
        """
        添加验证规则

        Args:
            validator_func: 验证函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            CompositeValidator: 自身实例
        """
        result = validator_func(*args, **kwargs)
        if not result['valid']:
            self.errors.append(result['message'])
        return self

    def validate(self, data: Dict[str, Any], rules: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        批量验证

        Args:
            data: 要验证的数据
            rules: 验证规则

        Returns:
            Dict[str, Any]: 验证结果
        """
        self.errors = []

        for field, field_rules in rules.items():
            field_value = data.get(field)
            field_name = field_rules[0].get('field_name', field) if field_rules else field

            for rule in field_rules:
                validator_func = rule.get('validator')
                validator_args = rule.get('args', [])
                validator_kwargs = rule.get('kwargs', {})

                # 如果没有指定field_name，使用字段名
                if 'field_name' not in validator_kwargs:
                    validator_kwargs['field_name'] = field_name

                result = validator_func(field_value, *validator_args, **validator_kwargs)
                if not result['valid']:
                    self.errors.append(result['message'])
                    break  # 该字段验证失败，跳过后续验证

        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors
        }


# 便捷函数
def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证用户数据"""
    validator = CompositeValidator()

    rules = {
        'username': [
            {'validator': PersonalInfoValidator.validate_name, 'args': [2, 20]},
            {'validator': BaseValidator.is_regex_match, 'kwargs': {'pattern': r'^[a-zA-Z0-9_]+$'}}
        ],
        'email': [
            {'validator': PersonalInfoValidator.validate_email}
        ],
        'phone': [
            {'validator': PersonalInfoValidator.validate_phone_number}
        ],
        'id_card': [
            {'validator': PersonalInfoValidator.validate_id_card}
        ]
    }

    return validator.validate(data, rules)


def validate_course_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证课程数据"""
    validator = CompositeValidator()

    rules = {
        'course_code': [
            {'validator': AcademicValidator.validate_course_code}
        ],
        'name': [
            {'validator': BaseValidator.is_required},
            {'validator': BaseValidator.is_length, 'kwargs': {'min_length': 2, 'max_length': 100}}
        ],
        'credits': [
            {'validator': AcademicValidator.validate_credits}
        ],
        'capacity': [
            {'validator': BaseValidator.is_numeric, 'kwargs': {'min_value': 1, 'max_value': 1000}}
        ]
    }

    return validator.validate(data, rules)


def validate_grade_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证成绩数据"""
    validator = CompositeValidator()

    rules = {
        'score': [
            {'validator': AcademicValidator.validate_score}
        ],
        'semester': [
            {'validator': AcademicValidator.validate_semester}
        ]
    }

    return validator.validate(data, rules)