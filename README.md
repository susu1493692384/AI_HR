# 🤖 AI招聘系统 (AI HR System)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-19+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

基于 LangChain/LangGraph 的智能简历分析与人才管理系统

[功能特性](#功能特性) • [快速开始](#快速开始) • [技术架构](#技术架构) • [API文档](#api文档) • [常见问题](#常见问题)

</div>

---

## 📖 项目说明

AI招聘系统是一个基于人工智能技术的企业级招聘管理平台，采用领域驱动设计(DDD)架构，整合了 LangChain、LangGraph 和 RAGFlow 等前沿 AI 技术栈。系统通过多智能体协作的方式，对简历进行全方位的智能分析，帮助企业快速筛选和评估候选人。

### 核心亮点

- 🎯 **多智能体协作分析** - 基于 LangGraph 的多智能体系统，从不同维度评估候选人
- 🧠 **智能简历解析** - 支持 PDF、Word、HTML 格式，自动提取关键信息
- 📊 **全方位评分体系** - 技能匹配、经验评估、教育背景、软技能、稳定性等多维度打分
- 🔗 **RAGFlow 知识库集成** - 自动上传简历到云端知识库，支持语义搜索
- ⚙️ **灵活的模型配置** - 支持 OpenAI、Claude、文心一言、通义千问等多种 AI 模型
- 🎨 **现代化 UI** - 基于 React 19 + Tailwind CSS 的响应式界面

---

## ✨ 功能特性

### 1. 简历管理

| 功能 | 说明 |
|------|------|
| 📄 简历上传 | 支持 PDF、DOC、DOCX、HTML 格式，单个文件最大 10MB |
| 🔍 智能解析 | 自动提取候选人姓名、邮箱、电话、位置等关键信息 |
| 📑 简历列表 | 支持搜索、筛选、排序、批量操作 |
| 📥 文件下载 | 一键下载原始简历文件 |
| 🗑️ 文件删除 | 支持单个删除和批量删除 |

### 2. AI 智能分析

| 分析维度 | 说明 |
|----------|------|
| 🔧 技能评估 | 评估候选人技能与岗位要求的匹配度 |
| 💼 经验分析 | 分析工作经历的相关性和深度 |
| 🎓 教育背景 | 评估学历、专业与岗位的匹配度 |
| 🤝 软技能 | 评估沟通能力、团队协作、领导力等 |
| 📈 稳定性评估 | 分析职业发展轨迹和跳槽频率 |
| 🚀 发展潜力 | 预测候选人的成长空间和学习能力 |
| 💪 工作态度 | 评估责任心、主动性等职业素养 |

### 3. AI 模型配置

支持多种主流 AI 模型提供商：

| 提供商 | 模型示例 | 状态 |
|--------|----------|------|
| OpenAI | GPT-4, GPT-3.5 | ✅ 支持 |
| Anthropic | Claude 3.5 Sonnet | ✅ 支持 |
| 百度 | 文心一言 | ✅ 支持 |
| 阿里 | 通义千问 | ✅ 支持 |
| Ollama | 本地开源模型 | ✅ 支持 |

**配置方式**：
1. 选择模型提供商
2. 输入 API Key（或本地服务地址）
3. 指定模型名称
4. 一键测试连接

### 4. 对话管理

- 💬 **智能对话** - 基于 AI 的候选人信息查询
- 📝 **对话历史** - 自动保存对话记录
- 🔄 **上下文关联** - 关联简历进行针对性分析
- 🎯 **模型切换** - 支持不同模型对比效果

### 5. 文件管理

- 📂 **分类管理** - 简历、附件、分析报告分类存储
- 🔎 **快速搜索** - 支持文件名、类型、日期等多维度筛选
- 👁️ **文件预览** - 支持在线预览多种文件格式
- 📊 **存储统计** - 实时显示文件数量和存储空间

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层 (Frontend)                    │
│  React 19 + TypeScript + Tailwind CSS + Zustand            │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 网关层 (Gateway)                   │
│                    FastAPI + CORS Middleware               │
└─────────────────────────────┬───────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
    ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
    │  业务逻辑层    │ │  AI 服务层   │ │  外部集成层  │
    │ (Application) │ │ (AI Services)│ │(Integration) │
    ├───────────────┤ ├──────────────┤ ├──────────────┤
    │• 用户认证     │ │• LLM 服务    │ │• RAGFlow API │
    │• 简历管理     │ │• Agent 协作  │ │• 招聘网站API │
    │• 文件处理     │ │• 向量存储    │ │• 消息通知    │
    │• 对话管理     │ │• Prompt 管理 │ │              │
    └───────┬───────┘ └──────┬───────┘ └──────┬───────┘
            │                │                │
            └────────────────┼────────────────┘
                             ▼
              ┌──────────────────────────────┐
              │      数据持久化层 (Storage)   │
              ├──────────────────────────────┤
              │• PostgreSQL (业务数据)       │
              │• Redis (缓存/会话)           │
              │• 文件系统 (简历存储)         │
              └──────────────────────────────┘
```

### 技术栈

#### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.2+ | UI 框架 |
| TypeScript | 5.9+ | 类型安全 |
| Tailwind CSS | 4.1+ | 样式框架 |
| Zustand | 5.0+ | 状态管理 |
| React Router | 7.11+ | 路由管理 |
| Axios | 1.13+ | HTTP 客户端 |
| Lucide React | 0.562+ | 图标库 |
| Vite | 7.3+ | 构建工具 |

#### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 开发语言 |
| FastAPI | 0.104+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL | 15+ | 关系数据库 |
| Redis | 7+ | 缓存/消息队列 |
| Celery | 5.3+ | 异步任务 |
| LangChain | 0.2+ | AI 框架 |
| LangGraph | 0.2+ | Agent 编排 |

### 项目结构

```
AI_HR/
├── frontend/                    # 前端应用 (React + TypeScript)
│   ├── src/
│   │   ├── components/         # 可复用组件
│   │   │   ├── common/        # 通用组件 (Button, Modal, Table...)
│   │   │   ├── layout/        # 布局组件 (Header, Sidebar...)
│   │   │   ├── llm/           # LLM 相关组件
│   │   │   ├── ResumeCard/    # 简历卡片
│   │   │   ├── ChatInput/     # 对话输入
│   │   │   ├── ResumeAnalysis/# 分析报告组件
│   │   │   └── ...
│   │   ├── pages/             # 页面组件
│   │   │   ├── Home/          # 首页
│   │   │   ├── Login/         # 登录
│   │   │   ├── ResumeLibrary/ # 简历库
│   │   │   ├── AIAnalysis/    # AI 分析
│   │   │   ├── FileManager/   # 文件管理
│   │   │   ├── UserSettings/  # 用户设置
│   │   │   └── TalentInfo/    # 人才详情
│   │   ├── services/          # API 服务
│   │   │   ├── api.ts         # Axios 实例配置
│   │   │   ├── auth.ts        # 认证服务
│   │   │   ├── files.ts       # 文件服务
│   │   │   ├── llm/           # LLM 服务
│   │   │   ├── resume.ts      # 简历服务
│   │   │   └── conversations.ts # 对话服务
│   │   ├── stores/            # Zustand 状态管理
│   │   │   ├── authStore.ts   # 认证状态
│   │   │   └── uiStore.ts     # UI 状态
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── types/             # TypeScript 类型
│   │   ├── constants/         # 常量定义
│   │   ├── utils/             # 工具函数
│   │   └── main.tsx           # 应用入口
│   ├── public/                # 静态资源
│   ├── package.json           # 依赖配置
│   ├── vite.config.ts         # Vite 配置
│   ├── tailwind.config.js     # Tailwind 配置
│   └── tsconfig.json          # TypeScript 配置
│
├── backend/                     # 后端应用 (FastAPI + Python)
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   └── v1/
│   │   │       ├── endpoints/ # API 端点
│   │   │       │   ├── auth.py        # 认证接口
│   │   │       │   ├── resumes.py     # 简历管理
│   │   │       │   ├── llm_config.py  # LLM 配置
│   │   │       │   ├── llm_init.py    # LLM 初始化
│   │   │       │   ├── agent_analysis.py # Agent 分析
│   │   │       │   ├── ragflow.py     # RAGFlow 集成
│   │   │       │   └── stats.py       # 统计接口
│   │   │       └── api.py     # 路由汇总
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── security.py    # 安全认证
│   │   │   ├── dependencies.py # 依赖注入
│   │   │   └── db_init.py     # 数据库初始化
│   │   ├── domain/            # 领域层 (DDD)
│   │   │   └── entities/      # 领域实体
│   │   ├── application/       # 应用层
│   │   │   ├── schemas/       # 数据模式
│   │   │   ├── services/      # 应用服务
│   │   │   ├── use_cases/     # 用例
│   │   │   └── agents/        # AI 智能体
│   │   │       ├── experts/   # 专家智能体
│   │   │       ├── base.py    # 基础 Agent
│   │   │       ├── coordinator.py # 协调器
│   │   │       └── prompts/   # Prompt 模板
│   │   ├── infrastructure/    # 基础设施层
│   │   │   ├── database/      # 数据库
│   │   │   │   ├── models.py  # SQLAlchemy 模型
│   │   │   │   └── database.py # 数据库连接
│   │   │   ├── repositories/  # 数据仓库
│   │   │   └── external_services/ # 外部服务
│   │   └── main.py           # FastAPI 应用入口
│   ├── uploads/               # 文件上传目录
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile            # Docker 镜像
│   └── alembic/              # 数据库迁移
│
├── docker/                     # Docker 配置
│   ├── nginx.conf            # Nginx 配置
│   └── default.conf          # Nginx 站点配置
│
├── docs/                       # 项目文档
│   └── README.md             # 详细文档
│
├── scripts/                    # 启动脚本
│   ├── dev-start.sh          # Linux/Mac 启动
│   ├── dev-stop.sh           # Linux/Mac 停止
│   ├── dev-start.bat         # Windows 启动
│   └── dev-stop.bat          # Windows 停止
│
├── docker-compose.yml         # Docker Compose 配置
├── QUICK_START.md            # 快速开始指南
└── README.md                 # 项目说明 (本文件)
```

---

## 🚀 快速开始

### 环境要求

| 环境 | 版本要求 |
|------|----------|
| Docker | 最新版本 |
| Docker Compose | v2.0+ |
| Node.js | 18+ (本地开发) |
| Python | 3.9+ (本地开发) |
| PostgreSQL | 15+ |
| Redis | 7+ |

### 方式一：Docker 部署 (推荐)

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-hr.git
cd ai-hr
```

#### 2. 启动服务

**开发模式 (支持热重载)**:
```bash
docker-compose --profile dev up -d
```

**生产模式**:
```bash
docker-compose up -d
```

**完整生产环境 (带 Nginx)**:
```bash
docker-compose --profile production up -d
```

#### 3. 查看服务状态

```bash
docker-compose ps
```

#### 4. 查看日志

```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend-dev
```

#### 5. 访问应用

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| Nginx (生产) | http://localhost:80 |

#### 6. 停止服务

```bash
docker-compose down

# 清理数据卷
docker-compose down -v
```

### 方式二：使用启动脚本 (混合模式)

**Windows**:
```cmd
scripts\dev-start.bat
```

**Linux/Mac**:
```bash
chmod +x scripts/dev-start.sh
./scripts/dev-start.sh
```

### 方式三：手动启动 (本地开发)

#### 1. 启动数据库服务

```bash
docker-compose up -d postgres redis
```

#### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 默认登录

- 用户名: `admin`
- 密码: `admin123456`

---

## ⚙️ 环境配置

### 后端环境变量 (.env)

```bash
# === 项目配置 ===
PROJECT_NAME=AI招聘系统
VERSION=1.0.0
DEBUG=True

# === 服务器配置 ===
HOST=0.0.0.0
PORT=8000

# === 安全配置 ===
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 8 days

# === CORS 配置 ===
ALLOWED_HOSTS=["http://localhost:3000","http://127.0.0.1:3000"]

# === 数据库配置 ===
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_hr
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_hr

# === Redis 配置 ===
REDIS_URL=redis://localhost:6380

# === RAGFlow 配置 ===
RAGFLOW_BASE_URL=https://api.ragflow.ai
RAGFLOW_API_KEY=your-ragflow-api-key
RAGFLOW_KNOWLEDGE_BASE_ID=your-knowledge-base-id

# === 文件上传配置 ===
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads
ALLOWED_FILE_TYPES=["application/pdf","application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document","text/html"]

# === Celery 配置 ===
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/0
```

### 前端环境变量 (.env)

```bash
# API 配置
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

---

## 📦 部署指南

### 生产环境部署

#### 1. 使用 Docker Compose

```bash
# 构建镜像
docker-compose build

# 启动生产环境
docker-compose --profile production up -d

# 查看服务状态
docker-compose ps
```

#### 2. 手动部署

**后端部署**:

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置生产环境配置

# 3. 初始化数据库
alembic upgrade head

# 4. 启动服务 (使用 Gunicorn)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**前端部署**:

```bash
# 1. 安装依赖
npm install

# 2. 构建生产版本
npm run build

# 3. 使用 Nginx 托管 dist 目录
# 或部署到 CDN
```

#### 3. Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 监控和日志

**日志位置**:
- 应用日志: `logs/app.log`
- 错误日志: `logs/error.log`
- 访问日志: `logs/access.log`

**监控指标**:
- API 响应时间
- 简历处理成功率
- AI 模型调用成功率
- 系统资源使用情况

---

## 📚 API 文档

### 基本信息

| 项目 | 说明 |
|------|------|
| **Base URL** | `http://localhost:8000` |
| **API 版本** | `v1` |
| **路径前缀** | `/api/v1` |
| **认证方式** | Bearer Token |

### 认证方式

API 使用 Bearer Token 认证：

```http
Authorization: Bearer <your-token>
```

获取 Token 方式：

```http
POST /api/v1/auth/login-json
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123456"
}
```

---

### 1. 认证接口 (`/api/v1/auth/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 | 否 |
| `/api/v1/auth/login` | POST | 用户登录 (OAuth2) | 否 |
| `/api/v1/auth/login-json` | POST | 用户登录 (JSON) | 否 |
| `/api/v1/auth/me` | GET | 获取当前用户信息 | 是 |
| `/api/v1/auth/logout` | POST | 用户登出 | 是 |
| `/api/v1/auth/change-password` | POST | 修改密码 | 是 |

#### 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role": "user"
}
```

#### 用户登录
```http
POST /api/v1/auth/login-json
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123456"
}

