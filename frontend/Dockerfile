# 前端生产环境 Dockerfile
# 多阶段构建: 1. 构建阶段 2. 运行阶段

# ============================================
# 阶段1: 构建阶段
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache python3 make g++

# 复制 package 文件并安装依赖
COPY frontend/package*.json ./
RUN npm ci

# 复制源代码并构建
COPY frontend/ ./

# 设置构建环境变量并构建
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_WS_BASE_URL=ws://localhost:8000

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_WS_BASE_URL=${VITE_WS_BASE_URL}

RUN npm run build

# ============================================
# 阶段2: 运行阶段
# ============================================
FROM nginx:alpine

# 复制自定义 nginx 配置
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/default.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
