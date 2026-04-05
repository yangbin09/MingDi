#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Service Layer for PyCron-Master Phase 8
Integrates with Minimax API for AI-powered features
"""
import os
import re
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

# Minimax API Configuration
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_pro"
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_GROUP_ID = os.environ.get("MINIMAX_GROUP_ID", "")

# System prompts for different AI tasks
SYSTEM_PROMPTS = {
    "generate_script": """你是一个专业的Python开发工程师。

要求：
1. 生成完整、可执行的Python代码
2. 代码必须有合理的错误处理
3. 包含必要的import语句
4. 添加清晰的注释说明关键逻辑
5. 考虑安全性和性能
6. 不要使用任何需要额外安装的库（仅使用Python标准库和requests）
7. 代码开头写明功能描述的注释

输出格式：只输出代码，不要有其他解释文字。代码用```python包裹。""",

    "diagnose_error": """你是一个资深的Python调试专家和系统架构师。当任务执行失败时，你会分析错误信息，给出通俗易懂的错误原因和修复建议。

要求：
1. 先用简短的一段话总结错误的核心原因（像经验丰富的运维工程师在解释问题）
2. 给出可能导致这个错误的具体原因（列出2-3个最可能的情况）
3. 针对每个原因，给出具体、可操作的修复建议
4. 如果合适，提供修复后的代码片段（用```python包裹）
5. 语气要专业但易懂，像一个老朋友在帮你debug

输出格式：
```
报告：[大白话描述]

可能原因：
1. [原因1] - [简短说明]
2. [原因2] - [简短说明]

修复建议：
1. [建议]
```""",

    "code_review": """你是一个严格的代码审查专家，专注于Python代码的性能优化和最佳实践。

要求：
1. 检查代码的性能问题（如死循环、内存泄漏、低效算法）
2. 检查代码的安全性（如SQL注入、命令注入风险）
3. 检查代码可读性和维护性
4. 提出具体的优化建议

输出格式：
```
审查报告：
- 性能问题：...
- 安全建议：...
- 优化建议：...
```""",

    "nlp_to_cron": """你是一个Cron表达式专家，擅长将自然语言转换为精确的Cron表达式。

支持的时间描述：
- "每分钟" -> * * * * *
- "每小时" -> 0 * * * *
- "每天凌晨2点" -> 0 2 * * *
- "每周一早上9点" -> 0 9 * * 1
- "每个工作日下午5点半" -> 30 17 * * 1-5

要求：
1. 只输出Cron表达式
2. 如果描述有歧义，输出最常见的理解

输出格式：
```
[cron表达式]
说明：[自然语言解释]
```""",

    "summarize_log": """你是一个专业的运维日志分析师。你会分析海量的程序运行日志，提炼出关键信息和核心结论。

要求：
1. 识别程序的主要功能和输出结果
2. 统计关键指标
3. 发现异常和错误信息
4. 给出简洁的总结

输出格式：
```
日志摘要：
- 执行结果：...
- 关键发现：...
- 建议：...
```""",

    "generate_doc": """你是一个技术文档专家，擅长从代码中提取关键信息并生成简洁的文档描述。

要求：
1. 阅读Python代码，理解其核心功能
2. 生成一段简洁的Markdown格式的功能描述
3. 使用专业但易懂的语言

输出格式：
```
## 功能描述
[描述]

### 输入
[参数说明]

### 输出
[输出说明]
```""",

    "humanize_alert": """你是一个贴心的运维助手，擅长将冷冰冰的系统报错转化成温暖、友好且有用的提示信息。

要求：
1. 将专业错误信息转化成易懂的大白话
2. 带上一点"工程师"的口吻，让信息更易读
3. 提出具体可行的解决建议

