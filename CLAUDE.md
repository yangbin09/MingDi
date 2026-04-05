# PyCron-Master Phase 2 开发规约

## 核心目标
UI重构与核心功能补全，打造极客风格运维面板。

## 任务清单 (Todo List) - 未完成请勿停止
- [x] 1. 引入 Tailwind CSS 组件库并重构整体的 Layout 布局框架（侧边栏+顶部栏）
- [x] 2. 开发 Dashboard 仪表盘页面并对接后端统计接口
- [x] 3. 升级任务列表，加入 Switch 启停开关和 Icon 图标
- [x] 4. 集成代码编辑器 (Monaco Editor) 到新建/编辑任务页面
- [x] 5. 开发 Terminal 风格的日志查看组件
- [x] 6. 联调测试所有新加入的 UI 交互，修复报错

---

# PyCron-Master Phase 8: 全面 AI 赋能 (AIOps) 与大模型深度集成

## Phase 8.5 前端 UI 深度补齐 (已完成)

### 一、AI 交互深度集成
- [x] **1. AI 脚本生成器** - Monaco Editor 上方输入自然语言，点击"AI 生成代码"按钮，自动写入编辑器
- [x] **2. 极简代码审查** - 编辑器工具栏"AI 审查"按钮，弹窗展示代码优化建议
- [x] **3. 日志智能诊断** - 失败日志旁的"诊断"按钮，高亮展示 AI 错误分析

### 二、高级运行环境与触发器 UI
- [x] **4. Docker 沙箱开关** - 编辑器标题栏切换开关，状态保存到数据库
- [x] **5. Webhook URL 展示** - 任务创建/编辑时显示触发 URL，一键复制按钮
- [x] **6. 节点依赖配置** - 前置任务下拉选择，支持 DAG 编排

### 三、系统设置面板扩充
- [x] **7. AI 与告警设置** - 新增"AI 设置"面板，配置 Minimax API Key、Group ID，在线测试连接

---

## Phase 8 核心功能 (已完成)

### 一、AI 辅助开发与排错 (AIGC & Debugging)
- [x] **1. 自然语言生成脚本 (Text-to-Script)**
- [x] **2. 异常智能诊断 (AI Auto-Fix)**
- [x] **3. 代码极简重构 (Code-Simplifier)**

### 二、智能交互与运维 (Smart Operations)
- [x] **4. 自然语言转 Cron (NLP to Cron)**
- [x] **5. 海量日志摘要 (Log Summarization)**
- [x] **6. 自动生成任务文档 (Auto-Doc)**

### 三、现代工作流与事件驱动 (Modern Workflow)
- [x] **7. Webhook 事件驱动触发**
- [x] **8. 节点化低代码编排 (Visual Node Flow)**
- [x] **9. AI 拟人化告警播报**
- [x] **10. 极速沙箱环境 (Docker Runner)**

## AI 配置说明

### 方式一：系统设置页面（推荐）
1. 进入"系统设置" -> "AI 设置" 标签页
2. 填入 Minimax API Key 和 Group ID
3. 点击"测试连接"验证
4. 点击"保存配置"

### 方式二：环境变量
```bash
# 后端环境变量 (.env)
MINIMAX_API_KEY=your_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
```

## 行为准则
1. **自主循环**：每完成清单中的一项，请自动勾选 `[x]` 并直接开始下一项，无需询问。
2. **错误处理**：遇到报错请自行修复，直到测试通过。
3. **完成标准**：直到所有清单项目全部勾选完成，并演示项目可运行后，方可停止。
