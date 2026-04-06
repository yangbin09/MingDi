# Claude Code + Everything Claude Code (ECC) 使用指南

> 本文档整理了 Claude Code CLI 和 Everything Claude Code 插件的完整使用方法。

---

## 一、Claude Code 基础

### 1.1 启动方式

```bash
# 进入项目目录
cd D:\code\claude\code

# 启动交互式会话（主要方式）
claude

# 非交互模式（适合脚本）
claude -p --print "你的问题"

# 继续上次会话
claude -c

# 跳过权限确认启动（不询问，直接执行危险操作）
claude --dangerously-skip-permissions

# 组合使用：跳过确认 + 非交互模式
claude -p --print "你的问题" --dangerously-skip-permissions
```

### 1.2 常用选项

| 选项 | 说明 |
|------|------|
| `-p, --print` | 非交互模式，打印输出后退出 |
| `-c, --continue` | 继续上次会话 |
| `-d, --debug` | 启用调试模式 |
| `--agent <name>` | 指定使用的 Agent |
| `--model <model>` | 指定模型 |
| `--dangerously-skip-permissions` | 跳过权限检查 |

### 1.3 核心命令格式

```
# 直接提问
claude "如何实现 Python 虚拟环境？"

# 执行文件操作
创建 app.py
修改 config.json
删除 temp.txt

# 执行 Terminal 命令
运行 npm install
执行 python main.py

# Git 操作
提交当前更改
创建分支 feature-login
```

---

## 二、Slash Commands（斜杠命令）

> 在交互式会话中输入 `/` 触发命令补全

### 2.1 内置命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/clear` | 清除当前会话 |
| `/resume [id]` | 恢复指定会话 |
| `/fork-session` | 复刻当前会话 |
| `/model <model>` | 切换模型 |
| `/agent <name>` | 切换 Agent |
| `/budget <amount>` | 设置预算上限 |

### 2.2 ECC 插件命令（需安装插件）

#### 规划与执行
```bash
/plan "实现用户登录功能"           # 创建实施计划（需确认后执行）
/tdd "用户认证模块"                 # 测试驱动开发
/e2e "登录流程"                     # 端到端测试
/build-fix                          # 修复构建错误
/feature-dev "新功能"                # 功能开发工作流
```

#### 代码审查
```bash
/code-review                        # 代码质量审查
/security-review                     # 安全审查
/python-reviewer                    # Python 专项审查
/go-reviewer                        # Go 专项审查
/cpp-reviewer                        # C++ 专项审查
```

#### 开发助手
```bash
/agent architect                    # 架构师 Agent
/agent planner                      # 规划师 Agent
/agent tdd-guide                    # TDD 指导
/agent code-reviewer                # 代码审查 Agent
/agent security-reviewer            # 安全审查 Agent
/e2e-runner                         # E2E 测试运行器
```

#### 知识与管理
```bash
/docs-lookup "React hooks"          # 文档查询
/doc-updater                         # 文档更新
/learn                               # 从会话中提取模式
/skill-create                        # 从 Git 历史生成技能
/context-budget                      # 上下文预算管理
```

### 2.3 Multi-Command（多实例命令）

> 需要额外安装 `ccg-workflow` 运行时

```bash
/multi-plan "微服务架构"             # 多实例规划
/multi-execute "部署脚本"            # 多实例执行
/multi-backend                       # 后端多实例开发
/multi-frontend                      # 前端多实例开发
/multi-workflow                      # 自定义多实例工作流
```

安装运行时：
```bash
npx ccg-workflow
```

---

## 三、ECC 规则系统（Rules）

> Rules 是 ECC 插件提供的编码规范，会自动应用到项目中

### 3.1 已安装的 Rules

| 规则集 | 路径 | 说明 |
|--------|------|------|
| common | `~/.claude/rules/common/` | 通用编码规范 |
| python | `~/.claude/rules/python/` | Python 最佳实践 |
| golang | `~/.claude/rules/golang/` | Go 语言规范 |

### 3.2 Rules 包含的内容