// 响应
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 43200
}
```

---

### 2. 简历管理 (`/api/v1/resumes/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/resumes` | GET | 获取简历列表 | 是 |
| `/api/v1/resumes/upload` | POST | 上传简历 | 是 |
| `/api/v1/resumes/{resume_id}` | GET | 获取简历详情 | 是 |
| `/api/v1/resumes/{resume_id}` | DELETE | 删除简历 | 是 |
| `/api/v1/resumes/{resume_id}/download` | GET | 下载简历文件 | 是 |
| `/api/v1/resumes/{resume_id}/parse` | POST | 解析简历 | 是 |
| `/api/v1/resumes/search` | POST | 语义搜索简历 | 是 |

#### 获取简历列表
```http
GET /api/v1/resumes?skip=0&limit=20&keyword=前端&status=completed
Authorization: Bearer <token>

// 查询参数
skip: 跳过数量 (默认 0)
limit: 限制数量 (默认 20)
keyword: 搜索关键词
status: 状态筛选 (uploaded/parsing/completed/failed)

// 响应
{
  "code": 0,
  "data": [
    {
      "id": "uuid",
      "filename": "张三_前端工程师_简历.pdf",
      "file_type": "resume",
      "file_size": 524288,
      "status": "completed",
      "candidate_name": "张三",
      "candidate_email": "zhangsan@example.com",
      "candidate_phone": "13800138000",
      "target_position": "前端工程师",
      "upload_time": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 100
}
```

#### 上传简历
```http
POST /api/v1/resumes/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <文件> (PDF/DOC/DOCX/HTML, 最大 10MB)
file_type: resume/attachment/report (可选, 默认 resume)
```

#### 语义搜索
```http
POST /api/v1/resumes/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "5年前端开发经验，熟悉React",
  "top_k": 10,
  "filters": {
    "target_position": "前端工程师",
    "min_experience": "3年"
  }
}
```

---

### 3. AI 分析 (`/api/v1/agent-analysis/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/agent-analysis/analyze/resume` | POST | 分析简历 | 是 |
| `/api/v1/agent-analysis/analyze/{resume_id}` | GET | 获取分析结果 | 是 |

#### 分析简历
```http
POST /api/v1/agent-analysis/analyze/resume
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_id": "uuid",
  "job_description": "资深前端工程师，要求5年以上经验",
  "position": "前端工程师",
  "dimensions": ["skills", "experience", "education", "soft_skills"]
}

