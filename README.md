# 垃圾图片分类系统 - 用户管理模块

一个基于 Flask 的垃圾分类识别系统，提供完整的用户认证和管理功能。

## 📋 项目概述

本项目是一个垃圾图片分类系统的用户管理模块，实现了用户注册、登录、管理员登录和密码找回等核心功能。系统采用 Python Flask 框架开发，使用 SQLite 数据库存储用户数据。

## ✨ 功能特性

### F001 - 用户注册
- 用户可通过用户名、密码、手机号/邮箱完成注册
- 支持手机号和邮箱两种联系方式注册
- 实现手机号/邮箱验证码验证
- 密码强度验证（8位以上，包含字母+数字）
- 账号唯一性校验

### F002 - 用户登录
- 已注册用户输入账号密码登录系统
- 搭配数字图形验证码，保障账号安全
- 密码使用 SHA256 加密存储
- 安全机制：连续输错5次密码，锁定账号10分钟防刷

### F003 - 管理员登录
- 管理员使用专属账号密码登录后台
- 登录后可访问管理员专属功能
- 管理员账号仅通过数据库后台添加，不开放页面注册
- 无需图形验证码

### F004 - 密码找回
- 普通用户通过注册时的手机号/邮箱接收验证码
- 验证通过后可重置登录密码
- 仅支持普通用户自主找回
- 管理员密码需后台手动修改

## 🏗️ 项目结构

```
.
├── app/                        # 应用主目录
│   ├── __init__.py            # 应用初始化
│   ├── models.py              # 数据库模型
│   ├── routes/                # 路由目录
│   │   ├── __init__.py
│   │   └── auth.py            # 认证相关路由
│   ├── templates/             # 模板目录
│   │   ├── base.html          # 基础模板
│   │   ├── index.html         # 首页
│   │   ├── register.html      # 注册页
│   │   ├── login.html         # 登录页
│   │   ├── admin_login.html   # 管理员登录页
│   │   ├── forgot_password.html # 忘记密码页
│   │   ├── dashboard.html     # 用户仪表盘
│   │   └── admin_dashboard.html # 管理员仪表盘
│   └── static/                # 静态文件目录
│       ├── css/
│       └── js/
├── config.py                  # 配置文件
├── run.py                     # 应用启动文件
├── requirements.txt           # 依赖列表
├── .coze                      # 项目配置文件
└── README.md                  # 项目文档

```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Flask 3.0.0
- SQLite 3

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行项目

```bash
python run.py
```

项目将运行在 `http://localhost:5000`

### 端口配置

项目默认使用端口 5000，可通过环境变量 `DEPLOY_RUN_PORT` 修改：

```bash
export DEPLOY_RUN_PORT=5000
python run.py
```

## 📊 数据库设计

### 用户表 (users)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键 |
| username | String(80) | 用户名（唯一） |
| password_hash | String(255) | 密码哈希（SHA256） |
| phone | String(20) | 手机号（唯一） |
| email | String(120) | 邮箱（唯一） |
| is_admin | Boolean | 是否为管理员 |
| login_attempts | Integer | 登录失败次数 |
| locked_until | DateTime | 锁定截止时间 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 验证码表 (verification_codes)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键 |
| contact | String(120) | 手机号或邮箱 |
| code | String(10) | 验证码 |
| code_type | String(20) | 验证码类型（register/login/reset_password） |
| created_at | DateTime | 创建时间 |
| expires_at | DateTime | 过期时间 |
| used | Boolean | 是否已使用 |

## 🔐 安全特性

1. **密码加密**：使用 SHA256 算法对密码进行哈希加密存储
2. **登录防刷**：连续5次登录失败后锁定账号10分钟
3. **验证码机制**：
   - 图形验证码：防止自动化攻击
   - 短信/邮箱验证码：验证用户身份
4. **账号唯一性**：用户名、手机号、邮箱均需唯一
5. **密码强度要求**：至少8位，包含字母和数字

## 📝 API 路由

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/register` | GET/POST | 用户注册 |
| `/login` | GET/POST | 用户登录 |
| `/admin/login` | GET/POST | 管理员登录 |
| `/forgot-password` | GET/POST | 密码找回 |
| `/send-verification-code` | POST | 发送验证码 |
| `/dashboard` | GET | 用户中心 |
| `/admin/dashboard` | GET | 管理员中心 |
| `/logout` | GET/POST | 退出登录 |

## 👤 管理员账号创建

管理员账号需要通过数据库直接创建，不提供页面注册入口。可以使用以下 Python 脚本创建：

```python
from app import create_app
from app.models import db, User

app = create_app()
with app.app_context():
    # 检查管理员是否已存在
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # 创建管理员账号
        admin = User(
            username='admin',
            is_admin=True
        )
        admin.set_password('admin123456')  # 修改为您的密码
        db.session.add(admin)
        db.session.commit()
        print("管理员账号创建成功！")
    else:
        print("管理员账号已存在！")
```

## ⚙️ 配置说明

主要配置项位于 `config.py` 文件中：

```python
class Config:
    SECRET_KEY = 'dev-secret-key-change-in-production'  # 会话密钥
    SQLALCHEMY_DATABASE_URI = 'sqlite:///garbage_classification.db'  # 数据库路径
    MAX_LOGIN_ATTEMPTS = 5  # 最大登录失败次数
    LOCKOUT_TIME_MINUTES = 10  # 锁定时间（分钟）
    PASSWORD_MIN_LENGTH = 8  # 密码最小长度
```

生产环境部署时，请务必修改 `SECRET_KEY`。

## 📦 依赖包

```
Flask==3.0.0              # Web 框架
Flask-SQLAlchemy==3.1.1   # ORM 数据库工具
Flask-Login==0.6.3        # 用户会话管理
email-validator==2.1.0    # 邮箱验证
Werkzeug==3.0.1           # 密码加密工具
```

## 🔧 部署说明

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py
```

### 生产环境

建议使用 Gunicorn 或 uWSGI 部署：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用（使用 4 个工作进程）
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 🎨 页面预览

- **首页**：简洁的欢迎页面，提供登录、注册、管理员登录入口
- **注册页**：支持手机号/邮箱验证码注册，实时表单验证
- **登录页**：包含图形验证码，防止恶意登录
- **管理员登录**：专用登录入口，无需图形验证码
- **密码找回**：通过验证码重置密码
- **用户中心**：查看个人信息
- **管理员中心**：查看所有用户信息和管理

## 📌 注意事项

1. **验证码发送**：当前版本验证码仅打印到控制台用于演示，生产环境需要集成真实的短信/邮件服务
2. **密码强度**：密码必须满足8位以上，包含字母和数字
3. **管理员账号**：管理员账号必须通过数据库创建，无法通过页面注册
4. **账号锁定**：连续5次登录失败将锁定账号10分钟
5. **数据库安全**：生产环境建议使用 PostgreSQL 或 MySQL 替代 SQLite

## 🤝 后续功能规划

- [ ] 图片上传与垃圾分类识别
- [ ] 用户识别历史记录
- [ ] 垃圾分类知识库
- [ ] 用户个人信息修改
- [ ] 真实的短信/邮件验证码服务集成
- [ ] 第三方登录（微信、QQ等）
- [ ] 用户权限细分
- [ ] 系统日志记录

## 📄 许可证

MIT License

## 👨‍💻 作者

垃圾图片分类系统开发团队

---

**最后更新时间**：2024年
