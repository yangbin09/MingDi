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

## 已完成功能

### 一、AI 辅助开发与排错 (AIGC & Debugging)
- [x] **1. 自然语言生成脚本 (Text-to-Script)** - 在"新建任务"页面集成 Minimax API 接口，用户输入自然语言描述，AI 直接在 Monaco Editor 中生成完整 Python 代码
- [x] **2. 异常智能诊断 (AI Auto-Fix)** - 当任务执行失败时，在日志页面增加"AI 诊断"按钮，点击后自动将 Error Traceback 喂给大模型，返回大白话的错误原因及修复建议
- [x] **3. 代码极简重构 (Code-Simplifier)** - 在代码编辑器上方加入"AI 审查"功能，调用大模型检查代码性能，提出优化建议

### 二、智能交互与运维 (Smart Operations)
- [x] **4. 自然语言转 Cron (NLP to Cron)** - 输入框支持直接输入"每个工作日下午5点半"，后台调用 AI 自动解析并转化为精准的 Cron 表达式
- [x] **5. 海量日志摘要 (Log Summarization)** - 对于输出长达几千行的日志，提供"AI 总结"功能，一键提炼核心运行结果
- [x] **6. 自动生成任务文档 (Auto-Doc)** - 保存脚本时，AI 自动读取 Python 代码逻辑，生成 Markdown 格式的功能描述

### 三、现代工作流与事件驱动 (Modern Workflow)
- [x] **7. Webhook 事件驱动触发** - 为每个任务生成一个专属的 Webhook URL，支持外部系统通过 HTTP POST 直接唤醒运行该脚本
- [x] **8. 节点化低代码编排 (Visual Node Flow)** - 引入可视化连线视图，允许用户将多个 Python 脚本通过拖拽连线编排成 DAG 处理流水线
- [x] **9. AI 拟人化告警播报** - 升级告警模块，通过 AI 将报错信息转化为"系统架构师"口吻，通过钉钉/企业微信机器人推送
- [x] **10. 极速沙箱环境 (Docker Runner)** - 为高敏感任务提供隔离运行选项，自动根据脚本提取 requirements.txt，并通过 Python 的 Docker SDK 在临时容器中执行

## AI 配置说明

要启用 AI 功能，需要配置以下环境变量：

```bash
# 后端环境变量 (.env)
MINIMAX_API_KEY=your_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
```

AI 功能包括：
- 脚本自动生成（Text-to-Script）
- 错误智能诊断（AI Auto-Fix）
- 代码质量审查（Code Review）
- 自然语言转 Cron 表达式
- 日志智能摘要
- 自动文档生成
- AI 拟人化告警播报

## 行为准则
1. **自主循环**：每完成清单中的一项，请自动勾选 `[x]` 并直接开始下一项，无需询问。
2. **错误处理**：遇到报错请自行修复，直到测试通过。
3. **完成标准**：直到所有清单项目全部勾选完成，并演示项目可运行后，方可停止。
