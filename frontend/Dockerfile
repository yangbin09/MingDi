# 前端 Dockerfile - 多阶段构建

# 阶段1: 构建
FROM node:20-slim AS builder

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存
COPY package.json package-lock.json* ./

RUN npm ci --only=production=false

# 复制源代码并构建
COPY . .
RUN npm run build

# 阶段2: 生产镜像
FROM nginx:stable-alpine

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 从构建阶段复制产物
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
