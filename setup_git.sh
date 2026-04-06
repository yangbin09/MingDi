#!/bin/bash
# 鸣镝 - GitHub 仓库初始化脚本

set -e

echo "📦 初始化 Git 仓库..."

# 如果已存在 .git 目录则跳过 init
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git 初始化完成"
else
    echo "ℹ️  Git 仓库已存在，跳过初始化"
fi

# 添加所有文件（排除 .gitignore 中指定的文件）
echo "📝 暂存所有文件..."
git add .

# 执行初始提交
echo "💾 创建初始提交..."
git commit -m "chore: 初始项目结构

- 前后端项目结构
- FastAPI 后端 + Vue 3 前端
- Docker 配置
- E2E 测试框架"

# 创建 GitHub 仓库并推送
echo "🚀 创建 GitHub 仓库并推送..."
gh repo create MingDi --public --source=. --remote=origin --push

echo ""
echo "✅ 完成！仓库地址: https://github.com/$(gh api user --jq .login)/MingDi"
