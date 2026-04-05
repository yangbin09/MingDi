# Claude Code 插件/技能汇总

本文档整理了 Claude Code 中常用的 9 个插件/技能的功能和用法。

---

## 目录

1. [skill-creator](#1-skill-creator)
2. [claude-md-management](#2-claude-md-management)
3. [code-simplifier](#3-code-simplifier)
4. [feature-dev](#4-feature-dev)
5. [frontend-design](#5-frontend-design)
6. [hookify](#6-hookify)
7. [pr-review-toolkit](#7-pr-review-toolkit)
8. [commit-commands](#8-commit-commands)
9. [ralph-loop](#9-ralph-loop)

---

## 1. skill-creator

### 功能说明
用于创建、初始化和管理自定义技能（skill）的工具。帮助用户快速生成符合 Claude Code 规范的新技能模板，降低技能开发门槛。

### 主要用途
- 快速初始化新技能项目结构
- 生成标准化的 skill 模板代码
- 规范技能配置和元数据

### 使用方式
```
/skill-creator
```
或配合参数创建特定类型的技能：
```
/skill-creator --type custom-skill-name
```

### 适用场景
- 需要扩展 Claude Code 功能时
- 团队需要共享自定义技能时
- 规范化技能开发流程时

---

## 2. claude-md-management

### 功能说明
Markdown 文档管理技能，提供文档整理、归档、搜索和批量处理等功能，方便管理项目中的 Markdown 文件。

### 主要用途
- 批量处理 md 文件
- 生成文档目录索引
- 文档搜索和查找
- 文档归档整理

### 使用方式
```
/claude-md-management
```

### 常用子命令
- `整理` - 自动整理项目中的 Markdown 文件
- `索引` - 生成文档目录索引
- `搜索` - 在文档中搜索关键词

### 适用场景
- 项目文档较多需要整理时
- 需要生成文档目录时
- 批量重命名或移动 md 文件时

---

## 3. code-simplifier

### 功能说明
代码简化和重构工具，分析代码并提供简化建议，能够移除冗余代码、提高可读性、优化代码结构。

### 主要用途
- 分析代码复杂度
- 提供代码简化建议
- 自动重构重复代码
- 优化代码结构

### 使用方式
对整个文件进行简化：
```
/code-simplifier [文件路径]
```

对选中代码进行简化：
```
选中代码后使用 /code-simplifier
```

### 适用场景
- 代码可读性较差需要重构时
- 存在大量重复代码时
- 代码过于复杂需要简化时

---

## 4. feature-dev

### 功能说明
辅助新功能开发的工作流技能，提供从需求分析到实现完成的完整流程支持，帮助开发者规范化开发流程。

### 主要用途
- 功能需求分析和拆解
- 技术方案设计
- 代码实现指导
- 测试用例规划

### 使用方式
```
/feature-dev
```

### 工作流程
1. 需求收集与分析
2. 功能拆解和任务划分
3. 技术方案设计
4. 代码实现
5. 测试验证

### 适用场景
- 开发新功能时需要流程指导
- 需要将复杂需求拆解为具体任务时
- 规范化功能开发流程时

---

## 5. frontend-design

### 功能说明
前端设计辅助工具，支持 UI 组件生成、设计稿转代码、CSS/样式编写等功能，提升前端开发效率。

### 主要用途
- 根据描述生成 UI 组件代码
- 设计稿（图片/Figma）转代码
- CSS/样式代码生成
- 响应式布局实现

### 使用方式
根据需求描述生成前端代码：
```
/frontend-design [需求描述]
```

示例：
```
/frontend-design 创建一个登录表单，包含用户名、密码输入框和登录按钮
```

### 支持的框架
- React
- Vue
- 原生 HTML/CSS/JavaScript

### 适用场景
- 需要快速生成前端组件时
- 设计稿需要转化为代码时
- CSS 样式编写困难时

---

## 6. hookify

### 功能说明
Claude Code Hook 系统管理工具，用于配置和管理各种钩子（hooks），实现特定操作的自动化触发和响应。

### 主要用途
- 创建和配置 hooks
- 管理 hook 触发条件
- 自动化任务触发
- 事件响应处理

### 使用方式
```
/hookify
```

### 常用子命令
- `create` - 创建新的 hook
- `list` - 列出所有 hooks
- `delete` - 删除指定 hook
- `edit` - 编辑 hook 配置

### Hook 类型示例
- `pre-commit` - 提交前触发
- `post-commit` - 提交后触发
- `pre-push` - 推送前触发
- `on-file-change` - 文件变更时触发

### 适用场景
- 需要在特定操作时自动执行任务时
- 配置 CI/CD 自动化流程时
- 强制代码规范检查时

---

## 7. pr-review-toolkit

### 功能说明
Pull Request 审查工具包，辅助代码审查流程，提供 PR 分析、审查意见生成、变更总结等功能。

### 主要用途
- PR 变更分析
- 生成结构化审查意见
- 代码质量评估
- 安全漏洞检测
- 审查意见汇总

### 使用方式
```
/pr-review-toolkit
```

### 常用功能
- `analyze` - 分析 PR 变更
- `comment` - 生成审查评论
- `summary` - 生成审查总结
- `suggest` - 提供改进建议

### 适用场景
- Code Review 流程中
- 团队代码审查时
- 需要快速了解 PR 变更时

---

## 8. commit-commands

### 功能说明
Git 提交命令集合，提供规范化的提交信息生成、提交历史管理等功能，支持 Conventional Commits 规范。

### 主要用途
- 生成规范化的提交信息
- 管理提交历史
- 批量处理提交
- 提交信息验证

### 使用方式
生成提交信息：
```
/commit-commands -m "fix: 修复登录失败问题"
```

其他常用命令：
```
/commit-commands amend    # 修改最后一次提交
/commit-commands log      # 查看提交历史
/commit-commands tag      # 管理标签
```

### 提交类型规范
| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复bug |
| docs | 文档更新 |
| style | 代码格式 |
| refactor | 重构 |
| test | 测试相关 |
| chore | 构建/工具 |

### 适用场景
- 需要规范化 Git 提交信息时
- 团队协作需要统一提交格式时
- 自动化生成 changelog 时

---

## 9. ralph-loop

### 功能说明
循环任务调度工具，支持定期执行检查、轮询任务或定时提醒，类似于 cron 但集成在 Claude Code 中。

### 主要用途
- 定时任务执行
- 定期状态检查
- 循环提醒
- 持续监控

### 使用方式
```
/ralph-loop [间隔] [任务描述]
```

### 常用参数
- 间隔格式：`*/5 * * * *`（每5分钟）
- 也支持自然语言：`every 5 minutes`、`hourly`、`daily`

### 使用示例
每5分钟检查一次部署状态：
```
/ralph-loop */5 * * * * 检查部署状态
```

每小时提醒喝水：
```
/ralph-loop 0 * * * * 提醒喝水
```

### 注意事项
- 任务仅在 Claude Code 会话期间运行
- 长时间运行需要保持会话活跃
- 可使用 `/loop` 命令作为简化版

### 适用场景
- 需要定期检查任务状态时
- 开发过程中定时提醒时
- 持续监控服务健康状态时

---

## 插件对比总结

| 插件名称 | 主要类别 | 核心功能 |
|---------|---------|---------|
| skill-creator | 技能开发 | 创建和管理自定义技能 |
| claude-md-management | 文档管理 | Markdown 文件整理 |
| code-simplifier | 代码优化 | 代码简化和重构 |
| feature-dev | 开发流程 | 功能开发工作流 |
| frontend-design | 前端开发 | UI 组件和样式生成 |
| hookify | 系统集成 | Hook 配置管理 |
| pr-review-toolkit | 代码审查 | PR 审查和分析 |
| commit-commands | Git 操作 | 规范化提交 |
| ralph-loop | 任务调度 | 定时循环任务 |

---

## 快速参考

### 开发流程类
- 新功能开发：`/feature-dev`
- 前端设计：`/frontend-design`
- 代码简化：`/code-simplifier`

### Git 操作类
- 提交代码：`/commit-commands`
- PR 审查：`/pr-review-toolkit`

### 自动化类
- 定时任务：`/ralph-loop`
- Hook 管理：`/hookify`

### 文档类
- 文档管理：`/claude-md-management`

### 扩展类
- 技能创建：`/skill-creator`
