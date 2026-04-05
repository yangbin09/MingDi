# PyCron-Master API 路由文档

> 本文档由代码逆向生成，详细记录了所有 RESTful API 端点。

---

## 一、任务管理 (Tasks)

### 1.1 获取任务列表
```
GET /tasks
```

**响应模型**: `List[TaskResponse]`

**说明**: 获取所有任务列表

---

### 1.2 获取单个任务
```
GET /tasks/{task_id}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | int | 是 | 任务ID |

**响应模型**: `TaskResponse`

**错误**: `404 Not Found` - 任务不存在

---

### 1.3 创建任务
```
POST /tasks
```

**请求体**: `TaskCreate`

**字段说明**:
| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| name | string | 是 | - | 任务名称 |
| script_path | string | 是 | - | 脚本路径 |
| cron_expr | string | 否 | null | Cron表达式 |
| is_active | bool | 否 | true | 是否启用 |
| interpreter_path | string | 否 | null | Python解释器路径 |
| depends_on | int | 否 | null | 依赖任务ID |
| timeout | int | 否 | 300 | 超时时间（秒） |
| webhook_enabled | bool | 否 | false | 是否启用Webhook |
| description | string | 否 | null | 任务描述 |
| use_docker | bool | 否 | false | 是否使用Docker沙箱 |
| docker_image | string | 否 | null | Docker镜像名称 |
| log_retention_count | int | 否 | 100 | 日志保留条数 |

---

### 1.4 更新任务
```
PUT /tasks/{task_id}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | int | 是 | 任务ID |

**请求体**: `TaskUpdate`（所有字段可选）

---

### 1.5 删除任务
```
DELETE /tasks/{task_id}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | int | 是 | 任务ID |

**响应**:
```json
{"message": "Task deleted successfully"}
```

---

### 1.6 立即运行任务
```
POST /tasks/{task_id}/run
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | int | 是 | 任务ID |

**响应**:
```json
{"message": "Task execution started"}
```

**错误**: `400 Bad Request` - 任务正在运行中

---

### 1.7 获取任务时间线
```
GET /tasks/timeline
```

**说明**: 获取最近24小时的任务执行历史，用于时间线可视化

**响应**: 数组，包含任务ID、名称、开始/结束时间、持续时间、退出码、状态

---

### 1.8 获取任务Webhook信息
```
GET /tasks/{task_id}/webhook-info
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | int | 是 | 任务ID |

---

### 1.9 启用Webhook
```
POST /tasks/{task_id}/enable-webhook
```

---

### 1.10 禁用Webhook
```
POST /tasks/{task_id}/disable-webhook
```

---

## 二、日志管理 (Logs)

### 2.1 获取任务日志列表
```
GET /tasks/{task_id}/logs
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | int | 是 | 任务ID |

**响应模型**: `List[LogResponse]`

---

### 2.2 搜索日志（分页）
```
GET /logs/search
```

**Query参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 20 | 每页条数 |
| task_id | int | 否 | - | 按任务ID过滤 |
| exit_code | int | 否 | - | 按退出码过滤（0=成功） |
| keyword | string | 否 | - | 关键词搜索（日志内容） |
| start_date | string | 否 | - | 开始日期（ISO格式） |
| end_date | string | 否 | - | 结束日期（ISO格式） |

**响应格式**:
```json
{
  "total": 92,
  "items": [
    {
      "id": 105,
      "task_id": 5,
      "start_time": "2026-04-06T01:25:00.030882",
      "end_time": "2026-04-06T01:25:05.081059",
      "output": "...",
      "exit_code": 0
    }
  ]
}
```

---

### 2.3 获取单条日志
```
GET /logs/{log_id}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| log_id | int | 是 | 日志ID |

**响应模型**: `LogResponse`

---

### 2.4 删除单条日志
```
DELETE /logs/{log_id}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| log_id | int | 是 | 日志ID |

**响应**:
```json
{"message": "Log deleted successfully", "id": 123}
```

---

### 2.5 批量删除日志
```
DELETE /logs
```

**请求体**: `List[int]` - 日志ID数组

**响应**:
```json
{"message": "Deleted 5 logs", "count": 5}
```

---

### 2.6 日志流式推送（SSE）
```
GET /tasks/{task_id}/logs/stream
```

**说明**: Server-Sent Events 实时推送新日志

---

### 2.7 下载日志文件
```
GET /logs/{log_id}/download
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| log_id | int | 是 | 日志ID |

**响应**: 文本文件下载（Content-Type: text/plain）

---

## 三、脚本管理 (Scripts)

### 3.1 上传脚本文件
```
POST /scripts/upload
```

**请求**: `multipart/form-data`
- `file`: Python文件（.py）

**响应**:
```json
{"filename": "test.py", "path": "/path/to/scripts/test.py"}
```

**限制**: 仅支持 .py 文件

---

### 3.2 上传脚本文本
```
POST /scripts/upload-text
```

**Query参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 文件名（需以.py结尾） |
| content | string | 是 | 脚本内容 |

---

## 四、环境变量 (EnvVars)

### 4.1 获取环境变量列表
```
GET /env-vars
```

**响应模型**: `List[EnvVarResponse]`

---

### 4.2 创建环境变量
```
POST /env-vars
```

**请求体**: `EnvVarCreate`
```json
{
  "key": "MY_VAR",
  "value": "my_value",
  "description": "这是描述",
  "is_secret": false
}
```

**错误**: `400 Bad Request` - 键已存在

---

### 4.3 更新环境变量
```
PUT /env-vars/{env_id}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| env_id | int | 是 | 环境变量ID |

