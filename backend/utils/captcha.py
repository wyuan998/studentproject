# ========================================
# 学生信息管理系统 - 验证码工具类
# ========================================

import random
import string
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import hashlib


def generate_captcha_text(length=4):
    """生成验证码文本"""
    # 生成包含数字和字母的验证码
    characters = string.digits + string.ascii_uppercase
    return ''.join(random.choices(characters, k=length))


def generate_captcha_image(width=120, height=40):
    """生成验证码图片"""
    # 生成验证码文本
    captcha_text = generate_captcha_text()
    captcha_id = hashlib.md5(f"{captcha_text}_{random.random()}".encode()).hexdigest()

    # 创建图片
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

    # 噪点
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(0, 255),
                                random.randint(0, 255),
                                random.randint(0, 255)))

    # 验证码文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()

    # 绘制每个字符，添加随机偏移和旋转
    for i, char in enumerate(captcha_text):
        x = 20 + i * 25 + random.randint(-5, 5)
        y = 8 + random.randint(-5, 5)

        # 随机颜色
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


def verify_captcha(captcha_id, captcha_text, redis_client):
    """验证验证码"""
    if not captcha_id or not captcha_text:
        return False

    # 从Redis获取验证码
    stored_captcha = redis_client.get(f"captcha:{captcha_id}")

    if not stored_captcha:
        return False

    # 验证码不区分大小写
    return stored_captcha.lower() == captcha_text.lower()


def store_captcha(captcha_data, redis_client, expire_time=300):
    """存储验证码到Redis"""
    redis_client.setex(
        f"captcha:{captcha_data['captcha_id']}",
        expire_time,
        captcha_data['captcha_text']
    )
    return captcha_data['captcha_id']