// 响应
{
  "analysis": {
    "overall_score": 85,
    "recommendation": "建议面试",
    "dimensions": {
      "skills": {
        "score": 90,
        "score_reason": "技术栈匹配度高",
        "credible_statements": ["5年React开发经验"],
        "needs_verification": ["精通性能优化"],
        "interview_questions": ["请介绍一个你优化过的性能案例"]
      },
      "experience": { "score": 85, ... },
      "education": { "score": 80, ... },
      "soft_skills": { "score": 82, ... },
      "stability": { "score": 75, ... },
      "development_potential": { "score": 88, ... },
      "work_attitude": { "score": 85, ... }
    },
    "suggestions": ["重点考察React实际项目经验"],
    "overall_assessment": "候选人在技术能力方面表现优秀..."
  }
}
```

---

### 4. LLM 配置 (`/api/v1/llm/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/llm/factories` | GET | 获取支持的 LLM 厂商列表 | 是 |
| `/api/v1/llm/set_api_key` | POST | 设置 API Key (批量配置) | 是 |
| `/api/v1/llm/add_llm` | POST | 添加单个 LLM 配置 | 是 |
| `/api/v1/llm/delete_llm` | POST | 删除模型配置 | 是 |
| `/api/v1/llm/enable_llm` | POST | 启用/禁用模型 | 是 |
| `/api/v1/llm/delete_factory` | POST | 删除整个厂商配置 | 是 |
| `/api/v1/llm/my_llms` | GET | 获取我的模型列表 | 是 |
| `/api/v1/llm/list` | GET | 获取可用模型列表 | 是 |
| `/api/v1/llm/tenant_info` | GET | 获取租户信息 | 是 |
| `/api/v1/llm/set_tenant_info` | POST | 设置租户信息 | 是 |

#### 获取支持的厂商
```http
GET /api/v1/llm/factories
Authorization: Bearer <token>

