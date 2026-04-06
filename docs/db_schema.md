# 鸣镝 数据库架构文档

> 本文档由代码逆向生成，详细记录了所有数据库表的字段信息。

---

## 一、核心业务表

### 1. tasks（任务表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| name | String(255) | 否 | - | 任务名称 |
| script_path | String(512) | 否 | - | 脚本路径 |
| cron_expr | String(100) | 是 | null | Cron 表达式 |
| status | String(50) | 是 | "idle" | 状态：idle/running/success/failed/timeout |
| last_run_time | DateTime | 是 | null | 最后运行时间 |
| is_active | Boolean | 是 | True | 是否启用 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |
| interpreter_path | String(512) | 是 | null | Python 解释器路径 |
| depends_on | Integer | 是 | null | 依赖任务ID |
| timeout | Integer | 是 | 300 | 超时时间（秒） |
| webhook_enabled | Boolean | 是 | False | 是否启用Webhook |
| webhook_token | String(64) | 是 | null | Webhook Token |
| description | Text | 是 | null | AI生成的文档描述 |
| use_docker | Boolean | 是 | False | 是否使用Docker沙箱 |
| docker_image | String(255) | 是 | null | Docker镜像名称 |
| log_retention_count | Integer | 是 | 100 | 日志保留条数（0=不限制） |

**关联关系**: `logs` (一对多，通过 `task_id`)

---

### 2. logs（日志表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| task_id | Integer | 否 | - | 关联任务ID（外键） |
| start_time | DateTime | 否 | - | 开始时间 |
| end_time | DateTime | 是 | null | 结束时间 |
| output | Text | 是 | "" | 脚本输出内容 |
| exit_code | Integer | 是 | null | 退出码 |

**关联关系**: `task` (多对一，通过 `task_id`)

---

### 3. node_flows（节点流表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| name | String(255) | 否 | - | 流程名称 |
| description | Text | 是 | null | 流程描述 |
| nodes | Text | 是 | "[]" | 节点JSON数据 |
| edges | Text | 是 | "[]" | 边JSON数据 |
| is_active | Boolean | 是 | True | 是否启用 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 4. env_vars（环境变量表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| key | String(255) | 否 | - | 变量名（唯一） |
| value | Text | 否 | - | 变量值 |
| description | String(512) | 是 | null | 描述 |
| is_secret | Boolean | 是 | False | 是否隐藏值 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 5. alert_configs（告警配置表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| name | String(255) | 否 | - | 告警名称 |
| webhook_url | String(1024) | 否 | - | Webhook URL |
| events | String(255) | 是 | "failed,timeout" | 触发事件类型 |
| is_active | Boolean | 是 | True | 是否启用 |
| ai_humanize | Boolean | 是 | False | AI人性化告警 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 6. system_settings（系统设置表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| key | String(255) | 否 | - | 配置键（唯一） |
| value | Text | 是 | null | 配置值 |
| description | String(512) | 是 | null | 配置描述 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

## 二、AI Hub 智能中枢表

### 7. ai_providers（AI服务商表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| name | String(100) | 否 | - | 提供商名称 |
| display_name | String(255) | 否 | - | 显示名称 |
| api_base_url | String(512) | 是 | null | API基础URL（支持Ollama自定义） |
| api_key | Text | 是 | null | API密钥 |
| is_enabled | Boolean | 是 | True | 是否启用 |
| is_primary | Boolean | 是 | False | 是否为主服务商 |
| priority | Integer | 是 | 100 | 优先级（越小越高） |
| rate_limit_rpm | Integer | 是 | null | 每分钟请求限制 |
| rate_limit_tpm | Integer | 是 | null | 每分钟Token限制 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 8. ai_models（AI模型表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| provider_id | Integer | 否 | - | 服务商ID（外键） |
| model_id | String(100) | 否 | - | 模型标识符 |
| display_name | String(255) | 否 | - | 显示名称 |
| model_type | String(50) | 否 | - | 模型类型：chat/completion |
| context_window | Integer | 是 | null | 最大Token数 |
| is_enabled | Boolean | 是 | True | 是否启用 |
| cost_per_input_token | Float | 是 | 0 | 输入Token单价（USD） |
| cost_per_output_token | Float | 是 | 0 | 输出Token单价（USD） |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

**关联关系**: `provider` (多对一)

---

