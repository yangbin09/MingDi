#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸣镝 - FastAPI 主应用
重构后：路由层仅处理 HTTP 协议，业务逻辑委托给 Service 层
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import shutil
import time

# 数据库与模型
from models import init_db, get_db, Task, Log, EnvVar, AlertConfig, NodeFlow
from models import AIProvider, AIModel, AIFeatureRouting
from models import AIPromptTemplate, AIRAGContext, AIPermissionLevel
from models import AIAuditLog

# Schema 定义（保持不变）
from schemas import (
    TaskCreate, TaskUpdate, TaskResponse, LogResponse, PaginatedLogResponse,
    EnvVarCreate, EnvVarUpdate, EnvVarResponse,
    AlertConfigCreate, AlertConfigUpdate, AlertConfigResponse,
    SystemStats, ScratchpadRequest, ScratchpadResponse, ExportData,
    AIScriptRequest, AIScriptResponse, AIDiagnoseRequest, AIDiagnoseResponse,
    AICodeReviewRequest, AICodeReviewResponse, AINLPCronRequest, AINLPCronResponse,
    AISummarizeLogRequest, AISummarizeLogResponse, AIGenerateDocRequest, AIGenerateDocResponse,
    AIHumanizeAlertRequest, AIHumanizeAlertResponse,
    WebhookTriggerRequest,
    NodeFlowCreate, NodeFlowUpdate, NodeFlowResponse,
    DockerRunRequest, DockerRunResponse,
    SystemSettingsResponse, SystemSettingsUpdate,
    AIProviderCreate, AIProviderUpdate, AIProviderResponse,
    AIModelCreate, AIModelUpdate, AIModelResponse,
    AIFeatureRoutingCreate, AIFeatureRoutingUpdate, AIFeatureRoutingResponse,
    AIPromptTemplateCreate, AIPromptTemplateUpdate, AIPromptTemplateResponse,
    AIRAGContextCreate, AIRAGContextUpdate, AIRAGContextResponse,
    AIPermissionLevelCreate, AIPermissionLevelUpdate, AIPermissionLevelResponse,
    AIUsageStatsResponse, AIAuditLogResponse
)

# 调度器
from scheduler import execute_task_now, start_scheduler, stop_scheduler

# AI 服务
from ai_service import ai_service, parse_cron_human
from docker_runner import run_in_docker, extract_requirements_from_code, DOCKER_AVAILABLE

# Service 层（依赖注入）
from services import (
    task_service, log_service, env_var_service, alert_service,
    node_flow_service, system_service
)
from repositories import (
    task_repo, alert_repo, env_var_repo,
    ai_provider_repo, ai_model_repo, ai_feature_routing_repo,
    ai_prompt_template_repo, ai_rag_context_repo, ai_permission_level_repo,
    ai_usage_stats_repo, ai_audit_log_repo
)

app = FastAPI(title="鸣镝 API", version="1.0.0")
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
SCRIPTS_DIR = "./scripts"


# ============ 生命周期事件 ============

@app.on_event("startup")
def startup_event() -> None:
    init_db()
    migrate_database()
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event() -> None:
    stop_scheduler()


# ============ 数据库迁移（保持原样，仅清理格式）============