// 响应
{
  "code": 0,
  "data": [
    {
      "name": "OpenAI",
      "logo": "https://...",
      "tags": ["chat", "embedding"],
      "rank": 100,
      "status": "1",
      "model_types": ["chat", "embedding", "image2text"]
    },
    {
      "name": "ZHIPU-AI",
      "logo": "https://...",
      "tags": ["chat"],
      "rank": 90,
      "status": "1",
      "model_types": ["chat"]
    }
  ]
}
```

#### 设置 API Key
```http
POST /api/v1/llm/set_api_key
Authorization: Bearer <token>
Content-Type: application/json

{
  "llm_factory": "OpenAI",
  "api_key": "sk-...",
  "base_url": "https://api.openai.com/v1",
  "model_type": "chat",
  "llm_name": "gpt-4"
}
```

#### 获取我的模型列表
```http
GET /api/v1/llm/my_llms?include_details=true
Authorization: Bearer <token>

// 响应
{
  "code": 0,
  "data": {
    "OpenAI": {
      "tags": ["chat", "embedding"],
      "llm": [
        {
          "type": "chat",
          "name": "gpt-4",
          "used_token": 15234,
          "status": "1"
        }
      ]
    }
  }
}
```

---

### 5. LLM 初始化 (`/api/v1/llm-init/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/llm-init/init-llm-data` | POST | 初始化 LLM 数据 | 否 |
| `/api/v1/llm-init/reset-and-init` | POST | 重置并重新初始化 | 否 |
| `/api/v1/llm-init/check-init-status` | GET | 检查初始化状态 | 否 |

#### 初始化 LLM 数据
```http
POST /api/v1/llm-init/init-llm-data?tenant_id=default-tenant

