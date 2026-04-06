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

# 复制后端代码（直接放在 /app 下，而非 /app/backend）
COPY backend/main.py ./main.py
COPY backend/models.py ./models.py
COPY backend/schemas.py ./schemas.py
COPY backend/scheduler.py ./scheduler.py
COPY backend/ai_service.py ./ai_service.py
COPY backend/db_utils.py ./db_utils.py
COPY backend/docker_runner.py ./docker_runner.py
COPY backend/repositories.py ./repositories.py
COPY backend/constants.py ./constants.py
COPY scripts/ ./scripts/

# 复制前端构建产物
COPY --from=frontend-builder /app/dist ./frontend/dist

# 初始化数据库（如果不存在）
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# 启动命令：在 /app 目录下运行
CMD ["python", "-c", "from models import init_db; init_db(); import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000)"]
