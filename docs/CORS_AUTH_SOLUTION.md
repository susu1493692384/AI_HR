# CORS和认证问题解决方案

## 问题描述

在实现真实的用户认证系统时，遇到了以下主要问题：

1. **CORS跨域访问被阻止**
   - 前端（http://localhost:3000）无法访问后端API（http://localhost:8000）
   - 浏览器控制台错误：`Access to XMLHttpRequest at 'http://localhost:8000/api/v1/auth/login-json' from origin 'http://localhost:3000' has been blocked by CORS policy`

2. **登录接口返回500错误**
   - POST请求到 `/api/v1/auth/login-json` 失败
   - 服务器内部错误，无法正常处理登录请求

3. **数据库查询问题**
   - 使用原生SQL查询导致类型不匹配
   - 用户模型实例化错误

## 解决步骤

### 1. 修复CORS配置

#### 问题原因
- CORS中间件未正确配置
- 中间件添加顺序不当
- 未正确处理OPTIONS预检请求

#### 解决方案
在 `backend/app/main.py` 中更新CORS配置：

```python
# 配置CORS - 必须在包含路由之前
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite 默认端口
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
    expose_headers=["*"]  # 暴露所有头部
)
```

关键点：
- CORS中间件必须在路由包含之前添加
- 使用 `allow_methods=["*"]` 而不是列举具体方法
- 使用 `allow_headers=["*"]` 允许所有请求头

### 2. 修复认证系统

#### 问题原因
- `authenticate_user` 函数返回原生SQL查询结果而不是User模型实例
- JWT令牌创建时参数错误
- 使用原生SQL而非ORM查询

#### 解决方案

##### 2.1 更新导入
在 `backend/app/api/v1/endpoints/auth.py` 中添加必要的导入：

```python
from sqlalchemy import select  # 添加ORM查询支持
```

##### 2.2 修复用户认证函数
将原生SQL查询改为ORM查询：

```python
async def authenticate_user(
    username: str,
    password: str,
    db: AsyncSession
) -> User | None:
    """验证用户凭据"""
    # 使用ORM查询而不是原生SQL
    stmt = select(User).where(
        (User.username == username) | (User.email == username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()  # 获取模型实例

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user  # 返回User模型实例
```

##### 2.3 修复JWT令牌创建
修正 `create_access_token` 的调用方式：

```python
# 错误方式
access_token = create_access_token(
    data={"sub": str(user.id), "username": user.username, "role": user.role},
    expires_delta=access_token_expires
)

# 正确方式
access_token = create_access_token(
    subject=str(user.id),  # 只传递用户ID作为subject
    expires_delta=access_token_expires
)
```

### 3. 创建默认管理员账户

#### 实现步骤
1. 创建初始化脚本 `backend/init_admin.py`
2. 使用SHA256进行密码哈希（临时方案）
3. 插入管理员记录到数据库

#### 管理员凭据
- 用户名：`admin`
- 密码：`admin123456`
- 邮箱：`admin@ai-hr.com`
- 角色：`admin`

## 验证步骤

### 1. 启动后端服务
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 创建管理员账户
```bash
python init_admin.py
```

### 3. 测试CORS配置
```bash
curl -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v http://localhost:8000/api/v1/auth/login-json
```

期望看到响应头包含：
- `access-control-allow-origin: http://localhost:3000`
- `access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT`
- `access-control-allow-credentials: true`

### 4. 测试登录
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"username":"admin","password":"admin123456"}' \
  http://localhost:8000/api/v1/auth/login-json
```

期望响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 691200
}
```

## 注意事项

1. **生产环境安全**
   - 当前使用SHA256进行密码哈希，生产环境应使用bcrypt
   - 需要配置更安全的密钥管理
   - 考虑添加JWT黑名单机制

2. **CORS配置**
   - 生产环境应限制具体的允许域名
   - 避免使用通配符 `*`

3. **数据库连接**
   - 确保PostgreSQL服务正在运行
   - 数据库连接字符串配置正确

## 相关文件

- `backend/app/main.py` - CORS配置
- `backend/app/api/v1/endpoints/auth.py` - 认证端点
- `backend/app/core/security.py` - 安全相关功能
- `backend/init_admin.py` - 管理员初始化脚本
- `backend/app/core/dependencies.py` - 依赖注入

## 后续优化建议

1. 实现refresh token机制
2. 添加密码重置功能
3. 实现邮箱验证
4. 添加登录尝试限制
5. 实现角色权限管理