// 响应
{
  "code": 0,
  "message": "LLM data initialized successfully",
  "data": {
    "tenant_id": "default-tenant",
    "factories_initialized": 25,
    "models_initialized": "hundreds"
  }
}
```

---

### 6. 对话管理 (`/api/v1/agent-analysis/conversations`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/agent-analysis/conversations` | GET | 获取对话列表 | 是 |
| `/api/v1/agent-analysis/conversations` | POST | 创建对话 | 是 |
| `/api/v1/agent-analysis/conversations/{id}` | GET | 获取对话详情 | 是 |
| `/api/v1/agent-analysis/conversations/{id}` | DELETE | 删除对话 | 是 |
| `/api/v1/agent-analysis/conversations/{id}/messages` | GET | 获取消息历史 | 是 |
| `/api/v1/agent-analysis/conversations/{id}/messages` | POST | 发送消息 (非流式) | 是 |
| `/api/v1/agent-analysis/conversations/{id}/stream` | POST | 发送消息 (流式) | 是 |

#### 创建对话
```http
POST /api/v1/agent-analysis/conversations
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "简历分析对话",
  "resume_id": "uuid"
}

// 响应
{
  "id": "uuid",
  "title": "简历分析对话",
  "resume_id": "uuid",
  "created_at": "2024-01-01T12:00:00Z",
  "status": "active"
}
```

