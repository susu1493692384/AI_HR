# AI HR System Frontend

基于 React 19 + TypeScript + Vite + Tailwind CSS 的现代化 AI 招聘系统前端应用。

## 技术栈

- **框架**: React 19
- **语言**: TypeScript
- **构建工具**: Vite
- **样式框架**: Tailwind CSS
- **状态管理**: Zustand
- **路由**: React Router v7
- **服务端状态**: React Query (TanStack Query)
- **UI组件**: Headless UI + 自定义组件
- **图标**: Heroicons + Lucide React
- **文件上传**: React Dropzone

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/         # 组件
│   │   ├── common/        # 通用组件
│   │   │   ├── Card/      # 卡片组件
│   │   │   ├── Button/    # 按钮组件
│   │   │   ├── Modal/     # 模态框组件
│   │   │   └── Table/     # 表格组件
│   │   └── layout/        # 布局组件
│   │       ├── Header/    # 顶部导航
│   │       └── Sidebar/   # 侧边栏
│   ├── pages/              # 页面组件
│   │   ├── Home/          # 首页
│   │   ├── Login/         # 登录页
│   │   ├── ResumeLibrary/ # 简历库
│   │   ├── TalentInfo/    # 人才信息
│   │   ├── AIAnalysis/    # AI分析
│   │   └── FileManager/   # 文件管理
│   ├── stores/             # Zustand 状态管理
│   ├── services/           # API 服务
│   ├── types/              # TypeScript 类型
│   ├── utils/              # 工具函数
│   ├── styles/             # 全局样式
│   └── App.tsx             # 主应用组件
```

## 开发指南

### 环境要求

- Node.js 18+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 设计系统

### 色彩方案

- **主色**: #6366F1 (Indigo)
- **辅色**: #8B5CF6 (Violet)
- **强调色**: #EC4899 (Pink)
- **中性色**: Gray-50 到 Gray-900

### 组件库

项目使用自定义组件库，基于 Headless UI 构建。所有组件都支持：

- 可定制主题
- 响应式设计
- 无障碍访问
- TypeScript 类型安全

### 主要功能

1. **用户认证**
   - 登录/登出
   - Token 管理
   - 权限控制

2. **简历管理**
   - 上传简历（支持拖拽）
   - 简历列表
   - 批量操作

3. **AI 分析**
   - 简历智能分析
   - 人才匹配
   - AI 对话助手

4. **人才信息表**
   - 卡片式展示
   - 高级筛选
   - 数据导出

5. **文件管理**
   - 文件浏览器
   - 预览功能
   - 存储统计

## 状态管理

使用 Zustand 进行状态管理：

- `authStore`: 用户认证状态
- `uiStore`: UI 状态（主题、侧边栏等）
- `resumeStore`: 简历数据
- `aiStore`: AI 模型和对话状态

## API 集成

项目使用 React Query 处理 API 请求：

- 自动缓存
- 请求重试
- 并发请求
- 错误处理

## 部署

### 构建优化

生产构建会自动：

- 代码分割
- Tree shaking
- 压缩优化
- 生成 sourcemap

### 环境变量

创建 `.env.production` 文件：

```bash
VITE_API_BASE_URL=https://your-api-server.com
VITE_APP_NAME=AI HR System
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License