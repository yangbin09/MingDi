# PyCron-Master

Python 脚本定时管理工具 - 定时执行、状态监控、日志追踪。

## 功能特性

- 脚本管理：上传、编辑、删除 Python 脚本
- 定时执行：支持 Cron 表达式配置定时任务
- 手动执行：点击按钮立即执行脚本
- 状态监控：实时显示任务状态（闲置、运行中、成功、失败、超时）
- 日志追踪：实时查看脚本输出（stdout/stderr）
- 自愈机制：重启后自动重新加载未完成的定时任务

## 技术栈

- **后端**: Python 3.10+ / FastAPI / APScheduler
- **数据库**: SQLite / SQLAlchemy
- **前端**: Vue 3 / Tailwind CSS / Vite

## 项目结构

```
pycron-master/
├── backend/
│   ├── main.py          # FastAPI 主应用
│   ├── models.py        # SQLAlchemy 数据模型
│   ├── schemas.py       # Pydantic 请求/响应模型
│   ├── scheduler.py     # APScheduler 调度引擎
│   └── requirements.txt # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── App.vue      # 主组件
│   │   └── main.js      # 入口文件
│   ├── package.json
│   └── vite.config.js
├── scripts/             # Python 脚本存放目录
└── pycron.db           # SQLite 数据库
```

## 快速开始

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问

- 前端: http://localhost:5173
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 使用说明

### 创建任务

1. 点击右上角「新建任务」
2. 填写任务名称、脚本路径、Cron 表达式
3. 选择是否启用定时执行

### 脚本路径

脚本路径相对于项目根目录，例如：
- `./scripts/my_script.py`
- `../scripts/my_script.py`

### Cron 表达式

格式：`分 时 日 月 周`

示例：
- `* * * * *` - 每分钟
- `0 * * * *` - 每小时整点
- `0 9 * * 1-5` - 工作日早上9点
- `*/5 * * * *` - 每5分钟

### 查看日志

1. 点击任务的「日志」按钮
2. 可以实时查看脚本输出
3. 支持查看历史执行记录

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /tasks | 获取所有任务 |
| POST | /tasks | 创建任务 |
| GET | /tasks/{id} | 获取任务详情 |
| PUT | /tasks/{id} | 更新任务 |
| DELETE | /tasks/{id} | 删除任务 |
| POST | /tasks/{id}/run | 立即执行任务 |
| GET | /tasks/{id}/logs | 获取任务日志 |
| POST | /scripts/upload | 上传脚本文件 |