#### 发送消息 (非流式)
```http
POST /api/v1/agent-analysis/conversations/{id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "请分析这个候选人的技能",
  "resume_id": "uuid",
  "use_agent": true
}

// 响应
{
  "message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "AI回复内容...",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 发送消息 (流式 SSE)
```http
POST /api/v1/agent-analysis/conversations/{id}/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "请分析这个候选人的技能",
  "use_agent": true
}

// 响应流 (Server-Sent Events)
data: {"type":"user_message","message":{...}}

data: {"type":"token","token":"AI","accumulated":"AI"}

data: {"type":"token","token":"回复","accumulated":"AI 回复"}

data: {"type":"done","message":{"role":"assistant","content":"..."}}

// 事件类型
user_message: 用户消息已保存
token: AI回复的token
json_data: 隐藏的JSON数据（报告数据）
done: 回复完成
error: 错误信息
```

---

### 7. RAGFlow 集成 (`/api/v1/ragflow/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/ragflow/knowledge-bases` | POST | 创建知识库 | 是 |
| `/api/v1/ragflow/knowledge-bases` | GET | 获取知识库列表 | 是 |
| `/api/v1/ragflow/knowledge-bases/{kb_id}/documents` | POST | 上传文档 | 是 |
| `/api/v1/ragflow/knowledge-bases/{kb_id}/documents/{doc_id}/status` | GET | 获取文档状态 | 是 |
| `/api/v1/ragflow/knowledge-bases/{kb_id}/search` | GET | 搜索知识库 | 是 |
| `/api/v1/ragflow/knowledge-bases/{kb_id}/documents/{doc_id}` | DELETE | 删除文档 | 是 |

#### 创建知识库
```http
POST /api/v1/ragflow/knowledge-bases
Authorization: Bearer <token>
Content-Type: multipart/form-data

