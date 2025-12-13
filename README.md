# 学生信息管理系统

基于 Flask + Vue 3 + Element Plus 的现代化学生信息管理系统。

## 系统功能

### 用户管理
- 多角色用户系统（管理员、教师、学生）
- 用户认证与权限控制
- 个人资料管理

### 学生管理
- 学生信息维护
- 学籍状态管理
- 学生档案查询

### 教师管理
- 教师信息管理
- 教师课程分配
- 教学工作量统计

### 课程管理
- 课程信息维护
- 课程发布与管理
- 课程资源管理

### 选课管理
- 学生在线选课
- 选课审核流程
- 选课冲突检测

### 成绩管理
- 成绩录入与发布
- 成绩统计分析
- 成绩单打印

### 消息通知
- 系统公告发布
- 个人消息管理
- 消息模板管理

### 系统管理
- 系统配置管理
- 用户权限管理
- 操作日志记录
- 数据备份恢复
- 系统监控统计

## 技术架构

### 后端技术栈
- **框架**: Flask 2.3+
- **数据库**: SQLite (开发) / MySQL (生产)
- **ORM**: SQLAlchemy + Flask-Migrate
- **认证**: JWT + Flask-JWT-Extended
- **API文档**: Flask-RESTX (Swagger)
- **缓存**: Flask-Caching + Redis
- **任务队列**: Celery + Redis
- **邮件**: Flask-Mail
- **实时通信**: Flask-SocketIO
- **限流**: Flask-Limiter

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: ECharts
- **样式**: SCSS

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Redis (可选，用于缓存和任务队列)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd studentproject
```

2. **使用一键启动脚本**

Windows:
```bash
start_dev.bat
```

Linux/Mac:
```bash
python start_dev.py
```

3. **手动安装（可选）**

后端设置:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_database.py
python app.py
```

前端设置:
```bash
cd frontend
npm install
npm run dev
```

### 访问系统
- 前端界面: http://localhost:3000
- 后端API: http://localhost:5000
- API文档: http://localhost:5000/docs

### 默认账号
- 管理员: admin / 123456
- 教师: teacher001 / 123456
- 学生: student001 / 123456

## 项目结构

```
studentproject/
├── backend/                 # 后端代码
│   ├── api/                # API路由
│   ├── models/             # 数据模型
│   ├── schemas/            # 数据序列化
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具函数
│   ├── scripts/            # 脚本文件
│   ├── config.py           # 配置文件
│   ├── app.py              # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/            # API接口
│   │   ├── components/     # 组件
│   │   ├── layouts/        # 布局
│   │   ├── router/         # 路由
│   │   ├── stores/         # 状态管理
│   │   ├── styles/         # 样式
│   │   ├── types/          # TypeScript类型
│   │   ├── utils/          # 工具函数
│   │   └── views/          # 页面
│   ├── package.json        # 前端依赖
│   └── vite.config.ts      # Vite配置
├── start_dev.py            # 开发启动脚本
├── start_dev.bat           # Windows启动脚本
└── README.md               # 项目说明
```

## 开发指南

### 后端开发
1. 所有API路由放在 `backend/api/` 目录
2. 数据模型定义在 `backend/models/` 目录
3. 业务逻辑实现在 `backend/services/` 目录
4. 使用Flask-RESTX进行API文档生成

### 前端开发
1. 页面组件放在 `frontend/src/views/` 目录
2. 通用组件放在 `frontend/src/components/` 目录
3. API接口定义在 `frontend/src/api/` 目录
4. 使用TypeScript进行类型检查

### 数据库操作
```bash
# 创建迁移
flask db migrate -m "描述"

# 应用迁移
flask db upgrade

# 初始化数据库
python scripts/init_database.py

# 填充测试数据
python scripts/seed_data.py
```

## API文档
启动后端服务后，访问 http://localhost:5000/docs 查看完整的API文档。

## 部署说明

### 生产环境配置
1. 修改 `backend/config.py` 中的生产环境配置
2. 设置环境变量：
   - `FLASK_ENV=production`
   - `DATABASE_URL` (数据库连接)
   - `SECRET_KEY` (应用密钥)
   - `JWT_SECRET_KEY` (JWT密钥)

### Docker部署
```bash
# 构建镜像
docker build -t student-management .

# 运行容器
docker run -p 5000:5000 student-management
```

## 常见问题

1. **端口冲突**: 修改前端或后端的端口配置
2. **数据库连接失败**: 检查数据库服务是否启动
3. **依赖安装失败**: 使用国内镜像源安装依赖

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。