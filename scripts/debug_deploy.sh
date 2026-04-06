#!/bin/bash
# debug_deploy.sh - 容器自愈诊断脚本

set -e

CONTAINER_NAME="mingdi"
IMAGE_NAME="ghcr.io/yangbin09/mingdi:latest"
LOCAL_IMAGE="mingdi:local"

echo "========================================"
echo "  鸣镝容器自愈诊断脚本"
echo "========================================"
echo ""

# 1. 捕获容器日志
echo "[1/4] 捕获容器日志..."
if docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "--- 最近 50 行日志 ---"
    docker logs --tail 50 "$CONTAINER_NAME" 2>&1 || true
    echo ""
    echo "--- 异常栈 (ERROR/FATAL/Traceback) ---"
    docker logs --tail 200 "$CONTAINER_NAME" 2>&1 | grep -E "(ERROR|FATAL|Traceback|Exception|traceback)" || echo "未发现异常关键字"
else
    echo "容器 $CONTAINER_NAME 不存在"
fi
echo ""

# 2. 检查端口监听状态
echo "[2/4] 检查容器内端口监听状态..."
if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "--- 容器进程和端口 ---"
    docker exec "$CONTAINER_NAME" sh -c "cat /proc/net/tcp /proc/net/tcp6 2>/dev/null | head -20" || \
    docker exec "$CONTAINER_NAME" sh -c "netstat -tulpn 2>/dev/null || ss -tulpn 2>/dev/null || echo 'netstat/ss 不可用'" || true
    echo ""
    echo "--- 容器健康状态 ---"
    docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "无健康检查"
else
    echo "容器未运行，跳过端口检查"
fi
echo ""

# 3. 清理并强制重启
echo "[3/4] 强制重启容器..."
# 停止并删除旧容器
if docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "停止旧容器..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# 清理旧镜像卷（如果存在）
echo "清理旧资源..."
docker volume prune -f 2>/dev/null || true

# 尝试拉取最新镜像
echo "拉取最新镜像..."
docker pull "$IMAGE_NAME" 2>/dev/null || echo "拉取失败，使用本地镜像: $LOCAL_IMAGE"
echo ""

# 4. 启动新容器
echo "[4/4] 启动新容器..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8000:8000 \
    -v mingdi-data:/app/data \
    -e PYTHONUNBUFFERED=1 \
    "$IMAGE_NAME" 2>/dev/null || \
    docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8000:8000 \
    -v mingdi-data:/app/data \
    -e PYTHONUNBUFFERED=1 \
    "$LOCAL_IMAGE"

echo ""
echo "========================================"
echo "  容器已重启"
echo "========================================"
echo ""
echo "检查容器状态..."
sleep 3
docker ps --filter "name=$CONTAINER_NAME"

echo ""
echo "测试健康端点..."
for i in 1 2 3; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✓ /health 端点正常"
        break
    else
        echo "× /health 端点失败 (尝试 $i/3)"
        sleep 2
    fi
done

echo ""
echo "测试 API 端点..."
curl -s http://localhost:8000/api/tasks/timeline | head -c 200 || echo "API 请求失败"

echo ""
echo ""
echo "查看完整日志: docker logs $CONTAINER_NAME"
echo "访问应用: http://localhost:8000"