name: 人才知识库
description: 存储简历文档
```

#### 搜索知识库
```http
GET /api/v1/ragflow/knowledge-bases/{kb_id}/search?query=前端工程师&top_k=5
Authorization: Bearer <token>

// 响应
{
  "success": true,
  "data": [
    {
      "doc_id": "uuid",
      "filename": "张三_简历.pdf",
      "score": 0.95,
      "chunk": "相关内容片段..."
    }
  ]
}
```

---

### 8. 统计数据 (`/api/v1/stats/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/stats/dashboard` | GET | 获取仪表板统计 | 是 |

#### 仪表板统计
```http
GET /api/v1/stats/dashboard
Authorization: Bearer <token>

// 响应
{
  "code": 0,
  "data": {
    "total_resumes": 150,      // 总简历数
    "talent_pool": 120,         // 已解析完成的简历数
    "pending": 15,              // 待解析的简历数
    "ai_analyzed": 85           // AI分析数
  }
}
```

---

### 9. AI 模型配置 (`/api/v1/ai-models/`)

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/v1/ai-models` | GET | 获取 AI 模型配置列表 | 是 |
| `/api/v1/ai-models` | POST | 创建 AI 模型配置 | 是 |
| `/api/v1/ai-models/{id}` | GET | 获取 AI 模型配置详情 | 是 |
| `/api/v1/ai-models/{id}` | PUT | 更新 AI 模型配置 | 是 |
| `/api/v1/ai-models/{id}` | DELETE | 删除 AI 模型配置 | 是 |
| `/api/v1/ai-models/{id}/test` | POST | 测试 AI 模型连接 | 是 |

---

### 在线文档

启动后端服务后，访问以下地址查看交互式 API 文档：

| 文档类型 | 地址 | 说明 |
|----------|------|------|
| Swagger UI | http://localhost:8000/docs | 交互式 API 文档，可直接测试 |
| ReDoc | http://localhost:8000/redoc | 美观的只读文档 |

---

### 附录：支持的文件格式

| 文件类型 | 支持格式 | MIME 类型 |
|----------|----------|-----------|
| 简历 | PDF, DOC, DOCX, HTML | application/pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, text/html |
| 附件 | PDF, DOC, DOCX, ZIP, JPG, PNG | 同上 + application/zip, image/jpeg, image/png |
| 报告 | PDF, HTML | application/pdf, text/html |

### 附录：简历状态说明

| 状态 | 说明 |
|------|------|
| uploaded | 已上传，待解析 |
| parsing | 正在解析 |
| completed | 解析完成 |
| failed | 解析失败 |

### 附录：支持的 AI 模型厂商

| 厂商 | 模型示例 | 状态 |
|------|----------|------|
| OpenAI | GPT-4, GPT-3.5-turbo | ✅ |
| Anthropic | Claude 3.5 Sonnet | ✅ |
| ZHIPU-AI | GLM-4 | ✅ |
| Baichuan | Baichuan-53B | ✅ |
| Qwen | Qwen-Max | ✅ |
| Ollama | 本地开源模型 | ✅ |
| Xinference | 本地部署模型 | ✅ |

---

## 🔧 开发指南

### 添加新的 AI 模型提供商

1. 在 `backend/app/domain/entities/ai_model.py` 中添加新的提供商：

```python
class AIModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BAIDU = "baidu"
    ALIBABA = "alibaba"
    OLLAMA = "ollama"
    YOUR_PROVIDER = "your_provider"  # 添加新提供商
```

2. 在相应的服务中实现调用逻辑

3. 更新前端模型配置界面

### 自定义分析评分规则

编辑 `backend/app/core/analysis_weights.py`：

