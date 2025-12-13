#!/usr/bin/env python3
# ========================================
# 学生信息管理系统 - 开发环境启动脚本
# ========================================

import os
import sys
import subprocess
import time
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'

def check_python():
    """检查Python环境"""
    print("检查Python环境...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")

def check_node():
    """检查Node.js环境"""
    print("检查Node.js环境...")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Node.js版本: {result.stdout.strip()}")
        else:
            print("错误: 未找到Node.js，请先安装Node.js")
            sys.exit(1)
    except FileNotFoundError:
        print("错误: 未找到Node.js，请先安装Node.js")
        sys.exit(1)

def install_backend_dependencies():
    """安装后端依赖"""
    print("安装后端依赖...")
    venv_dir = BACKEND_DIR / 'venv'

    # 创建虚拟环境（如果不存在）
    if not venv_dir.exists():
        print("创建虚拟环境...")
        subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)

    # 激活虚拟环境并安装依赖
    if os.name == 'nt':  # Windows
        pip_path = venv_dir / 'Scripts' / 'pip'
        python_path = venv_dir / 'Scripts' / 'python'
    else:  # Unix-like
        pip_path = venv_dir / 'bin' / 'pip'
        python_path = venv_dir / 'bin' / 'python'

    # 升级pip
    subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)

    # 安装依赖
    requirements_file = BACKEND_DIR / 'requirements.txt'
    if requirements_file.exists():
        subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], check=True)
        print("后端依赖安装完成！")
    else:
        print("警告: 未找到requirements.txt文件")

def install_frontend_dependencies():
    """安装前端依赖"""
    print("安装前端依赖...")
    os.chdir(FRONTEND_DIR)

    # 检查package.json是否存在
    if not (FRONTEND_DIR / 'package.json').exists():
        print("错误: 未找到package.json文件")
        sys.exit(1)

    # 安装依赖
    subprocess.run(['npm', 'install'], check=True)
    print("前端依赖安装完成！")

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    os.chdir(BACKEND_DIR)

    venv_dir = BACKEND_DIR / 'venv'
    if os.name == 'nt':  # Windows
        python_path = venv_dir / 'Scripts' / 'python'
    else:  # Unix-like
        python_path = venv_dir / 'bin' / 'python'

    # 运行数据库初始化脚本
    init_script = BACKEND_DIR / 'scripts' / 'init_database.py'
    if init_script.exists():
        subprocess.run([str(python_path), str(init_script)], check=True)
        print("数据库初始化完成！")
    else:
        print("警告: 未找到数据库初始化脚本")

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    os.chdir(BACKEND_DIR)

    venv_dir = BACKEND_DIR / 'venv'
    if os.name == 'nt':  # Windows
        python_path = venv_dir / 'Scripts' / 'python'
    else:  # Unix-like
        python_path = venv_dir / 'bin' / 'python'

    # 启动Flask应用
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'

    backend_process = subprocess.Popen(
        [str(python_path), 'app.py'],
        env=env,
        cwd=BACKEND_DIR
    )

    return backend_process

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")
    os.chdir(FRONTEND_DIR)

    # 启动Vue开发服务器
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=FRONTEND_DIR
    )

    return frontend_process

def main():
    """主函数"""
    print("=" * 50)
    print("学生信息管理系统 - 开发环境启动")
    print("=" * 50)

    # 检查环境
    check_python()
    check_node()

    # 安装依赖
    install_backend_dependencies()
    install_frontend_dependencies()

    # 初始化数据库
    init_database()

    print("\n正在启动服务...")

    # 启动后端服务
    backend_process = start_backend()
    print("后端服务启动成功！地址: http://localhost:5000")

    # 等待后端服务启动
    time.sleep(2)

    # 启动前端服务
    frontend_process = start_frontend()
    print("前端服务启动成功！地址: http://localhost:3000")

    print("\n" + "=" * 50)
    print("系统启动完成！")
    print("前端地址: http://localhost:3000")
    print("后端API: http://localhost:5000")
    print("API文档: http://localhost:5000/docs")
    print("\n默认管理员账号:")
    print("用户名: admin")
    print("密码: 123456")
    print("=" * 50)

    try:
        # 等待服务结束
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("服务已停止")

if __name__ == '__main__':
    main()