### 9. ai_feature_routing（功能路由表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| feature | String(100) | 否 | - | 功能标识（唯一） |
| display_name | String(255) | 否 | - | 显示名称 |
| primary_model_id | Integer | 是 | null | 主模型ID（外键） |
| fallback_model_ids | Text | 是 | "[]" | 备用模型ID列表（JSON） |
| is_enabled | Boolean | 是 | True | 是否启用 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 10. ai_prompt_templates（提示词模板表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| feature | String(100) | 否 | - | 功能标识（唯一） |
| display_name | String(255) | 否 | - | 显示名称 |
| system_prompt | Text | 是 | null | 系统提示词 |
| user_template | Text | 是 | null | 用户消息模板（支持{{variables}}） |
| temperature | Float | 是 | 0.7 | 温度参数 |
| top_p | Float | 是 | 0.9 | Top-P参数 |
| max_tokens | Integer | 是 | 2048 | 最大输出Token |
| context_lines | Integer | 是 | 100 | 错误诊断上下文行数 |
| is_enabled | Boolean | 是 | True | 是否启用 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 11. ai_semantic_cache（语义缓存表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| cache_key | String(64) | 否 | - | 缓存键（索引） |
| feature | String(100) | 否 | - | 功能标识 |
| prompt_hash | String(64) | 否 | - | Prompt哈希值 |
| response | Text | 否 | - | 缓存的响应 |
| model_id | Integer | 是 | null | 模型ID（外键） |
| hit_count | Integer | 是 | 0 | 命中次数 |
| first_hit_at | DateTime | 是 | datetime.now | 首次命中时间 |
| last_hit_at | DateTime | 是 | datetime.now | 最近命中时间 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| expires_at | DateTime | 是 | null | 过期时间 |

---

### 12. ai_rag_context（本地RAG上下文表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| context_type | String(50) | 否 | - | 上下文类型 |
| context_key | String(255) | 否 | - | 上下文键 |
| content | Text | 否 | - | 上下文内容 |
| is_enabled | Boolean | 是 | True | 是否启用 |
| injection_position | String(20) | 是 | "system" | 注入位置 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 13. ai_permissions（AI权限等级表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| permission_level | Integer | 是 | 1 | 权限等级 |
| permission_name | String(100) | 否 | - | 权限名称 |
| description | Text | 是 | null | 权限描述 |
| requires_confirm | Boolean | 是 | True | 是否需要确认 |
| is_enabled | Boolean | 是 | True | 是否启用 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

**权限等级说明**:
- 1 = Dry-run only（仅试运行）
- 2 = Allow script replace（允许脚本替换）
- 3 = Full autonomy（完全自主）

---

### 14. ai_usage_stats（AI使用统计表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| feature | String(100) | 否 | - | 功能标识 |
| model_id | Integer | 是 | null | 模型ID（外键） |
| provider_id | Integer | 是 | null | 服务商ID（外键） |
| input_tokens | Integer | 是 | 0 | 输入Token数 |
| output_tokens | Integer | 是 | 0 | 输出Token数 |
| total_tokens | Integer | 是 | 0 | 总Token数 |
| cost_usd | Float | 是 | 0 | 费用（USD） |
| request_count | Integer | 是 | 0 | 请求次数 |
| cache_hit_count | Integer | 是 | 0 | 缓存命中次数 |
| error_count | Integer | 是 | 0 | 错误次数 |
| date | String(10) | 否 | - | 统计日期（索引） |
| created_at | DateTime | 是 | datetime.now | 创建时间 |
| updated_at | DateTime | 是 | datetime.now | 更新时间 |

---

### 15. ai_audit_logs（AI审计日志表）

| 字段名 | 数据类型 | 可空 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| id | Integer | 否 | 自增 | 主键 |
| feature | String(100) | 否 | - | 功能标识 |
| model_id | Integer | 是 | null | 模型ID（外键） |
| provider_id | Integer | 是 | null | 服务商ID（外键） |
| prompt | Text | 否 | - | 用户Prompt |
| system_prompt | Text | 是 | null | 系统Prompt |
| response | Text | 是 | null | AI响应 |
| error_message | Text | 是 | null | 错误信息 |
| status | String(20) | 否 | - | 状态：success/error/fallback/cached |
| latency_ms | Integer | 是 | null | 延迟（毫秒） |
| input_tokens | Integer | 是 | 0 | 输入Token数 |
| output_tokens | Integer | 是 | 0 | 输出Token数 |
| cost_usd | Float | 是 | 0 | 费用（USD） |
| cache_hit | Boolean | 是 | False | 是否缓存命中 |
| fallback_used | Boolean | 是 | False | 是否使用了备用 |
| created_at | DateTime | 是 | datetime.now | 创建时间 |

---

## 三、表关系图

```
tasks ──────────────┐
   │               │
   │ 1:N           │ 1:1
   ▼               │
logs ◄──────────────┘
   │
   │ N:1
   │
   └──► tasks (via depends_on)

ai_providers ────── 1:N ──────► ai_models
       │                           │
       │ 1:N                       │ 1:N
       ▼                           ▼
ai_feature_routing         ai_usage_stats
                                   │
ai_prompt_templates              │
       │                           │
ai_semantic_cache ◄──────────────┘
       │
       │
ai_rag_context
ai_permissions
ai_audit_logs
```

---

## 四、数据库配置

- **数据库类型**: SQLite
- **数据库文件**: `./pycron.db`
- **连接字符串**: `sqlite:///./pycron.db`
