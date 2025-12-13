@echo off
chcp 65001 >nul
title 学生信息管理系统 - 开发环境启动

echo ========================================
echo 学生信息管理系统 - 开发环境启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 进入后端目录
cd /d "%~dp0backend"

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 升级pip
python -m pip install --upgrade pip

REM 安装后端依赖
if exist requirements.txt (
    echo 安装后端依赖...
    pip install -r requirements.txt
) else (
    echo 警告: 未找到requirements.txt文件
)

REM 初始化数据库
if exist scripts\init_database.py (
    echo 初始化数据库...
    python scripts\init_database.py
) else (
    echo 警告: 未找到数据库初始化脚本
)

REM 启动后端服务
echo 启动后端服务...
start "后端服务" cmd /k "python app.py"

REM 等待后端服务启动
timeout /t 3 /nobreak >nul

REM 进入前端目录
cd /d "%~dp0frontend"

REM 安装前端依赖
if exist package.json (
    echo 安装前端依赖...
    call npm install
) else (
    echo 错误: 未找到package.json文件
    pause
    exit /b 1
)

REM 启动前端服务
echo 启动前端服务...
start "前端服务" cmd /k "npm run dev"

echo.
echo ========================================
echo 系统启动完成！
echo 前端地址: http://localhost:3000
echo 后端API: http://localhost:5000
echo API文档: http://localhost:5000/docs
echo.
echo 默认管理员账号:
echo 用户名: admin
echo 密码: 123456
echo ========================================
echo.
echo 按任意键退出...
pause >nul