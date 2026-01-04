# AI招聘系统 - 快速开始指南

## 🚀 启动方式

### 方式1: Docker完整部署（推荐）

**开发模式（前端支持热重载）：**
```bash
docker-compose --profile dev up -d
```

**生产模式：**
```bash
docker-compose up -d
```

**完整生产环境（带Nginx反向代理）：**
```bash
docker-compose --profile production up -d
```

**查看日志：**
```bash
docker-compose logs -f
```

**停止服务：**
```bash
docker-compose down
```

### 方式2: 使用启动脚本（混合模式）

**Windows用户:**
```cmd
scripts\dev-start.bat
```

**Linux/Mac用户:**
```bash
chmod +x scripts/dev-start.sh
./scripts/dev-start.sh
```

### 方式3: 手动启动

#### 1. 启动数据库服务
```bash
docker-compose up -d postgres redis
```

#### 2. 启动后端服务
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

## 🌐 访问应用

启动成功后，可以通过以下地址访问：

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:3000 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |
| Nginx（生产） | http://localhost:80 |

## 🔑 默认登录

- 用户名: `admin`
- 密码: `admin123456`

## 🐳 Docker服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| postgres | 5432 | PostgreSQL数据库 |
| redis | 6380 | Redis缓存 |
| backend | 8000 | FastAPI后端服务 |
| frontend-dev | 3000 | 前端开发服务器 |
| frontend | 3000:80 | 前端生产服务器（Nginx） |
| celery_worker | - | 异步任务处理 |
| celery_beat | - | 定时任务调度 |
| nginx | 80 | 反向代理（生产） |

## 📋 功能验证

### 1. 登录系统
1. 打开 http://localhost:3000
2. 使用默认账号登录

### 2. 配置AI模型
1. 进入 "AI模型配置" 页面
2. 点击 "新增模型"
3. 选择模型提供商（如OpenAI）
4. 输入API Key和模型名称
5. 点击 "创建" 后进行连接测试

### 3. 上传简历
1. 进入 "简历管理" -> "上传简历"
2. 选择目标职位
3. 上传PDF或Word格式的简历文件
4. 等待上传完成

### 4. 查看分析结果
1. 在简历列表中找到已上传的简历
2. 点击 "分析" 按钮
3. 等待分析完成
4. 查看详细的分析结果和评分

## 🛠️ 环境要求

- **Docker**: 最新版本（Docker部署）
- **Docker Compose**: v2.0+
- **Node.js**: 18+（手动启动前端）
- **Python**: 3.9+（手动启动后端）

## 📝 注意事项

1. **API Key配置**: 需要配置真实的AI模型API Key才能使用分析功能
2. **RAGFlow集成**: 如需使用RAGFlow功能，需要配置相应的API Key
3. **文件大小限制**: 单个简历文件最大10MB
4. **支持格式**: PDF、DOC、DOCX

## 🆘 常见问题

### Q: Docker构建失败
A: 尝试重新构建镜像
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Q: 前端无法连接后端
A: 检查环境变量配置，确保API地址正确

### Q: 数据库连接失败
A: 确保Docker服务正在运行，PostgreSQL容器已正常启动
```bash
docker-compose ps
docker-compose logs postgres
```

### Q: AI模型测试失败
A: 检查API Key是否正确，网络连接是否正常

## 🔧 开发调试

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend-dev

# 查看Docker容器
docker-compose ps
```

### 重启单个服务
```bash
docker-compose restart backend
docker-compose restart frontend-dev
```

### 进入容器调试
```bash
docker-compose exec backend bash
docker-compose exec frontend-dev sh
```

## 📚 更多文档

- [详细文档](docs/README.md)
- [API文档](http://localhost:8000/docs)
- [项目架构说明](docs/architecture.md)

## 🎯 下一步

1. 配置真实的AI模型API Key
2. 测试简历上传和分析功能
3. 根据需要调整分析评分规则
4. 集成RAGFlow知识库功能
5. 开发招聘网站自动抓取功能

---

✨ **祝您使用愉快！** 如果遇到问题，请查看日志文件或联系技术支持。