def migrate_database() -> None:
    """Auto-migrate database to add new columns and tables"""
    import sqlite3

    db_path = "./pycron.db"
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]

    cursor.execute("PRAGMA table_info(tasks)")
    tasks_cols = [col[1] for col in cursor.fetchall()]

    new_task_columns = {
        'webhook_enabled': 'ALTER TABLE tasks ADD COLUMN webhook_enabled BOOLEAN DEFAULT 0',
        'webhook_token': 'ALTER TABLE tasks ADD COLUMN webhook_token TEXT',
        'description': 'ALTER TABLE tasks ADD COLUMN description TEXT',
        'use_docker': 'ALTER TABLE tasks ADD COLUMN use_docker BOOLEAN DEFAULT 0',
        'docker_image': 'ALTER TABLE tasks ADD COLUMN docker_image TEXT',
        'log_retention_count': 'ALTER TABLE tasks ADD COLUMN log_retention_count INTEGER DEFAULT 100',
    }

    for col, sql in new_task_columns.items():
        if col not in tasks_cols:
            try:
                cursor.execute(sql)
                print(f"Migrated: Added {col} column to tasks table")
            except Exception as e:
                print(f"Column {col} already exists: {e}")

    cursor.execute("PRAGMA table_info(alert_configs)")
    alert_cols = [col[1] for col in cursor.fetchall()]

    if 'ai_humanize' not in alert_cols:
        try:
            cursor.execute("ALTER TABLE alert_configs ADD COLUMN ai_humanize BOOLEAN DEFAULT 0")
            print("Migrated: Added ai_humanize column to alert_configs")
        except Exception as e:
            print(f"Column ai_humanize already exists: {e}")

    if 'system_settings' not in existing_tables:
        cursor.execute("""
            CREATE TABLE system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Migrated: Created system_settings table")

    if 'node_flows' not in existing_tables:
        cursor.execute("""
            CREATE TABLE node_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                nodes TEXT DEFAULT '[]',
                edges TEXT DEFAULT '[]',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Migrated: Created node_flows table")

    # AI Hub Tables
    if 'ai_providers' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                api_base_url TEXT,
                api_key TEXT,
                is_enabled BOOLEAN DEFAULT 1,
                is_primary BOOLEAN DEFAULT 0,
                priority INTEGER DEFAULT 100,
                rate_limit_rpm INTEGER,
                rate_limit_tpm INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Migrated: Created ai_providers table")

    if 'ai_models' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                model_id TEXT NOT NULL,
                display_name TEXT NOT NULL,
                model_type TEXT NOT NULL,
                context_window INTEGER,
                is_enabled BOOLEAN DEFAULT 1,
                cost_per_input_token REAL DEFAULT 0,
                cost_per_output_token REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (provider_id) REFERENCES ai_providers(id)
            )
        """)
        print("Migrated: Created ai_models table")

    if 'ai_feature_routing' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_feature_routing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                primary_model_id INTEGER,
                fallback_model_ids TEXT DEFAULT '[]',
                is_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (primary_model_id) REFERENCES ai_models(id)
            )
        """)
        print("Migrated: Created ai_feature_routing table")

    if 'ai_prompt_templates' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                system_prompt TEXT,
                user_template TEXT,
                temperature REAL DEFAULT 0.7,
                top_p REAL DEFAULT 0.9,
                max_tokens INTEGER DEFAULT 2048,
                context_lines INTEGER DEFAULT 100,
                is_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Migrated: Created ai_prompt_templates table")

    if 'ai_semantic_cache' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_semantic_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT NOT NULL,
                feature TEXT NOT NULL,
                prompt_hash TEXT NOT NULL,
                response TEXT NOT NULL,
                model_id INTEGER,
                hit_count INTEGER DEFAULT 0,
                first_hit_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_hit_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES ai_models(id)
            )
        """)
        print("Migrated: Created ai_semantic_cache table")

    if 'ai_rag_context' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_rag_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT NOT NULL,
                context_key TEXT NOT NULL,
                content TEXT NOT NULL,
                is_enabled BOOLEAN DEFAULT 1,
                injection_position TEXT DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Migrated: Created ai_rag_context table")

    if 'ai_permissions' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                permission_level INTEGER DEFAULT 1,
                permission_name TEXT NOT NULL,
                description TEXT,
                requires_confirm BOOLEAN DEFAULT 1,
                is_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            """INSERT INTO ai_permissions
            (permission_level, permission_name, description, requires_confirm, is_enabled)
            VALUES (1, 'dry_run', '仅建议 - AI 仅提供建议，不执行任何修改', 0, 1),
            (2, 'script_replace', '允许一键替换脚本 - AI 可以修改并替换脚本内容', 1, 1),
            (3, 'config_modify', '允许修改配置 - AI 可以修改任务配置并自动重试', 1, 1)"""
        )
        print("Migrated: Created ai_permissions table with defaults")

    if 'ai_usage_stats' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT NOT NULL,
                model_id INTEGER,
                provider_id INTEGER,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0,
                request_count INTEGER DEFAULT 0,
                cache_hit_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES ai_models(id),
                FOREIGN KEY (provider_id) REFERENCES ai_providers(id)
            )
        """)
        print("Migrated: Created ai_usage_stats table")

    if 'ai_audit_logs' not in existing_tables:
        cursor.execute("""
            CREATE TABLE ai_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT NOT NULL,
                model_id INTEGER,
                provider_id INTEGER,
                prompt TEXT NOT NULL,
                system_prompt TEXT,
                response TEXT,
                error_message TEXT,
                status TEXT NOT NULL,
                latency_ms INTEGER,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0,
                cache_hit BOOLEAN DEFAULT 0,
                fallback_used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES ai_models(id),
                FOREIGN KEY (provider_id) REFERENCES ai_providers(id)
            )
        """)
        print("Migrated: Created ai_audit_logs table")

    conn.commit()
    conn.close()


# ============ 路由定义（全部使用 Service 层）============

@router.get("/")
def root() -> Dict[str, str]:
    return {"message": "鸣镝 API is running"}


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "mingdi"}