---

### 4.4 删除环境变量
```
DELETE /env-vars/{env_id}
```

---

### 4.5 导出环境变量
```
GET /env-vars/export
```

**说明**: 导出为字典格式，供任务执行时使用

---

## 五、告警配置 (Alerts)

### 5.1 获取告警列表
```
GET /alerts
```

---

### 5.2 创建告警
```
POST /alerts
```

**请求体**: `AlertConfigCreate`
```json
{
  "name": "失败告警",
  "webhook_url": "https://...",
  "events": "failed,timeout",
  "is_active": true,
  "ai_humanize": false
}
```

---

### 5.3 更新告警
```
PUT /alerts/{alert_id}
```

---

### 5.4 删除告警
```
DELETE /alerts/{alert_id}
```

---

## 六、AI 功能 (AI)

### 6.1 生成脚本
```
POST /ai/generate-script
```

**请求体**:
```json
{"description": "自然语言描述"}
```

---

### 6.2 错误诊断
```
POST /ai/diagnose-error
```

**请求体**:
```json
{
  "error_traceback": "错误堆栈",
  "script_content": "相关代码"
}
```

---

### 6.3 代码审查
```
POST /ai/code-review
```

**请求体**:
```json
{"code": "代码内容"}
```

---

### 6.4 自然语言转Cron
```
POST /ai/nlp-to-cron
```

**请求体**:
```json
{"natural_language": "每个工作日下午5点半"}
```

---

### 6.5 日志摘要
```
POST /ai/summarize-log
```

**请求体**:
```json
{"log_content": "日志内容"}
```

---

### 6.6 生成文档
```
POST /ai/generate-doc
```

**请求体**:
```json
{"code": "代码内容"}
```

---

### 6.7 AI告警播报
```
POST /ai/humanize-alert
```

**请求体**:
```json
{
  "alert_type": "failed",
  "task_name": "任务名",
  "error_info": "错误信息"
}
```

---

### 6.8 获取AI能力
```
GET /ai/capabilities
```

---

### 6.9 AI审计日志
```
GET /ai/audit-logs
```

---

### 6.10 AI使用统计
```
GET /ai/usage-stats
```

---

## 七、系统 (System)

### 7.1 获取系统统计
```
GET /system/stats
```

**响应**:
```json
{
  "total_tasks": 5,
  "active_tasks": 3,
  "total_logs": 100,
  "recent_logs": 24,
  "ai_calls_today": 10
}
```

---

### 7.2 获取系统设置
```
GET /system/settings
```

---

### 7.3 更新系统设置
```
PUT /system/settings
```

---

### 7.4 测试AI连接
```
POST /system/settings/test-ai
```

---

## 八、Webhook 触发

### 8.1 Webhook触发任务
```
POST /webhook/{token}
```

**说明**: 通过Webhook Token触发关联任务执行

---

## 九、导入导出

### 9.1 导出配置
```
GET /export
```

**说明**: 导出所有任务、环境变量、告警配置为JSON

---

### 9.2 导入配置
```
POST /import
```

**说明**: 从JSON导入配置

---

## 十、临时执行 (Scratchpad)

### 10.1 执行临时代码
```
POST /scratchpad
```

**请求体**:
```json
{
  "code": "print('Hello')",
  "interpreter_path": null
}
```

**响应**:
```json
{
  "output": "Hello\n",
  "exit_code": 0,
  "execution_time": 0.123
}
```

---

## 十一、节点流编排 (NodeFlows)

### 11.1 获取节点流列表
```
GET /node-flows
```

---

### 11.2 获取单个节点流
```
GET /node-flows/{flow_id}
```

---

### 11.3 创建节点流
```
POST /node-flows
```

---

### 11.4 更新节点流
```
PUT /node-flows/{flow_id}
```

---

### 11.5 删除节点流
```
DELETE /node-flows/{flow_id}
```

---

### 11.6 执行节点流
```
POST /node-flows/{flow_id}/execute
```

---

## 响应格式规范

### 分页响应
```json
{
  "total": 100,
  "items": [...]
}
```

### 成功响应
```json
{"message": "操作成功"}
```

### 错误响应
```json
{"detail": "错误描述"}
```

---

## 认证说明

当前版本未实现认证机制，所有API可直接访问。

**CORS配置**: 仅允许 `http://localhost:5173` 和 `http://127.0.0.1:5173`
