#!/usr/bin/env python3
"""
简化的注册功能测试服务器
"""

import json
import uuid
import hashlib
import random
from datetime import datetime
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

app = Flask(__name__)

# 模拟数据库
users_db = {}
captchas_db = {}

def generate_captcha_image():
    """生成验证码图片"""
    # 生成验证码文本
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    captcha_text = ''.join(random.choices(characters, k=4))
    captcha_id = hashlib.md5(f"{captcha_text}_{random.random()}".encode()).hexdigest()

    # 创建图片
    width, height = 120, 40
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 背景
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=(random.randint(220, 255),
                                     random.randint(220, 255),
                                     random.randint(220, 255)))

    # 干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255),
                                              random.randint(0, 255),
                                              random.randint(0, 255)), width=1)

    # 验证码文字
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    for i, char in enumerate(captcha_text):
        x = 20 + i * 25 + random.randint(-3, 3)
        y = 8 + random.randint(-3, 3)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, font=font, fill=color)

    # 转换为base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        'captcha_id': captcha_id,
        'captcha_text': captcha_text,
        'captcha_image': f"data:image/png;base64,{image_base64}"
    }

@app.route('/auth/captcha', methods=['GET'])
def get_captcha():
    """获取验证码"""
    try:
        captcha_data = generate_captcha_image()
        captchas_db[captcha_data['captcha_id']] = captcha_data['captcha_text']
        return jsonify({
            'success': True,
            'message': '验证码生成成功',
            'data': {
                'captcha_id': captcha_data['captcha_id'],
                'captcha_image': captcha_data['captcha_image']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/auth/check-username', methods=['POST'])
def check_username():
    """检查用户名是否可用"""
    try:
        data = request.json
        username = data.get('value', '').strip()

        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            }), 400

        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': '用户名长度至少为3位'
            }), 400

        if username in [user['username'] for user in users_db.values()]:
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 409

        return jsonify({
            'success': True,
            'message': '用户名可用'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/auth/check-email', methods=['POST'])
def check_email():
    """检查邮箱是否可用"""
    try:
        data = request.json
        email = data.get('value', '').strip()

        if not email:
            return jsonify({
                'success': False,
                'message': '邮箱不能为空'
            }), 400

        if email in [user['email'] for user in users_db.values()]:
            return jsonify({
                'success': False,
                'message': '邮箱已被注册'
            }), 409

        return jsonify({
            'success': True,
            'message': '邮箱可用'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        captcha_id = data.get('captcha_id')
        captcha = data.get('captcha')

        # 验证验证码
        if not captcha_id or captcha_id not in captchas_db:
            return jsonify({
                'success': False,
                'message': '验证码ID无效'
            }), 400

        if captcha.lower() != captchas_db[captcha_id].lower():
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        # 清除已使用的验证码
        del captchas_db[captcha_id]

        # 检查必填字段
        required_fields = ['username', 'email', 'password', 'confirm_password', 'phone', 'real_name', 'student_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} 是必填字段'
                }), 400

        # 验证密码确认
        if data['password'] != data['confirm_password']:
            return jsonify({
                'success': False,
                'message': '密码确认不匹配'
            }), 400

        # 检查用户名和邮箱是否已存在
        if data['username'] in [user['username'] for user in users_db.values()]:
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 409

        if data['email'] in [user['email'] for user in users_db.values()]:
            return jsonify({
                'success': False,
                'message': '邮箱已被注册'
            }), 409

        # 创建用户
        user_id = str(uuid.uuid4())
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()

        users_db[user_id] = {
            'id': user_id,
            'username': data['username'],
            'email': data['email'],
            'password_hash': password_hash,
            'phone': data['phone'],
            'real_name': data['real_name'],
            'student_id': data['student_id'],
            'role': 'student',
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        print(f"新用户注册成功: {data['username']} ({data['email']})")
        print(f"当前用户数量: {len(users_db)}")

        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'user_id': user_id,
                'username': data['username'],
                'email': data['email']
            }
        })

    except Exception as e:
        print(f"注册错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'message': '测试服务器运行正常',
        'user_count': len(users_db),
        'captcha_count': len(captchas_db)
    })

if __name__ == '__main__':
    print("注册功能测试服务器启动中...")
    print("服务地址: http://localhost:5001")
    print("验证码API: http://localhost:5001/auth/captcha")
    print("注册API: http://localhost:5001/auth/register")
    print("健康检查: http://localhost:5001/health")
    print("\n按 Ctrl+C 停止服务器\n")

    app.run(host='0.0.0.0', port=5001, debug=True)