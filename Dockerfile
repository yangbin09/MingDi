# 鸣镝 - 统一 Docker 镜像
# 包含: 前端 + 后端 + SQLite 数据库

# ========== 阶段1: 构建前端 ==========
FROM node:20-slim AS frontend-builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --only=production=false

COPY frontend/ ./
RUN npm run build

# ========== 阶段2: 后端 + 前端 ==========
FROM python:3.11-slim

WORKDIR /app

# 安装后端依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/
COPY scripts/ ./scripts/

# 复制前端构建产物
COPY --from=frontend-builder /app/dist ./frontend/dist

# 初始化数据库（如果不存在）
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# 启动命令：直接运行，无需额外配置
CMD ["python", "-c", "from backend.models import init_db; init_db(); import uvicorn; uvicorn.run('backend.main:app', host='0.0.0.0', port=8000)"]