输出格式：
```
报告！[大白话描述问题]

可能原因：[简短分析]

建议：[具体可行的操作建议]
```""",
}


class AIService:
    """AI Service for PyCron-Master"""

    def __init__(self):
        self.api_key = MINIMAX_API_KEY
        self.group_id = MINIMAX_GROUP_ID
        self.api_url = MINIMAX_API_URL

    def _call_minimax(self, prompt: str, system_prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Call Minimax API with given prompts"""
        if not self.api_key or not self.group_id:
            logger.warning("Minimax API credentials not configured")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "abab5.5-chat",
            "tokens_to_generate": 1024,
            "temperature": temperature,
            "messages": [
                {"sender_type": "system", "text": system_prompt},
                {"sender_type": "user", "text": prompt}
            ]
        }

        try:
            response = requests.post(
                f"{self.api_url}?GroupId={self.group_id}",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("messages", [{}])[0].get("text", "")
        except requests.exceptions.Timeout:
            logger.error("Minimax API timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Minimax API error: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Minimax API response parsing error: {e}")
            return None

    def _fallback_response(self, task_type: str, input_data: str) -> str:
        """Fallback response when AI is not available"""
        fallbacks = {
            "generate_script": "# AI服务未配置，请配置MINIMAX_API_KEY环境变量",
            "diagnose_error": "# AI诊断服务未配置，请检查错误信息",
            "code_review": "# AI审查服务未配置",
            "nlp_to_cron": "* * * * *",
            "summarize_log": "# AI摘要服务未配置",
            "generate_doc": "# AI文档生成需要配置API Key",
            "humanize_alert": "报告！系统遇到了点麻烦，请检查日志",
        }
        return fallbacks.get(task_type, "未知任务类型")

    # ========== AI Feature Methods ==========

    def generate_script(self, description: str) -> str:
        """Generate Python script from natural language description"""
        prompt = f"用户需求：{description}"
        result = self._call_minimax(prompt, SYSTEM_PROMPTS["generate_script"])
        return result if result else self._fallback_response("generate_script", description)

    def diagnose_error(self, error_traceback: str, script_content: str = "") -> str:
        """Diagnose error and provide fix suggestions"""
        prompt = f"错误信息：\n{error_traceback}\n"
        if script_content:
            prompt += f"相关代码：\n{script_content[:500]}\n"
        prompt += "\n请分析这个错误，给出诊断报告。"
        result = self._call_minimax(prompt, SYSTEM_PROMPTS["diagnose_error"])
        return result if result else self._fallback_response("diagnose_error", error_traceback)

    def code_review(self, code: str) -> str:
        """Review code for performance, security, and best practices"""
        prompt = f"请审查以下Python代码：\n{code}"
        result = self._call_minimax(prompt, SYSTEM_PROMPTS["code_review"])
        return result if result else self._fallback_response("code_review", code)

    def nlp_to_cron(self, natural_language: str) -> str:
        """Convert natural language to Cron expression"""
        prompt = f"请将以下时间描述转换为Cron表达式：{natural_language}"
        result = self._call_minimax(prompt, SYSTEM_PROMPTS["nlp_to_cron"])
        return result if result else self._fallback_response("nlp_to_cron", natural_language)

    def summarize_log(self, log_content: str) -> str:
        """Summarize long log output"""
        truncated = log_content[:8000] if len(log_content) > 8000 else log_content
        prompt = f"请分析以下日志内容并生成摘要：\n{truncated}"
        result = self._call_minimax(prompt, SYSTEM_PROMPTS["summarize_log"])
        return result if result else self._fallback_response("summarize_log", log_content)

    def generate_doc(self, code: str) -> str:
        """Generate documentation from code"""
        prompt = f"请阅读以下Python代码，生成简洁的功能文档：\n{code}"
        result = self._call_minimax(prompt, SYSTEM_PROMPTS["generate_doc"])
        return result if result else self._fallback_response("generate_doc", code)

    def humanize_alert(self, alert_type: str, task_name: str, error_info: str) -> str:
        """Convert technical alert to human-friendly message"""
        prompt = f"告警类型：{alert_type}\n任务名称：{task_name}\n错误信息：{error_info}"
        result = self._call_minimax(prompt, SYSTEM_PROMPTS["humanize_alert"], temperature=0.9)
        return result if result else self._fallback_response("humanize_alert", error_info)


# Singleton instance
ai_service = AIService()


# ========== Utility Functions ==========

def extract_requirements(code: str) -> List[str]:
    """Extract pip requirements from Python code"""
    requirements = set()

    # Common imports to package mapping
    import_map = {
        "requests": "requests",
        "urllib": "urllib3",
        "json": None,
        "os": None,
        "sys": None,
        "datetime": None,
        "time": None,
        "re": None,
        "sqlite3": None,
        "csv": None,
        "xml": None,
        "hashlib": None,
        "logging": None,
        "collections": None,
        "itertools": None,
        "functools": None,
        "subprocess": None,
        "threading": None,
        "asyncio": None,
    }

    import_patterns = [
        r'^import\s+(\w+)',
        r'^from\s+(\w+)\s+import',
    ]

    for line in code.split('\n'):
        line = line.strip()
        for pattern in import_patterns:
            match = re.match(pattern, line)
            if match:
                module = match.group(1)
                if module in import_map and import_map[module]:
                    requirements.add(import_map[module])

    return sorted(list(requirements))


def generate_webhook_token() -> str:
    """Generate a unique webhook token for a task"""
    import secrets
    return secrets.token_urlsafe(32)


def parse_cron_human(cron_expr: str) -> str:
    """Parse cron expression to human-readable text (Chinese)"""
    if not cron_expr:
        return "未设置定时"

    parts = cron_expr.split()
    if len(parts) != 5:
        return cron_expr

    minute, hour, day, month, week = parts

    # Common patterns
    if cron_expr == "* * * * *":
        return "每分钟"
    if cron_expr == "0 * * * *":
        return "每小时整点"
    if cron_expr == "0 0 * * *":
        return "每天凌晨"
    if minute.startswith("*/"):
        return f"每{minute[2:]}分钟"

    # Build description
    desc = []

    if day == "*" and month == "*" and week == "*":
        desc.append(f"每天 {hour}:{minute.zfill(2)}")
    elif week != "*" and day == "*":
        week_days = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        try:
            days = [week_days[int(d)] for d in week.split(',')]
            desc.append(f"每周{','.join(days)} {hour}:{minute.zfill(2)}")
        except:
            desc.append(f"每周{week} {hour}:{minute.zfill(2)}")
    else:
        desc.append(f"在 {cron_expr} 执行")

    return ' '.join(desc) if desc else cron_expr
