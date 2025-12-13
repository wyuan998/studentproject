# ========================================
# 学生信息管理系统 - 邮件工具类
# ========================================

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import threading
import uuid
from jinja2 import Template

from flask import current_app, render_template_string
from ..utils.rate_limit import check_rate_limit


class EmailService:
    """邮件服务"""

    def __init__(self):
        self.smtp_server = current_app.config.get('SMTP_SERVER')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.smtp_username = current_app.config.get('SMTP_USERNAME')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD')
        self.use_tls = current_app.config.get('SMTP_USE_TLS', True)
        self.use_ssl = current_app.config.get('SMTP_USE_SSL', False)
        self.default_sender = current_app.config.get('DEFAULT_FROM_EMAIL')
        self.from_name = current_app.config.get('FROM_NAME', '学生信息管理系统')

        # 邮件模板缓存
        self.template_cache = {}

    def send_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        content: str,
        content_type: str = 'html',
        cc_emails: Union[str, List[str]] = None,
        bcc_emails: Union[str, List[str]] = None,
        attachments: List[str] = None,
        reply_to: str = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        发送邮件

        Args:
            to_emails: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型 ('html' 或 'plain')
            cc_emails: 抄送邮箱
            bcc_emails: 密送邮箱
            attachments: 附件列表
            reply_to: 回复邮箱
            headers: 自定义邮件头

        Returns:
            Dict[str, Any]: 发送结果
        """
        try:
            # 检查限流
            if not check_rate_limit('email', '10/hour'):
                return {
                    'success': False,
                    'error': '邮件发送频率超限',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }

            # 规范化邮箱地址
            to_emails = self._normalize_emails(to_emails)
            cc_emails = self._normalize_emails(cc_emails) if cc_emails else []
            bcc_emails = self._normalize_emails(bcc_emails) if bcc_emails else []

            # 创建邮件对象
            message = MIMEMultipart()
            message['From'] = f"{self.from_name} <{self.default_sender}>"
            message['To'] = ', '.join(to_emails)
            message['Subject'] = subject

            if cc_emails:
                message['Cc'] = ', '.join(cc_emails)
            if reply_to:
                message['Reply-To'] = reply_to

            # 添加自定义头部
            if headers:
                for key, value in headers.items():
                    message[key] = value

            # 添加邮件内容
            if content_type == 'html':
                message.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                message.attach(MIMEText(content, 'plain', 'utf-8'))

            # 添加附件
            if attachments:
                for file_path in attachments:
                    self._add_attachment(message, file_path)

            # 发送邮件
            result = self._send_smtp_message(message, to_emails + cc_emails + bcc_emails)

            return {
                'success': True,
                'message_id': result.get('message_id', str(uuid.uuid4())),
                'recipients': to_emails + cc_emails + bcc_emails,
                'sent_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f"邮件发送失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'SEND_FAILED'
            }

    def send_template_email(
        self,
        to_emails: Union[str, List[str]],
        template_name: str,
        context: Dict[str, Any],
        subject_template: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送模板邮件

        Args:
            to_emails: 收件人邮箱
            template_name: 模板名称
            context: 模板上下文
            subject_template: 主题模板
            **kwargs: 其他send_email参数

        Returns:
            Dict[str, Any]: 发送结果
        """
        try:
            # 渲染邮件内容
            content = self.render_template(template_name, context)

            # 渲染主题
            subject = subject_template or self._get_default_subject(template_name)
            if subject and isinstance(subject, str) and '{' in subject:
                subject = Template(subject).render(**context)

            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                content=content,
                content_type='html',
                **kwargs
            )

        except Exception as e:
            current_app.logger.error(f"模板邮件发送失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'TEMPLATE_RENDER_FAILED'
            }

    def send_async_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        content: str,
        **kwargs
    ) -> str:
        """
        异步发送邮件

        Args:
            to_emails: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            **kwargs: 其他send_email参数

        Returns:
            str: 任务ID
        """
        task_id = str(uuid.uuid4())

        def send_in_background():
            try:
                self.send_email(to_emails, subject, content, **kwargs)
                current_app.logger.info(f"异步邮件发送完成: {task_id}")
            except Exception as e:
                current_app.logger.error(f"异步邮件发送失败: {task_id}, 错误: {str(e)}")

        # 启动后台线程
        thread = threading.Thread(target=send_in_background)
        thread.daemon = True
        thread.start()

        return task_id

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染邮件模板

        Args:
            template_name: 模板名称
            context: 模板上下文

        Returns:
            str: 渲染后的内容
        """
        # 检查缓存
        cache_key = f"email_template:{template_name}"
        if cache_key in self.template_cache:
            template = self.template_cache[cache_key]
        else:
            # 加载模板
            template_content = self._load_template_content(template_name)
            if not template_content:
                raise ValueError(f"模板不存在: {template_name}")

            template = Template(template_content)
            self.template_cache[cache_key] = template

        # 添加全局上下文
        global_context = {
            'app_name': current_app.config.get('APP_NAME', '学生信息管理系统'),
            'support_email': current_app.config.get('SUPPORT_EMAIL', 'support@example.com'),
            'current_year': datetime.now().year,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 合并上下文
        full_context = {**global_context, **context}

        return template.render(**full_context)

    def _normalize_emails(self, emails: Union[str, List[str]]) -> List[str]:
        """规范化邮箱地址列表"""
        if isinstance(emails, str):
            emails = [email.strip() for email in emails.split(',') if email.strip()]
        elif isinstance(emails, list):
            emails = [email.strip() for email in emails if email.strip()]
        else:
            emails = []

        return emails

    def _add_attachment(self, message: MIMEMultipart, file_path: str):
        """添加附件"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"附件不存在: {file_path}")

            with open(path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {path.name}'
            )

            message.attach(part)

        except Exception as e:
            current_app.logger.warning(f"添加附件失败: {file_path}, 错误: {str(e)}")

    def _send_smtp_message(self, message: MIMEMultipart, recipients: List[str]) -> Dict[str, Any]:
        """通过SMTP发送邮件"""
        try:
            if self.use_ssl:
                # 使用SSL连接
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    result = server.send_message(message, to_addrs=recipients)
            else:
                # 使用普通连接
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    result = server.send_message(message, to_addrs=recipients)

            return {'message_id': str(uuid.uuid4()), 'recipients': result}

        except Exception as e:
            current_app.logger.error(f"SMTP发送失败: {str(e)}")
            raise

    def _load_template_content(self, template_name: str) -> str:
        """加载邮件模板内容"""
        # 尝试从不同位置加载模板
        template_paths = [
            f"templates/email/{template_name}.html",
            f"backend/templates/email/{template_name}.html",
            f"email_templates/{template_name}.html"
        ]

        for template_path in template_paths:
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                continue

        # 返回默认模板
        return self._get_default_template(template_name)

    def _get_default_template(self, template_name: str) -> str:
        """获取默认模板"""
        default_templates = {
            'welcome': """
            <html>
            <body>
                <h2>欢迎加入学生信息管理系统</h2>
                <p>尊敬的 {{ name }}：</p>
                <p>欢迎您注册学生信息管理系统！您的账号已创建成功。</p>
                <p>登录信息：</p>
                <ul>
                    <li>用户名：{{ username }}</li>
                    <li>邮箱：{{ email }}</li>
                </ul>
                <p>请妥善保管您的账号信息。</p>
                <p>如有问题，请联系我们：{{ support_email }}</p>
                <p>祝好！<br>{{ app_name }} 团队</p>
            </body>
            </html>
            """,
            'password_reset': """
            <html>
            <body>
                <h2>密码重置请求</h2>
                <p>您好，{{ name }}：</p>
                <p>我们收到了您的密码重置请求。请点击以下链接重置密码：</p>
                <p><a href="{{ reset_url }}">重置密码</a></p>
                <p>如果链接无法点击，请复制以下地址到浏览器：</p>
                <p>{{ reset_url }}</p>
                <p>此链接将在24小时后过期。</p>
                <p>如果您没有请求重置密码，请忽略此邮件。</p>
                <p>祝好！<br>{{ app_name }} 团队</p>
            </body>
            </html>
            """,
            'notification': """
            <html>
            <body>
                <h2>{{ title }}</h2>
                <p>{{ message }}</p>
                {% if details %}
                <p>详细信息：</p>
                <ul>
                    {% for key, value in details.items() %}
                    <li>{{ key }}：{{ value }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                <p>请登录系统查看详情。</p>
                <p>祝好！<br>{{ app_name }} 团队</p>
            </body>
            </html>
            """
        }

        return default_templates.get(template_name, "<html><body>{{ content }}</body></html>")

    def _get_default_subject(self, template_name: str) -> str:
        """获取默认主题"""
        subjects = {
            'welcome': '欢迎加入学生信息管理系统',
            'password_reset': '密码重置请求',
            'notification': '系统通知',
            'enrollment_approved': '选课申请已批准',
            'enrollment_rejected': '选课申请已拒绝',
            'grade_published': '成绩已发布',
            'system_maintenance': '系统维护通知'
        }

        return subjects.get(template_name, '来自学生信息管理系统的通知')


