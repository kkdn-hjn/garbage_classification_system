# 基于百度智能云的垃圾分类识别系统

后台管理系统，包含用户登录注册、角色权限、登录日志等功能。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + MySQL
- **前端**: Vue 3 + Vite + Pinia + Vue Router

## 项目结构

```
garbage_classification_system/
├── backend/          # FastAPI 后端
│   ├── routers/      # 路由：auth, users, admin
│   ├── core/         # 安全、日志
│   ├── models.py     # 数据模型
│   └── main.py
└── frontend/         # Vue 3 前端
    └── src/
```

## 快速开始

### 1. 数据库

创建 MySQL 数据库 `garbage_db`：

```sql
CREATE DATABASE garbage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

复制 `.env.example` 为 `.env` 并配置数据库连接：

```bash
cd backend
cp .env.example .env
# 编辑 .env 中的 DATABASE_URL
```

### 2. 后端

```bash
cd backend
pip install -r requirements.txt
python init_db.py   # 初始化表并创建默认管理员 admin / admin123
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5174

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 功能说明

- **登录/注册**: 左右分栏布局，左侧品牌区，右侧表单
- **角色权限**: 管理员(role=1) / 普通用户(role=2)，管理员可访问用户管理、系统管理
- **登录日志**: 系统管理页可查看认证日志（登录/注册成功或失败），支持按类型、级别、关键词筛选
