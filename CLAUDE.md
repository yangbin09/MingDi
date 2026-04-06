# 鸣镝 - AI 全栈开发规范

> 本项目是鸣镝，一个极客风格运维面板，支持任务调度、AI 辅助、节点编排等功能。

---

## 一、角色与全局规则

你是一个拥有 10 年经验的资深全栈架构师。在所有对话、代码注释、Commit Message 以及终端输出中，**必须严格使用中文 (Simplified Chinese)**。不要输出任何英文对话！

---

## 二、项目技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 (Composition API, `<script setup>`) | 使用 Vite 构建 |
| UI 组件库 | Element Plus | 必须使用 `element-plus`，禁止使用 `element-ui` |
| CSS 框架 | Tailwind CSS | 仅用于辅助间距和响应式排版 |
| 后端框架 | FastAPI | Python 3, SQLAlchemy, SQLite |
| 任务调度 | APScheduler | Cron 表达式调度 |
| AI 服务 | Minimax API | 支持脚本生成、错误诊断、日志摘要等 |

---

## 三、项目结构

```
pycron-master/
├── backend/
│   ├── main.py          # FastAPI 主应用（含所有路由）
│   ├── models.py        # SQLAlchemy 模型定义
│   ├── schemas.py       # Pydantic Schema 定义
│   ├── scheduler.py     # APScheduler 任务调度器
│   ├── ai_service.py   # AI 服务封装
│   └── db_utils.py     # 数据库工具函数
├── frontend/
│   ├── src/
│   │   ├── views/       # 页面组件（Tasks, Logs, Dashboard, AIAssistant, Settings）
│   │   ├── components/   # 可复用组件（Task/, Dashboard/）
│   │   ├── composables/ # 组合式函数（useTask, useAI, usePolling, useDebounce）
│   │   ├── utils/       # 工具函数（api.js, formatters.js）
│   │   └── App.vue      # 根组件
│   └── package.json
├── docs/                 # AI 知识库文档
│   ├── db_schema.md     # 数据库架构文档
│   └── api_routes.md    # API 路由文档
├── scripts/             # 任务脚本目录
├── CLAUDE.md           # 本规范文件
└── pycron.db          # SQLite 数据库文件
```

---

## 四、前端编码规范

### 4.1 Hook 化规范
业务逻辑必须抽离到 `composables/` 目录，保持 Vue 组件极度轻量：
- `useTask.js` - 任务 CRUD 操作
- `useAI.js` - AI API 调用
- `usePolling.js` - 轮询工具
- `useDebounce.js` / `useThrottle.js` - 防抖节流

### 4.2 样式规范
- 界面必须符合 IDEA Darcula 级别的企业级专业审美
- **禁止使用写死的颜色**，必须使用 CSS 变量
- 主要 CSS 变量：
  - `--bg-primary`, `--bg-secondary`, `--bg-tertiary`
  - `--text-main`, `--text-muted`, `--text-disabled`
  - `--border-subtle`, `--color-primary`, `--color-danger`
  - `--space-xs`, `--space-sm`, `--space-md`, `--space-lg`, `--space-xl`
  - `--radius-sm`, `--radius-md`, `--radius-lg`
  - `--font-family-sans`, `--font-family-mono`

### 4.3 组件约束
- 优先使用 Element Plus 原生组件
- 必须妥善处理交互反馈（加载状态、ElMessage 提示）
- 表格使用 `size="small"` 提高数据密度

---

## 五、后端编码规范

### 5.1 API 设计规范
- 遵循 RESTful 规范
- **分页必须返回格式**：`{"total": int, "items": array}`
- 所有 API 响应必须使用 Pydantic Schema 验证
- 使用 `JSONResponse` 强制返回正确格式

### 5.2 容错与日志
- 遇到数据库或沙箱执行操作时，必须加上 try-except
- 详细记录错误日志到 `logger.error()`

---

## 六、关键约定

### 6.1 日志保留机制
- 任务支持配置 `log_retention_count`（默认100条）
- 任务执行完成后，调度器自动清理超出限制的旧日志
- 设为 0 代表不限制

### 6.2 AI 功能配置
- AI API Key 和 Group ID 通过系统设置页面配置
- 也可通过环境变量 `MINIMAX_API_KEY` 和 `MINIMAX_GROUP_ID` 配置

### 6.3 Webhook 触发
- 任务启用 Webhook 后生成唯一 Token
- 触发 URL：`/webhook/{token}`
- 支持手动触发和外部系统集成

---

## 七、AI 交互指南

### 7.1 编码原则
- **Talk less, code more**：不要解释过度，直接给出最优方案
- **Agentic Loop**：遇到 Bug 时自主完成 [诊断] -> [修改] -> [测试检查] 闭环

### 7.2 文档知识库
遇到复杂业务逻辑时，可参考：
- `docs/db_schema.md` - 数据库表结构
- `docs/api_routes.md` - API 路由详情

---

## 八、其他规范

- Commit Message 必须使用中文描述
- 代码注释必须使用中文
- 变量命名遵循小驼峰（camelCase）
- 常量命名使用全大写下划线（MAX_RETRIES）