class EmailQueue:
    """邮件队列"""

    def __init__(self):
        self.queue = []

    def add_email(self, email_data: Dict[str, Any]) -> str:
        """
        添加邮件到队列

        Args:
            email_data: 邮件数据

        Returns:
            str: 队列ID
        """
        queue_id = str(uuid.uuid4())
        email_data.update({
            'queue_id': queue_id,
            'created_at': datetime.utcnow(),
            'status': 'pending',
            'retry_count': 0
        })

        self.queue.append(email_data)
        return queue_id

    def process_queue(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        处理邮件队列

        Args:
            batch_size: 批处理大小

        Returns:
            Dict[str, Any]: 处理结果
        """
        email_service = EmailService()
        processed = 0
        failed = 0

        # 获取待处理的邮件
        pending_emails = [email for email in self.queue if email['status'] == 'pending'][:batch_size]

        for email_data in pending_emails:
            try:
                result = email_service.send_email(
                    to_emails=email_data['to_emails'],
                    subject=email_data['subject'],
                    content=email_data['content'],
                    **email_data.get('extra_args', {})
                )

                if result['success']:
                    email_data['status'] = 'sent'
                    email_data['sent_at'] = datetime.utcnow()
                    processed += 1
                else:
                    email_data['status'] = 'failed'
                    email_data['error'] = result['error']
                    failed += 1

            except Exception as e:
                email_data['status'] = 'failed'
                email_data['error'] = str(e)
                failed += 1

        return {
            'processed': processed,
            'failed': failed,
            'remaining': len([email for email in self.queue if email['status'] == 'pending'])
        }

    def clear_sent_emails(self, days: int = 7) -> int:
        """
        清理已发送的邮件

        Args:
            days: 保留天数

        Returns:
            int: 清理数量
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        original_count = len(self.queue)

        self.queue = [
            email for email in self.queue
            if not (email['status'] == 'sent' and
                   email.get('sent_at') and
                   email['sent_at'] < cutoff_time)
        ]

        return original_count - len(self.queue)


# 预定义邮件模板
class EmailTemplates:
    """邮件模板类"""

    @staticmethod
    def welcome_email(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """欢迎邮件"""
        return {
            'template': 'welcome',
            'subject': '欢迎加入学生信息管理系统',
            'context': {
                'name': user_data.get('name', '用户'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'login_url': user_data.get('login_url', '/login')
            }
        }

    @staticmethod
    def password_reset(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """密码重置邮件"""
        return {
            'template': 'password_reset',
            'subject': '密码重置请求',
            'context': {
                'name': user_data.get('name', '用户'),
                'reset_url': user_data.get('reset_url'),
                'expiry_hours': 24
            }
        }

    @staticmethod
    def enrollment_notification(enrollment_data: Dict[str, Any]) -> Dict[str, Any]:
        """选课通知邮件"""
        status = enrollment_data.get('status', 'pending')
        if status == 'approved':
            subject = '选课申请已批准'
        elif status == 'rejected':
            subject = '选课申请已拒绝'
        else:
            subject = '选课申请处理中'

        return {
            'template': 'notification',
            'subject': subject,
            'context': {
                'title': subject,
                'message': f'您的选课申请状态已更新：{status}',
                'details': {
                    '课程名称': enrollment_data.get('course_name'),
                    '课程代码': enrollment_data.get('course_code'),
                    '申请时间': enrollment_data.get('applied_at'),
                    '状态': status
                }
            }
        }

    @staticmethod
    def grade_notification(grade_data: Dict[str, Any]) -> Dict[str, Any]:
        """成绩发布通知"""
        return {
            'template': 'notification',
            'subject': '成绩已发布',
            'context': {
                'title': '成绩发布通知',
                'message': '您的课程成绩已发布，请登录系统查看。',
                'details': {
                    '课程名称': grade_data.get('course_name'),
                    '课程代码': grade_data.get('course_code'),
                    '学期': grade_data.get('semester'),
                    '发布时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        }

    @staticmethod
    def system_maintenance(maintenance_data: Dict[str, Any]) -> Dict[str, Any]:
        """系统维护通知"""
        return {
            'template': 'notification',
            'subject': '系统维护通知',
            'context': {
                'title': '系统维护通知',
                'message': '系统将进行维护升级，届时服务将暂时不可用。',
                'details': {
                    '维护时间': maintenance_data.get('maintenance_time'),
                    '预计时长': maintenance_data.get('duration', '2小时'),
                    '影响范围': '全系统'
                }
            }
        }


# 全局邮件队列实例
email_queue = EmailQueue()


# 便捷函数
def send_welcome_email(user_email: str, user_data: Dict[str, Any], async_send: bool = True) -> Dict[str, Any]:
    """发送欢迎邮件"""
    email_service = EmailService()
    template = EmailTemplates.welcome_email(user_data)

    if async_send:
        task_id = email_service.send_async_email(
            to_emails=user_email,
            subject=template['subject'],
            content=email_service.render_template(template['template'], template['context'])
        )
        return {'success': True, 'task_id': task_id}
    else:
        return email_service.send_template_email(
            to_emails=user_email,
            template_name=template['template'],
            context=template['context'],
            subject_template=template['subject']
        )


def send_password_reset_email(user_email: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """发送密码重置邮件"""
    email_service = EmailService()
    template = EmailTemplates.password_reset(user_data)

    return email_service.send_template_email(
        to_emails=user_email,
        template_name=template['template'],
        context=template['context'],
        subject_template=template['subject']
    )


def send_notification_email(
    user_email: str,
    title: str,
    message: str,
    details: Dict[str, Any] = None,
    async_send: bool = True
) -> Dict[str, Any]:
    """发送通知邮件"""
    email_service = EmailService()

    template_data = {
        'title': title,
        'message': message,
        'details': details
    }

    if async_send:
        task_id = email_service.send_async_email(
            to_emails=user_email,
            subject=title,
            content=email_service.render_template('notification', template_data)
        )
        return {'success': True, 'task_id': task_id}
    else:
        return email_service.send_template_email(
            to_emails=user_email,
            template_name='notification',
            context=template_data,
            subject_template=title
        )