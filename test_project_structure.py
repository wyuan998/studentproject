#!/usr/bin/env python3
# ========================================
# 学生信息管理系统 - 简化测试脚本
# ========================================

import os
import sys
from pathlib import Path

def check_project_structure():
    """检查项目结构"""
    print("=" * 50)
    print("Checking project structure...")
    print("=" * 50)

    project_root = Path(__file__).parent

    # 检查主要目录
    required_dirs = [
        'backend',
        'frontend',
        'backend/api',
        'backend/models',
        'backend/schemas',
        'backend/services',
        'backend/utils',
        'frontend/src',
        'frontend/src/api',
        'frontend/src/components',
        'frontend/src/views',
        'frontend/src/stores'
    ]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        status = "[OK]" if full_path.exists() else "[MISSING]"
        print(f"{status} {dir_path}")

    print("\n" + "=" * 50)
    print("Checking key files...")
    print("=" * 50)

    # 检查关键文件
    required_files = [
        'backend/app.py',
        'backend/config.py',
        'backend/extensions.py',
        'backend/requirements.txt',
        'backend/scripts/init_database.py',
        'frontend/package.json',
        'frontend/src/main.ts',
        'frontend/src/App.vue',
        'frontend/src/router/index.ts',
        'start_dev.py',
        'README.md'
    ]

    for file_path in required_files:
        full_path = project_root / file_path
        status = "[OK]" if full_path.exists() else "[MISSING]"
        print(f"{status} {file_path}")

def check_api_modules():
    """检查API模块"""
    print("\n" + "=" * 50)
    print("Checking frontend API modules...")
    print("=" * 50)

    api_files = [
        'frontend/src/api/request.ts',
        'frontend/src/api/auth.ts',
        'frontend/src/api/user.ts',
        'frontend/src/api/student.ts',
        'frontend/src/api/teacher.ts',
        'frontend/src/api/course.ts',
        'frontend/src/api/enrollment.ts',
        'frontend/src/api/grade.ts',
        'frontend/src/api/message.ts',
        'frontend/src/api/system.ts',
        'frontend/src/api/report.ts'
    ]

    project_root = Path(__file__).parent

    for api_file in api_files:
        full_path = project_root / api_file
        status = "[OK]" if full_path.exists() else "[MISSING]"
        print(f"{status} {api_file}")

def check_backend_modules():
    """检查后端模块"""
    print("\n" + "=" * 50)
    print("Checking backend modules...")
    print("=" * 50)

    backend_files = [
        'backend/api/__init__.py',
        'backend/api/auth.py',
        'backend/api/users.py',
        'backend/api/students.py',
        'backend/api/teachers.py',
        'backend/api/courses.py',
        'backend/api/enrollments.py',
        'backend/api/grades.py',
        'backend/api/messages.py',
        'backend/api/system_config.py',
        'backend/api/reports.py',
        'backend/models/__init__.py',
        'backend/models/user.py',
        'backend/models/student.py',
        'backend/models/teacher.py',
        'backend/models/course.py',
        'backend/models/enrollment.py',
        'backend/models/grade.py',
        'backend/models/message.py'
    ]

    project_root = Path(__file__).parent

    for backend_file in backend_files:
        full_path = project_root / backend_file
        status = "[OK]" if full_path.exists() else "[MISSING]"
        print(f"{status} {backend_file}")

def check_frontend_components():
    """检查前端组件"""
    print("\n" + "=" * 50)
    print("Checking frontend components...")
    print("=" * 50)

    component_files = [
        'frontend/src/views/auth/Login.vue',
        'frontend/src/views/dashboard/Dashboard.vue',
        'frontend/src/views/student/StudentList.vue',
        'frontend/src/views/teacher/TeacherList.vue',
        'frontend/src/views/course/CourseList.vue',
        'frontend/src/views/enrollment/EnrollmentList.vue',
        'frontend/src/views/grade/GradeList.vue',
        'frontend/src/components/layout/AppHeader.vue',
        'frontend/src/components/layout/AppSidebar.vue',
        'frontend/src/stores/user.ts',
        'frontend/src/stores/app.ts'
    ]

    project_root = Path(__file__).parent

    for component_file in component_files:
        full_path = project_root / component_file
        status = "[OK]" if full_path.exists() else "[MISSING]"
        print(f"{status} {component_file}")

def main():
    """主函数"""
    print("Student Management System - Project Structure Test")

    check_project_structure()
    check_api_modules()
    check_backend_modules()
    check_frontend_components()

    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)
    print("Project structure completeness check:")
    print("[OK] = File/Directory exists")
    print("[MISSING] = File/Directory missing")
    print("\nIf you see many [MISSING] tags, the project structure is incomplete")
    print("If you see many [OK] tags, the project structure is complete")

if __name__ == '__main__':
    main()