**common/**
- `agents.md` - Agent 使用指南
- `code-review.md` - 代码审查规范
- `coding-style.md` - 编码风格
- `development-workflow.md` - 开发流程
- `git-workflow.md` - Git 工作流
- `hooks.md` - 钩子配置
- `patterns.md` - 设计模式
- `performance.md` - 性能优化
- `security.md` - 安全规范
- `testing.md` - 测试规范

**python/**
- `coding-style.md`
- `hooks.md`
- `patterns.md`
- `security.md`
- `testing.md`

**golang/**
- `coding-style.md`
- `hooks.md`
- `patterns.md`
- `security.md`
- `testing.md`

---

## 四、ECC Agents

> Agents 是专业化的子代理，用于委托特定任务

### 4.1 主要 Agents

| Agent | 说明 |
|-------|------|
| `architect` | 系统架构设计 |
| `planner` | 功能规划 |
| `code-reviewer` | 代码审查 |
| `security-reviewer` | 安全审查 |
| `tdd-guide` | TDD 指导 |
| `e2e-runner` | E2E 测试 |
| `refactor-cleaner` | 重构清理 |
| `doc-updater` | 文档更新 |
| `python-reviewer` | Python 审查 |
| `go-reviewer` | Go 审查 |
| `build-error-resolver` | 构建错误修复 |

### 4.2 使用方式

```
# 在交互式会话中
/agent architect

# 或直接描述任务
请使用 architect agent 设计一个微服务架构
```

---

## 五、项目实战命令

### 5.1 PyCron-Master 项目

```bash
# 启动 Claude Code
cd D:\code\claude\code
claude

# 在会话中使用以下命令：

# 1. 规划新功能
/plan "实现任务导出功能"

# 2. 添加单元测试
/tdd "任务调度器测试"

# 3. 代码审查
/code-review

# 4. 修复构建问题
/build-fix

# 5. 使用 Python 专家审查
/agent python-reviewer
```

### 5.2 日常工作流

```
# 早晨：查看项目状态
claude "检查代码质量和待办事项"

# 开发前：规划任务
/plan "本周开发任务"

# 编码中：遇到问题
claude "解释这段代码的含义" [选中代码]

# 完成后：审查代码
/code-review

# 提交前：最终检查
/agent security-reviewer
```

---

## 六、安装与配置

### 6.1 ECC 插件已安装位置

| 组件 | 路径 |
|------|------|
| Marketplace | `~/.claude/plugins/marketplaces/affaan-m-everything-claude-code/` |
| Plugin Cache | `~/.claude/plugins/cache/ecc-ecc/1.10.0/` |
| Rules | `~/.claude/rules/` |
| Commands | `~/.claude/plugins/cache/ecc-ecc/1.10.0/commands/` (79个) |
| Agents | `~/.claude/plugins/cache/ecc-ecc/1.10.0/agents/` (38个) |

### 6.2 配置文件

```bash
# Claude Code 配置
~/.claude/settings.json

# 已安装插件
~/.claude/plugins/installed_plugins.json

# 市场列表
~/.claude/plugins/known_marketplaces.json
```

### 6.3 永久跳过确认配置

如果希望每次启动都跳过权限确认，可以设置环境变量：

```bash
# 在系统环境变量中添加
CLAUDE_CODE_PERMISSION_MODE=acceptEdits

# 或在 ~/.bashrc / ~/.zshrc 中添加（Linux/macOS/MINGW）
echo 'export CLAUDE_CODE_PERMISSION_MODE=acceptEdits' >> ~/.bashrc

# Windows 系统变量
# 添加用户环境变量 CLAUDE_CODE_PERMISSION_MODE = acceptEdits
```

或在 `settings.json` 中配置：

```json
{
  "skipDangerousModePermissionPrompt": true
}
```

**注意**：`--dangerously-skip-permissions` 选项和 `acceptEdits` 模式会绕过所有安全确认，请仅在可信赖的环境中使用。

---

## 七、常见问题

### Q1: 非交互模式下 slash commands 不工作？

**A**：这是预期行为。Slash commands 仅在交互式会话中可用：

```bash
# 错误 - 非交互模式
claude -p --print '/plan "xxx"'

# 正确 - 交互式会话
claude
# 然后输入 /plan "xxx"
```

### Q2: 如何查看所有可用命令？

```bash
claude
# 输入 / 查看命令列表
```

### Q3: 如何验证 ECC 已正确安装？

```bash
claude
# 输入 /plugin list
# 或输入 /plan 测试
```

### Q4: Multi-command 报错了？

**A**：需要安装 `ccg-workflow` 运行时：

```bash
npx ccg-workflow
```

### Q5: 如何跳过每次的权限确认？

**A**：使用 `--dangerously-skip-permissions` 选项，或设置环境变量：

```bash
# 临时方案：命令行选项
claude --dangerously-skip-permissions

# 永久方案：设置环境变量
export CLAUDE_CODE_PERMISSION_MODE=acceptEdits

# 或在 settings.json 中设置
# 添加 "skipDangerousModePermissionPrompt": true
```

### Q6: 权限确认模式有什么区别？

| 模式 | 说明 |
|------|------|
| `auto` | 默认，每次询问 |
| `acceptEdits` | 自动接受编辑操作 |
| `dontAsk` | 不询问，直接执行 |
| `bypassPermissions` | 绕过所有权限检查 |

---

## 八、快速参考卡

```
╔══════════════════════════════════════════════════════════════╗
║                   Claude Code 速查                         ║
╠══════════════════════════════════════════════════════════════╣
║  claude                                   # 交互式会话     ║
║  claude -c                                # 继续会话       ║
║  claude -p --print "..."                  # 非交互模式     ║
║  claude --dangerously-skip-permissions     # 跳过确认       ║
║  /help                                    # 帮助           ║
║  /plan "任务"                             # 规划（ECC）   ║
║  /tdd "模块"                              # TDD（ECC）    ║
║  /code-review                             # 代码审查（ECC）║
║  /agent <name>                            # 调用 Agent    ║
║  /build-fix                               # 修复错误（ECC）║
╚══════════════════════════════════════════════════════════════╝
```

---

## 九、资源链接

- [Claude Code 官方文档](https://docs.claude.com/claude-code/)
- [ECC GitHub 仓库](https://github.com/affaan-m/everything-claude-code)
- [ECC 官方指南](https://ecc.tools)

---

*最后更新：2026-04-06 | 新增跳过确认启动配置*
