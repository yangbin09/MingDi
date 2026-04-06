#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants and Enumerations for 鸣镝
Centralizes magic strings and configuration values.
"""
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class AlertEvent(str, Enum):
    """Alert event types"""
    FAILED = "failed"
    TIMEOUT = "timeout"
    SUCCESS = "success"
    STARTED = "started"


# Default configuration values
DEFAULT_TASK_TIMEOUT = 300  # seconds
DEFAULT_DOCKER_IMAGE = "python:3.11-slim"
DEFAULT_CPU_PERCENT_INTERVAL = 0.1

# AI Service constants
MAX_LOG_LENGTH_FOR_SUMMARY = 8000
MAX_CODE_LENGTH_FOR_REVIEW = 10000
DEFAULT_AI_TEMPERATURE = 0.7
DEFAULT_AI_TOP_P = 0.9
DEFAULT_AI_MAX_TOKENS = 2048

# Database constants
LOGS_PAGE_SIZE = 100
TIMELINE_HOURS = 24

# Regex patterns (pre-compiled)
IMPORT_PATTERN_STANDARD = r'^import\s+(\w+)'
IMPORT_PATTERN_FROM = r'^from\s+(\w+)\s+import'

# Cron presets for UI
CRON_PRESETS = [
    {"label": "每分钟", "value": "* * * * *"},
    {"label": "每小时", "value": "0 * * * *"},
    {"label": "每天凌晨", "value": "0 2 * * *"},
    {"label": "每周一", "value": "0 9 * * 1"},
]