```python
ANALYSIS_WEIGHTS = {
    "skills": 0.25,        # 技能匹配权重
    "experience": 0.25,    # 经验评估权重
    "education": 0.15,     # 教育背景权重
    "soft_skills": 0.15,   # 软技能权重
    "stability": 0.10,     # 稳定性权重
    "potential": 0.10,     # 发展潜力权重
}
```

### 运行测试

**后端测试**:
```bash
cd backend
pytest
pytest --cov=app  # 测试覆盖率
```

**前端测试**:
```bash
cd frontend
npm test
npm run test:coverage
```

### 代码规范

**后端**:
```bash
black .        # 代码格式化
isort .        # 导入排序
flake8 .       # 代码检查
```

**前端**:
```bash
npm run lint   # 代码检查
```

---

## ❓ 常见问题

### 1. Docker 构建失败

**问题**: `docker-compose build` 失败

**解决方案**:
```bash
# 清理缓存重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 2. 前端无法连接后端

**问题**: 前端显示网络错误

**解决方案**:
- 检查后端服务是否正常启动: `docker-compose ps`
- 检查环境变量配置: `VITE_API_BASE_URL`
- 查看浏览器控制台和网络请求

### 3. 数据库连接失败

**问题**: 后端日志显示数据库连接错误

**解决方案**:
```bash
# 检查 PostgreSQL 容器状态
docker-compose ps
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 4. AI 模型测试失败

**问题**: 模型测试返回错误

**解决方案**:
- 检查 API Key 是否正确
- 检查网络连接是否正常
- 检查模型名称是否正确
- 查看后端日志获取详细错误信息

### 5. 文件上传失败

**问题**: 上传简历时显示错误

**解决方案**:
- 检查文件大小是否超过 10MB
- 检查文件格式是否支持 (PDF、DOC、DOCX、HTML)
- 检查上传目录权限
- 查看后端日志

### 6. RAGFlow 集成问题

**问题**: RAGFlow 相关功能无法使用

**解决方案**:
- 确认已配置正确的 RAGFlow API Key
- 检查 RAGFLOW_BASE_URL 是否正确
- 查看 RAGFlow 服务状态

### 7. 下载按钮无响应

**问题**: 点击下载按钮没有反应

**解决方案**:
- 确保已重启后端服务 (路由顺序修复)
- 清除浏览器缓存
- 检查浏览器控制台是否有错误
- 确认文件已成功上传

### 8. HTML 文件上传失败

**问题**: 上传 HTML 格式报告失败

**解决方案**:
- 确保后端已更新到最新版本
- 重启后端服务
- 检查文件扩展名是否为 `.html` 或 `.htm`

---

## 🗺️ 路线图

### 已完成 ✅

- [x] 用户认证与权限管理
- [x] 简历上传与解析
- [x] 多 AI 模型配置支持
- [x] 基于多智能体的简历分析
- [x] 文件管理功能
- [x] 对话管理功能
- [x] HTML 报告上传支持

### 计划中 🚧

- [ ] 招聘网站简历自动抓取
- [ ] 简历批量导入
- [ ] 高级搜索和筛选
- [ ] 候选人画像生成
- [ ] 面试安排管理
- [ ] 招聘流程可视化
- [ ] 数据统计和报表
- [ ] 移动端适配

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循现有代码风格
- 添加必要的注释和文档
- 确保测试通过
- 更新相关文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👥 作者

- **您的名字** - *项目维护者* - [your.email@example.com]

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://react.dev/) - 用于构建用户界面的 JavaScript 库
- [LangChain](https://langchain.com/) - AI 应用开发框架
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent 编排框架
- [RAGFlow](https://ragflow.ai/) - 知识库管理平台
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架

---

## 📞 联系方式

- 项目主页: [https://github.com/your-username/ai-hr](https://github.com/your-username/ai-hr)
- 问题反馈: [GitHub Issues](https://github.com/your-username/ai-hr/issues)
- 邮箱: [your.email@example.com](mailto:your.email@example.com)

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️**

Made with ❤️ by AI HR Team

</div>