@router.get("/system/stats", response_model=SystemStats)
def get_system_stats() -> SystemStats:
    try:
        import psutil
        import os
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk_path = os.path.splitdrive(os.getcwd())[0] + '\\' if os.name == 'nt' else '/'
        disk = psutil.disk_usage(disk_path)

        return SystemStats(
            cpu_percent=cpu,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            memory_used_gb=round(memory.used / (1024**3), 2),
            memory_total_gb=round(memory.total / (1024**3), 2),
            disk_used_gb=round(disk.used / (1024**3), 2),
            disk_total_gb=round(disk.total / (1024**3), 2)
        )
    except ImportError:
        return SystemStats(
            cpu_percent=0.0, memory_percent=0.0, disk_percent=0.0,
            memory_used_gb=0.0, memory_total_gb=0.0,
            disk_used_gb=0.0, disk_total_gb=0.0
        )


# ============ Task 路由 ============

@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db)) -> List[Task]:
    return task_service.list_tasks(db)


@router.get("/tasks/timeline")
def get_tasks_timeline(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    return log_service.get_timeline(db)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = task_service.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.post("/tasks/{task_id}/run")
def run_task_now(task_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == "running":
        raise HTTPException(status_code=400, detail="Task is already running")
    task_service.run_task_now(db, task_id)
    return {"message": "Task execution started"}


@router.post("/tasks", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)) -> Task:
    return task_service.create_task(db, task_data)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task = task_service.update_task(db, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ============ Webhook 路由 ============

@router.get("/webhook/{token}")
def trigger_webhook(token: str, db: Session = Depends(get_db)) -> JSONResponse:
    task = task_service.find_by_webhook_token(db, token)
    if not task:
        return JSONResponse(status_code=404, content={"success": False, "message": "Invalid webhook token"})
    if not task.webhook_enabled:
        return JSONResponse(status_code=403, content={"success": False, "message": "Webhook trigger is disabled for this task"})
    execute_task_now(task.id)
    return {"success": True, "message": f"Task '{task.name}' execution triggered", "task_id": task.id, "task_status": "running"}


@router.post("/webhook/{token}")
def trigger_webhook_post(token: str, request: WebhookTriggerRequest, db: Session = Depends(get_db)) -> JSONResponse:
    task = task_service.find_by_webhook_token(db, token)
    if not task:
        return JSONResponse(status_code=404, content={"success": False, "message": "Invalid webhook token"})
    if not task.webhook_enabled:
        return JSONResponse(status_code=403, content={"success": False, "message": "Webhook trigger is disabled"})
    if request.payload:
        env_var_service.set_webhook_payload_vars(db, request.payload)
    execute_task_now(task.id)
    return {"success": True, "message": f"Task '{task.name}' triggered with payload", "task_id": task.id}


@router.post("/tasks/{task_id}/enable-webhook")
def enable_webhook(task_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    result = task_service.enable_webhook(db, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.post("/tasks/{task_id}/disable-webhook")
def disable_webhook(task_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = task_service.disable_webhook(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "message": "Webhook disabled"}


@router.get("/tasks/{task_id}/webhook-info")
def get_webhook_info(task_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    info = task_service.get_webhook_info(db, task_id)
    if not info:
        raise HTTPException(status_code=404, detail="Task not found")
    return info


# ============ Script 路由 ============

@router.post("/scripts/upload")
def upload_script(file: UploadFile = File(...)) -> Dict[str, str]:
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are allowed")
    file_path = os.path.join(SCRIPTS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "path": file_path}


@router.post("/scripts/upload-text")
def upload_script_text(filename: str, content: str) -> Dict[str, str]:
    if not filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are allowed")
    file_path = os.path.join(SCRIPTS_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"filename": filename, "path": file_path}


# ============ Log 路由 ============

@router.get("/tasks/{task_id}/logs", response_model=List[LogResponse])
def get_task_logs(task_id: int, db: Session = Depends(get_db)) -> List[Log]:
    logs = log_service.get_task_logs(db, task_id)
    return logs


@router.get("/logs/search", response_model=PaginatedLogResponse)
def search_logs(
    keyword: Optional[str] = None,
    task_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    exit_code: Optional[int] = None,
    exit_code_non_zero: bool = False,
    is_running: bool = False,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
) -> JSONResponse:
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="page and size must be positive integers")
    items, total = log_service.search_logs(
        db, keyword, task_id, start_date, end_date,
        exit_code, exit_code_non_zero, is_running, page, size
    )
    return JSONResponse(content={"total": total, "items": items})


@router.get("/logs/{log_id}", response_model=LogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)) -> Log:
    log = log_service.get_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@router.delete("/logs/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    success = log_service.delete_log(db, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"message": "Log deleted successfully", "id": log_id}


@router.delete("/logs")
def batch_delete_logs(ids: List[int] = Body(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    count = log_service.batch_delete_logs(db, ids)
    return {"message": f"Deleted {count} logs", "count": count}


@router.get("/tasks/{task_id}/logs/stream")
def stream_logs(task_id: int) -> StreamingResponse:
    async def event_generator():
        import asyncio
        import json
        from models import SessionLocal

        last_log_id = 0
        while True:
            db = SessionLocal()
            try:
                new_logs = log_service.get_logs_for_streaming(db, task_id, last_log_id)
                if new_logs:
                    last_log_id = new_logs[0].id
                    for log in reversed(new_logs):
                        data = {
                            "id": log.id,
                            "start_time": log.start_time.isoformat() if log.start_time else None,
                            "end_time": log.end_time.isoformat() if log.end_time else None,
                            "output": log.output,
                            "exit_code": log.exit_code,
                        }
                        yield f"data: {json.dumps(data)}\n\n"
            finally:
                db.close()
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/logs/{log_id}/download")
def download_log(log_id: int, db: Session = Depends(get_db)) -> Response:
    content = log_service.format_log_for_download(db, log_id)
    if not content:
        raise HTTPException(status_code=404, detail="Log not found")
    return Response(content=content.encode(), media_type="text/plain", headers={
        "Content-Disposition": f"attachment; filename=log_{log_id}.log"
    })


# ============ EnvVar 路由 ============

@router.get("/env-vars", response_model=List[EnvVarResponse])
def list_env_vars(db: Session = Depends(get_db)) -> List[EnvVar]:
    return env_var_service.list_env_vars(db)


@router.post("/env-vars", response_model=EnvVarResponse)
def create_env_var(env_data: EnvVarCreate, db: Session = Depends(get_db)) -> EnvVar:
    try:
        return env_var_service.create_env_var(db, env_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/env-vars/{env_id}", response_model=EnvVarResponse)
def update_env_var(env_id: int, env_data: EnvVarUpdate, db: Session = Depends(get_db)) -> EnvVar:
    try:
        env_var = env_var_service.update_env_var(db, env_id, env_data)
        if not env_var:
            raise HTTPException(status_code=404, detail="Environment variable not found")
        return env_var
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/env-vars/{env_id}")
def delete_env_var(env_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = env_var_service.delete_env_var(db, env_id)
    if not success:
        raise HTTPException(status_code=404, detail="Environment variable not found")
    return {"message": "Environment variable deleted successfully"}


@router.get("/env-vars/export")
def export_env_vars(db: Session = Depends(get_db)) -> Dict[str, str]:
    return env_var_service.export_as_dict(db)


# ============ Alert 路由 ============

@router.get("/alerts", response_model=List[AlertConfigResponse])
def list_alerts(db: Session = Depends(get_db)) -> List[AlertConfig]:
    return alert_service.list_alerts(db)


@router.post("/alerts", response_model=AlertConfigResponse)
def create_alert(alert_data: AlertConfigCreate, db: Session = Depends(get_db)) -> AlertConfig:
    return alert_service.create_alert(db, alert_data)


@router.put("/alerts/{alert_id}", response_model=AlertConfigResponse)
def update_alert(alert_id: int, alert_data: AlertConfigUpdate, db: Session = Depends(get_db)) -> AlertConfig:
    alert = alert_service.update_alert(db, alert_id, alert_data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert configuration not found")
    return alert


@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = alert_service.delete_alert(db, alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert configuration not found")
    return {"message": "Alert configuration deleted successfully"}


# ============ Scratchpad 路由 ============

@router.post("/scratchpad", response_model=ScratchpadResponse)
def execute_scratchpad(req: ScratchpadRequest, db: Session = Depends(get_db)) -> ScratchpadResponse:
    import subprocess
    import sys
    import tempfile

    start_time = time.time()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(req.code)
        temp_path = f.name

    try:
        interpreter = req.interpreter_path or sys.executable
        env_dict = env_var_service.export_as_dict(db)
        env_dict['PYTHONUNBUFFERED'] = '1'

        result = subprocess.run(
            [interpreter, temp_path],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, **env_dict}
        )
        output = result.stdout + result.stderr
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        output = "Error: Execution timed out after 60 seconds"
        exit_code = -1
    except Exception as e:
        output = f"Error: {str(e)}"
        exit_code = -1
    finally:
        os.unlink(temp_path)

    execution_time = time.time() - start_time
    return ScratchpadResponse(output=output, exit_code=exit_code, execution_time=round(execution_time, 3))


# ============ Export / Import 路由 ============

@router.get("/export")
def export_config(db: Session = Depends(get_db)) -> ExportData:
    tasks = task_repo.get_all(db)
    env_vars = env_var_repo.get_all(db)
    alerts = alert_repo.get_all(db)
    return ExportData(tasks=tasks, env_vars=env_vars, alert_configs=alerts, version="1.0.0")


@router.post("/import")
def import_config(data: ExportData, db: Session = Depends(get_db)) -> Dict[str, Any]:
    imported_tasks = 0
    imported_envs = 0
    imported_alerts = 0

    for task_data in data.tasks:
        existing = task_repo.get_by_id(db, task_data.id)
        if existing:
            existing.name = task_data.name
            existing.script_path = task_data.script_path
            existing.cron_expr = task_data.cron_expr
            existing.is_active = task_data.is_active
            existing.interpreter_path = task_data.interpreter_path
            existing.depends_on = task_data.depends_on
            existing.timeout = task_data.timeout
        else:
            task = Task(
                id=task_data.id,
                name=task_data.name,
                script_path=task_data.script_path,
                cron_expr=task_data.cron_expr,
                is_active=task_data.is_active,
                interpreter_path=task_data.interpreter_path,
                depends_on=task_data.depends_on,
                timeout=task_data.timeout or 300,
            )
            db.add(task)
            imported_tasks += 1

    for env_data in data.env_vars:
        existing = env_var_repo.get_by_key(db, env_data.key)
        if not existing:
            env_var = EnvVar(
                key=env_data.key,
                value=env_data.value,
                description=env_data.description,
                is_secret=env_data.is_secret,
            )
            db.add(env_var)
            imported_envs += 1

    for alert_data in data.alert_configs:
        existing = alert_repo.get_by_id(db, alert_data.id)
        if not existing:
            alert = AlertConfig(
                name=alert_data.name,
                webhook_url=alert_data.webhook_url,
                events=alert_data.events,
                is_active=alert_data.is_active,
            )
            db.add(alert)
            imported_alerts += 1

    db.commit()
    return {
        "message": "Configuration imported successfully",
        "tasks_imported": imported_tasks,
        "env_vars_imported": imported_envs,
        "alerts_imported": imported_alerts
    }


# ============ System Settings 路由 ============

@router.get("/system/settings", response_model=SystemSettingsResponse)
def get_system_settings(db: Session = Depends(get_db)) -> SystemSettingsResponse:
    settings = system_service.get_system_settings(db)
    return SystemSettingsResponse(**settings)


@router.put("/system/settings", response_model=SystemSettingsResponse)
def update_system_settings(settings: SystemSettingsUpdate, db: Session = Depends(get_db)) -> SystemSettingsResponse:
    settings_dict = system_service.update_system_settings(
        db,
        settings.minimax_api_key,
        settings.minimax_group_id
    )
    if settings.minimax_api_key is not None:
        ai_service.api_key = settings.minimax_api_key
    if settings.minimax_group_id is not None:
        ai_service.group_id = settings.minimax_group_id
    return SystemSettingsResponse(**settings_dict)


@router.post("/system/settings/test-ai")
def test_ai_connection(db: Session = Depends(get_db)) -> Dict[str, Any]:
    api_key = system_service.get_setting(db, "minimax_api_key")
    group_id = system_service.get_setting(db, "minimax_group_id")
    if not api_key or not group_id:
        return {"success": False, "message": "API key or Group ID not configured"}

    original_key = ai_service.api_key
    original_group = ai_service.group_id
    ai_service.api_key = api_key
    ai_service.group_id = group_id

    try:
        result = ai_service.generate_script("print('hello')")
        success = result and "# AI服务未配置" not in result
        return {"success": success, "message": "Connection successful" if success else "Connection failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        ai_service.api_key = original_key
        ai_service.group_id = original_group


# ============ AI Features 路由 ============

@router.post("/ai/generate-script", response_model=AIScriptResponse)
def ai_generate_script(req: AIScriptRequest) -> AIScriptResponse:
    code = ai_service.generate_script(req.description)
    return AIScriptResponse(code=code, used_ai=bool(ai_service.api_key))


@router.post("/ai/diagnose-error", response_model=AIDiagnoseResponse)
def ai_diagnose_error(req: AIDiagnoseRequest) -> AIDiagnoseResponse:
    diagnosis = ai_service.diagnose_error(req.error_traceback, req.script_content)
    return AIDiagnoseResponse(diagnosis=diagnosis, used_ai=bool(ai_service.api_key))


@router.post("/ai/code-review", response_model=AICodeReviewResponse)
def ai_code_review(req: AICodeReviewRequest) -> AICodeReviewResponse:
    review = ai_service.code_review(req.code)
    return AICodeReviewResponse(review=review, used_ai=bool(ai_service.api_key))


@router.post("/ai/nlp-to-cron", response_model=AINLPCronResponse)
def ai_nlp_to_cron(req: AINLPCronRequest) -> AINLPCronResponse:
    result = ai_service.nlp_to_cron(req.natural_language)
    lines = result.strip().split('\n')
    cron_expr = lines[0].strip() if lines else req.natural_language
    description = '\n'.join(lines[1:]) if len(lines) > 1 else parse_cron_human(cron_expr)
    return AINLPCronResponse(cron_expr=cron_expr, description=description, used_ai=bool(ai_service.api_key))


@router.post("/ai/summarize-log", response_model=AISummarizeLogResponse)
def ai_summarize_log(req: AISummarizeLogRequest) -> AISummarizeLogResponse:
    summary = ai_service.summarize_log(req.log_content)
    return AISummarizeLogResponse(summary=summary, used_ai=bool(ai_service.api_key))


@router.post("/ai/generate-doc", response_model=AIGenerateDocResponse)
def ai_generate_doc(req: AIGenerateDocRequest) -> AIGenerateDocResponse:
    doc = ai_service.generate_doc(req.code)
    return AIGenerateDocResponse(doc=doc, used_ai=bool(ai_service.api_key))


@router.post("/ai/humanize-alert", response_model=AIHumanizeAlertResponse)
def ai_humanize_alert(req: AIHumanizeAlertRequest) -> AIHumanizeAlertResponse:
    message = ai_service.humanize_alert(req.alert_type, req.task_name, req.error_info)
    return AIHumanizeAlertResponse(message=message, used_ai=bool(ai_service.api_key))


@router.get("/ai/capabilities")
def ai_capabilities() -> Dict[str, Any]:
    return {
        "ai_enabled": bool(ai_service.api_key and ai_service.group_id),
        "docker_available": DOCKER_AVAILABLE,
        "features": {
            "script_generation": True,
            "error_diagnosis": True,
            "code_review": True,
            "nlp_to_cron": True,
            "log_summarization": True,
            "auto_documentation": True,
            "humanized_alerts": True,
            "docker_sandbox": DOCKER_AVAILABLE
        }
    }


# ============ NodeFlow 路由 ============

@router.get("/node-flows", response_model=List[NodeFlowResponse])
def list_node_flows(db: Session = Depends(get_db)) -> List[NodeFlow]:
    return node_flow_service.list_node_flows(db)


@router.get("/node-flows/{flow_id}", response_model=NodeFlowResponse)
def get_node_flow(flow_id: int, db: Session = Depends(get_db)) -> NodeFlow:
    flow = node_flow_service.get_node_flow(db, flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Node flow not found")
    return flow


@router.post("/node-flows", response_model=NodeFlowResponse)
def create_node_flow(flow_data: NodeFlowCreate, db: Session = Depends(get_db)) -> NodeFlow:
    return node_flow_service.create_node_flow(db, flow_data)


@router.put("/node-flows/{flow_id}", response_model=NodeFlowResponse)
def update_node_flow(flow_id: int, flow_data: NodeFlowUpdate, db: Session = Depends(get_db)) -> NodeFlow:
    flow = node_flow_service.update_node_flow(db, flow_id, flow_data)
    if not flow:
        raise HTTPException(status_code=404, detail="Node flow not found")
    return flow


@router.delete("/node-flows/{flow_id}")
def delete_node_flow(flow_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = node_flow_service.delete_node_flow(db, flow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Node flow not found")
    return {"message": "Node flow deleted successfully"}


@router.post("/node-flows/{flow_id}/execute")
def execute_node_flow(flow_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        return node_flow_service.execute_node_flow(db, flow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ Docker 路由 ============

@router.post("/docker/run", response_model=DockerRunResponse)
def docker_sandbox_run(req: DockerRunRequest, db: Session = Depends(get_db)) -> DockerRunResponse:
    if not DOCKER_AVAILABLE:
        return DockerRunResponse(
            success=False, output="", exit_code=-1, execution_time=0,
            error="Docker is not available on this system"
        )

    env_dict = env_var_service.export_as_dict(db)
    env_dict['PYTHONUNBUFFERED'] = '1'

    success, output, exit_code, exec_time = run_in_docker(
        code=req.code,
        requirements=req.requirements,
        docker_image=req.docker_image,
        timeout=req.timeout,
        environment=env_dict
    )

    return DockerRunResponse(
        success=success, output=output, exit_code=exit_code,
        execution_time=exec_time, error=None if success else output
    )


@router.post("/docker/extract-requirements")
def docker_extract_requirements(code: str = Body(..., media_type="text/plain")) -> Dict[str, Any]:
    requirements = extract_requirements_from_code(code)
    return {"requirements": requirements}


# ============ AI Hub 路由 ============

@router.get("/ai/providers", response_model=List[AIProviderResponse])
def list_ai_providers(db: Session = Depends(get_db)) -> List[AIProvider]:
    return ai_provider_repo.get_ordered(db)


@router.post("/ai/providers", response_model=AIProviderResponse)
def create_ai_provider(provider_data: AIProviderCreate, db: Session = Depends(get_db)) -> AIProvider:
    provider = AIProvider(
        name=provider_data.name,
        display_name=provider_data.display_name,
        api_base_url=provider_data.api_base_url,
        api_key=provider_data.api_key,
        is_enabled=provider_data.is_enabled,
        is_primary=provider_data.is_primary,
        priority=provider_data.priority,
        rate_limit_rpm=provider_data.rate_limit_rpm,
        rate_limit_tpm=provider_data.rate_limit_tpm,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.put("/ai/providers/{provider_id}", response_model=AIProviderResponse)
def update_ai_provider(provider_id: int, provider_data: AIProviderUpdate, db: Session = Depends(get_db)) -> AIProvider:
    provider = ai_provider_repo.get_by_id(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="AI Provider not found")
    for field, value in provider_data.model_dump(exclude_unset=True).items():
        setattr(provider, field, value)
    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/ai/providers/{provider_id}")
def delete_ai_provider(provider_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = ai_provider_repo.delete(db, provider_id)
    if not success:
        raise HTTPException(status_code=404, detail="AI Provider not found")
    return {"message": "AI Provider deleted successfully"}


@router.get("/ai/models", response_model=List[AIModelResponse])
def list_ai_models(db: Session = Depends(get_db)) -> List[AIModel]:
    return ai_model_repo.get_all(db)


@router.post("/ai/models", response_model=AIModelResponse)
def create_ai_model(model_data: AIModelCreate, db: Session = Depends(get_db)) -> AIModel:
    model = AIModel(
        provider_id=model_data.provider_id,
        model_id=model_data.model_id,
        display_name=model_data.display_name,
        model_type=model_data.model_type,
        context_window=model_data.context_window,
        is_enabled=model_data.is_enabled,
        cost_per_input_token=model_data.cost_per_input_token,
        cost_per_output_token=model_data.cost_per_output_token,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.put("/ai/models/{model_id}", response_model=AIModelResponse)
def update_ai_model(model_id: int, model_data: AIModelUpdate, db: Session = Depends(get_db)) -> AIModel:
    model = ai_model_repo.get_by_id(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found")
    for field, value in model_data.model_dump(exclude_unset=True).items():
        setattr(model, field, value)
    db.commit()
    db.refresh(model)
    return model


@router.delete("/ai/models/{model_id}")
def delete_ai_model(model_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = ai_model_repo.delete(db, model_id)
    if not success:
        raise HTTPException(status_code=404, detail="AI Model not found")
    return {"message": "AI Model deleted successfully"}


@router.get("/ai/feature-routing", response_model=List[AIFeatureRoutingResponse])
def list_feature_routing(db: Session = Depends(get_db)) -> List[AIFeatureRouting]:
    return ai_feature_routing_repo.get_all(db)


@router.post("/ai/feature-routing", response_model=AIFeatureRoutingResponse)
def create_feature_routing(routing_data: AIFeatureRoutingCreate, db: Session = Depends(get_db)) -> AIFeatureRouting:
    routing = AIFeatureRouting(
        feature=routing_data.feature,
        display_name=routing_data.display_name,
        primary_model_id=routing_data.primary_model_id,
        fallback_model_ids=routing_data.fallback_model_ids,
        is_enabled=routing_data.is_enabled,
    )
    db.add(routing)
    db.commit()
    db.refresh(routing)
    return routing


@router.put("/ai/feature-routing/{routing_id}", response_model=AIFeatureRoutingResponse)
def update_feature_routing(routing_id: int, routing_data: AIFeatureRoutingUpdate, db: Session = Depends(get_db)) -> AIFeatureRouting:
    routing = ai_feature_routing_repo.get_by_id(db, routing_id)
    if not routing:
        raise HTTPException(status_code=404, detail="Feature routing not found")
    for field, value in routing_data.model_dump(exclude_unset=True).items():
        setattr(routing, field, value)
    db.commit()
    db.refresh(routing)
    return routing


@router.delete("/ai/feature-routing/{routing_id}")
def delete_feature_routing(routing_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = ai_feature_routing_repo.delete(db, routing_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feature routing not found")
    return {"message": "Feature routing deleted successfully"}


@router.get("/ai/prompt-templates", response_model=List[AIPromptTemplateResponse])
def list_prompt_templates(db: Session = Depends(get_db)) -> List[AIPromptTemplate]:
    return ai_prompt_template_repo.get_all(db)


@router.post("/ai/prompt-templates", response_model=AIPromptTemplateResponse)
def create_prompt_template(template_data: AIPromptTemplateCreate, db: Session = Depends(get_db)) -> AIPromptTemplate:
    template = AIPromptTemplate(
        feature=template_data.feature,
        display_name=template_data.display_name,
        system_prompt=template_data.system_prompt,
        user_template=template_data.user_template,
        temperature=template_data.temperature,
        top_p=template_data.top_p,
        max_tokens=template_data.max_tokens,
        context_lines=template_data.context_lines,
        is_enabled=template_data.is_enabled,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/ai/prompt-templates/{template_id}", response_model=AIPromptTemplateResponse)
def update_prompt_template(template_id: int, template_data: AIPromptTemplateUpdate, db: Session = Depends(get_db)) -> AIPromptTemplate:
    template = ai_prompt_template_repo.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    for field, value in template_data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/ai/prompt-templates/{template_id}")
def delete_prompt_template(template_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = ai_prompt_template_repo.delete(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return {"message": "Prompt template deleted successfully"}


@router.get("/ai/rag-context", response_model=List[AIRAGContextResponse])
def list_rag_contexts(db: Session = Depends(get_db)) -> List[AIRAGContext]:
    return ai_rag_context_repo.get_all(db)


@router.post("/ai/rag-context", response_model=AIRAGContextResponse)
def create_rag_context(rag_data: AIRAGContextCreate, db: Session = Depends(get_db)) -> AIRAGContext:
    rag = AIRAGContext(
        context_type=rag_data.context_type,
        context_key=rag_data.context_key,
        content=rag_data.content,
        is_enabled=rag_data.is_enabled,
        injection_position=rag_data.injection_position,
    )
    db.add(rag)
    db.commit()
    db.refresh(rag)
    return rag


@router.put("/ai/rag-context/{rag_id}", response_model=AIRAGContextResponse)
def update_rag_context(rag_id: int, rag_data: AIRAGContextUpdate, db: Session = Depends(get_db)) -> AIRAGContext:
    rag = ai_rag_context_repo.get_by_id(db, rag_id)
    if not rag:
        raise HTTPException(status_code=404, detail="RAG context not found")
    for field, value in rag_data.model_dump(exclude_unset=True).items():
        setattr(rag, field, value)
    db.commit()
    db.refresh(rag)
    return rag


@router.delete("/ai/rag-context/{rag_id}")
def delete_rag_context(rag_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = ai_rag_context_repo.delete(db, rag_id)
    if not success:
        raise HTTPException(status_code=404, detail="RAG context not found")
    return {"message": "RAG context deleted successfully"}


@router.get("/ai/permissions", response_model=List[AIPermissionLevelResponse])
def list_permissions(db: Session = Depends(get_db)) -> List[AIPermissionLevel]:
    return ai_permission_level_repo.get_enabled(db)


@router.post("/ai/permissions", response_model=AIPermissionLevelResponse)
def create_permission(perm_data: AIPermissionLevelCreate, db: Session = Depends(get_db)) -> AIPermissionLevel:
    perm = AIPermissionLevel(
        permission_level=perm_data.permission_level,
        permission_name=perm_data.permission_name,
        description=perm_data.description,
        requires_confirm=perm_data.requires_confirm,
        is_enabled=perm_data.is_enabled,
    )
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.put("/ai/permissions/{perm_id}", response_model=AIPermissionLevelResponse)
def update_permission(perm_id: int, perm_data: AIPermissionLevelUpdate, db: Session = Depends(get_db)) -> AIPermissionLevel:
    perm = ai_permission_level_repo.get_by_id(db, perm_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission level not found")
    for field, value in perm_data.model_dump(exclude_unset=True).items():
        setattr(perm, field, value)
    db.commit()
    db.refresh(perm)
    return perm


@router.delete("/ai/permissions/{perm_id}")
def delete_permission(perm_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    success = ai_permission_level_repo.delete(db, perm_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission level not found")
    return {"message": "Permission level deleted successfully"}


@router.get("/ai/usage-stats", response_model=AIUsageStatsResponse)
def get_usage_stats(db: Session = Depends(get_db)) -> AIUsageStatsResponse:
    today = datetime.now().strftime("%Y-%m-%d")
    stats = ai_usage_stats_repo.get_by_date(db, today)
    total_requests = sum(s.request_count for s in stats)
    total_cost = sum(s.cost_usd for s in stats)
    input_tokens = sum(s.input_tokens for s in stats)
    output_tokens = sum(s.output_tokens for s in stats)
    return AIUsageStatsResponse(
        total_requests=total_requests,
        total_cost=total_cost,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


@router.get("/ai/audit-logs", response_model=List[AIAuditLogResponse])
def list_audit_logs(db: Session = Depends(get_db)) -> List[AIAuditLog]:
    return ai_audit_log_repo.get_recent(db, limit=100)


# ============ 路由挂载 ============

app.include_router(router, prefix="/api")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    app.mount("/favicon.png", StaticFiles(directory=FRONTEND_DIST, html=False), name="favicon")


@app.get("/{path:path}")
async def serve_spa_fallback(path: str):
    if path.startswith("api/") or path == "api":
        raise HTTPException(status_code=404, detail="Not Found")
    if "." in path:
        raise HTTPException(status_code=404, detail="Not Found")
    from fastapi.responses import FileResponse
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
