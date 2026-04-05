from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
import shutil
import time
import secrets

from models import init_db, get_db, Task, Log, EnvVar, AlertConfig, NodeFlow, SystemSettings, AIProvider, AIModel, AIFeatureRouting, AIPromptTemplate, AISemanticCache, AIRAGContext, AIPermissionLevel, AIUsageStats, AIAuditLog
from schemas import (
    TaskCreate, TaskUpdate, TaskResponse, LogResponse,
    EnvVarCreate, EnvVarUpdate, EnvVarResponse,
    AlertConfigCreate, AlertConfigUpdate, AlertConfigResponse,
    SystemStats, ScratchpadRequest, ScratchpadResponse, ExportData,
    AIScriptRequest, AIScriptResponse, AIDiagnoseRequest, AIDiagnoseResponse,
    AICodeReviewRequest, AICodeReviewResponse, AINLPCronRequest, AINLPCronResponse,
    AISummarizeLogRequest, AISummarizeLogResponse, AIGenerateDocRequest, AIGenerateDocResponse,
    AIHumanizeAlertRequest, AIHumanizeAlertResponse,
    WebhookTriggerRequest, WebhookTriggerResponse,
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
from scheduler import add_task_job, remove_task_job, execute_task_now, start_scheduler, stop_scheduler
from ai_service import ai_service, generate_webhook_token, extract_requirements, parse_cron_human
from docker_runner import run_in_docker, extract_requirements_from_code, DOCKER_AVAILABLE

app = FastAPI(title="PyCron-Master API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCRIPTS_DIR = "./scripts"


@app.on_event("startup")
def startup_event():
    init_db()
    migrate_database()
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    start_scheduler()


def migrate_database():
    """Auto-migrate database to add new columns and tables"""
    import sqlite3
    import os

    db_path = "./pycron.db"
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]

    # New columns for tasks table
    cursor.execute("PRAGMA table_info(tasks)")
    tasks_cols = [col[1] for col in cursor.fetchall()]

    new_task_columns = {
        'webhook_enabled': 'ALTER TABLE tasks ADD COLUMN webhook_enabled BOOLEAN DEFAULT 0',
        'webhook_token': 'ALTER TABLE tasks ADD COLUMN webhook_token TEXT',
        'description': 'ALTER TABLE tasks ADD COLUMN description TEXT',
        'use_docker': 'ALTER TABLE tasks ADD COLUMN use_docker BOOLEAN DEFAULT 0',
        'docker_image': 'ALTER TABLE tasks ADD COLUMN docker_image TEXT',
    }

    for col, sql in new_task_columns.items():
        if col not in tasks_cols:
            try:
                cursor.execute(sql)
                print(f"Migrated: Added {col} column to tasks table")
            except Exception as e:
                print(f"Column {col} already exists: {e}")

    # New columns for alert_configs
    cursor.execute("PRAGMA table_info(alert_configs)")
    alert_cols = [col[1] for col in cursor.fetchall()]

    if 'ai_humanize' not in alert_cols:
        try:
            cursor.execute("ALTER TABLE alert_configs ADD COLUMN ai_humanize BOOLEAN DEFAULT 0")
            print("Migrated: Added ai_humanize column to alert_configs")
        except Exception as e:
            print(f"Column ai_humanize already exists: {e}")

    # Create system_settings table
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

    # Create node_flows table
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

    # ============ AI Hub Tables ============

    # Create ai_providers table
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

    # Create ai_models table
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

    # Create ai_feature_routing table
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

    # Create ai_prompt_templates table
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

    # Create ai_semantic_cache table
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

    # Create ai_rag_context table
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

    # Create ai_permissions table
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
        # Insert default permissions
        cursor.execute("""INSERT INTO ai_permissions (permission_level, permission_name, description, requires_confirm, is_enabled) VALUES
            (1, 'dry_run', '仅建议 - AI 仅提供建议，不执行任何修改', 0, 1),
            (2, 'script_replace', '允许一键替换脚本 - AI 可以修改并替换脚本内容', 1, 1),
            (3, 'config_modify', '允许修改配置 - AI 可以修改任务配置并自动重试', 1, 1)""")
        print("Migrated: Created ai_permissions table with defaults")

    # Create ai_usage_stats table
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

    # Create ai_audit_logs table
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


@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


@app.get("/")
def root():
    return {"message": "PyCron-Master API is running"}


# System Stats Endpoint
@app.get("/system/stats", response_model=SystemStats)
def get_system_stats():
    """Get real-time system resource usage"""
    try:
        import psutil
        import os
        cpu = psutil.cpu_percent(interval=None)  # Non-blocking
        memory = psutil.virtual_memory()
        # Cross-platform disk usage: use current working directory's drive on Windows
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
        # Fallback if psutil not installed
        return SystemStats(
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_percent=0.0,
            memory_used_gb=0.0,
            memory_total_gb=0.0,
            disk_used_gb=0.0,
            disk_total_gb=0.0
        )


# Task CRUD endpoints
@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks


# Task execution history / timeline data
@app.get("/tasks/timeline")
def get_tasks_timeline(db: Session = Depends(get_db)):
    """Get task execution history for timeline visualization (last 24 hours)"""
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(hours=24)

    logs = db.query(Log).filter(Log.start_time >= cutoff).order_by(Log.start_time.desc()).all()

    # Optimization: Only fetch task IDs that appear in logs, not all tasks
    task_ids = list(set(log.task_id for log in logs))
    if task_ids:
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
        task_map = {t.id: t.name for t in tasks}
    else:
        task_map = {}

    timeline = []
    for log in logs:
        duration = None
        if log.end_time and log.start_time:
            duration = (log.end_time - log.start_time).total_seconds()

        timeline.append({
            "id": log.id,
            "task_id": log.task_id,
            "task_name": task_map.get(log.task_id, "Unknown"),
            "start_time": log.start_time.isoformat() if log.start_time else None,
            "end_time": log.end_time.isoformat() if log.end_time else None,
            "duration": duration,
            "exit_code": log.exit_code,
            "status": "success" if log.exit_code == 0 else "failed"
        })

    return timeline


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    remove_task_job(task_id)
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@app.post("/tasks/{task_id}/run")
def run_task_now(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == "running":
        raise HTTPException(status_code=400, detail="Task is already running")

    execute_task_now(task_id)
    return {"message": "Task execution started"}


# Script upload
@app.post("/scripts/upload")
def upload_script(file: UploadFile = File(...)):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are allowed")

    file_path = os.path.join(SCRIPTS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "path": file_path}


@app.post("/scripts/upload-text")
def upload_script_text(filename: str, content: str):
    """Upload script as raw text content"""
    if not filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are allowed")

    file_path = os.path.join(SCRIPTS_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"filename": filename, "path": file_path}


# Log endpoints
@app.get("/tasks/{task_id}/logs", response_model=List[LogResponse])
def get_task_logs(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    logs = db.query(Log).filter(Log.task_id == task_id).order_by(Log.start_time.desc()).all()
    return logs


@app.get("/logs/search")
def search_logs(
    keyword: Optional[str] = None,
    task_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    exit_code: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """Search logs with filters and pagination"""
    query = db.query(Log)

    # Apply ALL filters before counting and pagination
    if task_id:
        query = query.filter(Log.task_id == task_id)
    if exit_code is not None:
        query = query.filter(Log.exit_code == exit_code)
    if start_date:
        query = query.filter(Log.start_time >= start_date)
    if end_date:
        query = query.filter(Log.start_time <= end_date)
    if keyword:
        keyword_lower = keyword.lower()
        query = query.filter(func.lower(Log.output).like(f"%{keyword_lower}%"))

    # Get total count after all filters applied
    total = query.count()

    # Order and apply pagination at database level
    logs = query.order_by(Log.start_time.desc()).offset((page - 1) * size).limit(size).all()

    return {"total": total, "items": logs}


@app.get("/logs/{log_id}", response_model=LogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@app.get("/tasks/{task_id}/logs/stream")
def stream_logs(task_id: int):
    """SSE endpoint for real-time log streaming"""
    async def event_generator():
        import asyncio
        import json
        from models import SessionLocal, Log

        last_log_id = 0
        while True:
            db = SessionLocal()
            try:
                new_logs = db.query(Log).filter(
                    Log.task_id == task_id,
                    Log.id > last_log_id
                ).order_by(Log.start_time.desc()).limit(10).all()

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


@app.get("/logs/{log_id}/download")
def download_log(log_id: int, db: Session = Depends(get_db)):
    """Download a single log as a .log file"""
    from fastapi.responses import Response

    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    content = f"=== PyCron-Master Log #{log.id} ===\n"
    content += f"Task ID: {log.task_id}\n"
    content += f"Start Time: {log.start_time}\n"
    content += f"End Time: {log.end_time}\n"
    content += f"Exit Code: {log.exit_code}\n"
    content += f"\n=== Output ===\n{log.output or '// No output'}\n"

    return Response(content=content.encode(), media_type="text/plain", headers={
        "Content-Disposition": f"attachment; filename=log_{log_id}.log"
    })


# ============ Environment Variables ============

@app.get("/env-vars", response_model=List[EnvVarResponse])
def list_env_vars(db: Session = Depends(get_db)):
    return db.query(EnvVar).all()


@app.post("/env-vars", response_model=EnvVarResponse)
def create_env_var(env_data: EnvVarCreate, db: Session = Depends(get_db)):
    existing = db.query(EnvVar).filter(EnvVar.key == env_data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Environment variable with this key already exists")

    env_var = EnvVar(
        key=env_data.key,
        value=env_data.value,
        description=env_data.description,
        is_secret=env_data.is_secret,
    )
    db.add(env_var)
    db.commit()
    db.refresh(env_var)
    return env_var


@app.put("/env-vars/{env_id}", response_model=EnvVarResponse)
def update_env_var(env_id: int, env_data: EnvVarUpdate, db: Session = Depends(get_db)):
    env_var = db.query(EnvVar).filter(EnvVar.id == env_id).first()
    if not env_var:
        raise HTTPException(status_code=404, detail="Environment variable not found")

    if env_data.key is not None:
        existing = db.query(EnvVar).filter(EnvVar.key == env_data.key, EnvVar.id != env_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Environment variable with this key already exists")
        env_var.key = env_data.key
    if env_data.value is not None:
        env_var.value = env_data.value
    if env_data.description is not None:
        env_var.description = env_data.description
    if env_data.is_secret is not None:
        env_var.is_secret = env_data.is_secret

    db.commit()
    db.refresh(env_var)
    return env_var


@app.delete("/env-vars/{env_id}")
def delete_env_var(env_id: int, db: Session = Depends(get_db)):
    env_var = db.query(EnvVar).filter(EnvVar.id == env_id).first()
    if not env_var:
        raise HTTPException(status_code=404, detail="Environment variable not found")

    db.delete(env_var)
    db.commit()
    return {"message": "Environment variable deleted successfully"}


@app.get("/env-vars/export")
def export_env_vars(db: Session = Depends(get_db)):
    """Export env vars as a dict for task execution"""
    env_vars = db.query(EnvVar).all()
    return {ev.key: ev.value for ev in env_vars}


# ============ Alert Configs ============

@app.get("/alerts", response_model=List[AlertConfigResponse])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(AlertConfig).all()


@app.post("/alerts", response_model=AlertConfigResponse)
def create_alert(alert_data: AlertConfigCreate, db: Session = Depends(get_db)):
    alert = AlertConfig(
        name=alert_data.name,
        webhook_url=alert_data.webhook_url,
        events=alert_data.events,
        is_active=alert_data.is_active,
        ai_humanize=alert_data.ai_humanize,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@app.put("/alerts/{alert_id}", response_model=AlertConfigResponse)
def update_alert(alert_id: int, alert_data: AlertConfigUpdate, db: Session = Depends(get_db)):
    alert = db.query(AlertConfig).filter(AlertConfig.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert configuration not found")

    if alert_data.name is not None:
        alert.name = alert_data.name
    if alert_data.webhook_url is not None:
        alert.webhook_url = alert_data.webhook_url
    if alert_data.events is not None:
        alert.events = alert_data.events
    if alert_data.is_active is not None:
        alert.is_active = alert_data.is_active
    if alert_data.ai_humanize is not None:
        alert.ai_humanize = alert_data.ai_humanize

    db.commit()
    db.refresh(alert)
    return alert


@app.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(AlertConfig).filter(AlertConfig.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert configuration not found")

    db.delete(alert)
    db.commit()
    return {"message": "Alert configuration deleted successfully"}


# ============ Scratchpad ============

@app.post("/scratchpad", response_model=ScratchpadResponse)
def execute_scratchpad(req: ScratchpadRequest, db: Session = Depends(get_db)):
    """Execute temporary Python code and return result"""
    import subprocess
    import sys
    import tempfile

    start_time = time.time()

    # Create temp file with code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(req.code)
        temp_path = f.name

    try:
        # Determine interpreter
        interpreter = req.interpreter_path or sys.executable

        # Get env vars
        env_vars = db.query(EnvVar).all()
        env_dict = {ev.key: ev.value for ev in env_vars}
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

    return ScratchpadResponse(
        output=output,
        exit_code=exit_code,
        execution_time=round(execution_time, 3)
    )


# ============ Export / Import ============

@app.get("/export")
def export_config(db: Session = Depends(get_db)):
    """Export all configuration as JSON"""
    tasks = db.query(Task).all()
    env_vars = db.query(EnvVar).all()
    alerts = db.query(AlertConfig).all()

    return ExportData(
        tasks=tasks,
        env_vars=env_vars,
        alert_configs=alerts,
        version="1.0.0"
    )


@app.post("/import")
def import_config(data: ExportData, db: Session = Depends(get_db)):
    """Import configuration from JSON"""
    imported_tasks = 0
    imported_envs = 0
    imported_alerts = 0

    # Import tasks
    for task_data in data.tasks:
        existing = db.query(Task).filter(Task.id == task_data.id).first()
        if existing:
            # Update existing
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

    # Import env vars
    for env_data in data.env_vars:
        existing = db.query(EnvVar).filter(EnvVar.key == env_data.key).first()
        if not existing:
            env_var = EnvVar(
                key=env_data.key,
                value=env_data.value,
                description=env_data.description,
                is_secret=env_data.is_secret,
            )
            db.add(env_var)
            imported_envs += 1

    # Import alerts
    for alert_data in data.alert_configs:
        existing = db.query(AlertConfig).filter(AlertConfig.name == alert_data.name).first()
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


# ============ System Settings ============

def get_setting(db: Session, key: str) -> Optional[str]:
    """Get a system setting value"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    return setting.value if setting else None


def set_setting(db: Session, key: str, value: str, description: str = None) -> None:
    """Set a system setting value"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = SystemSettings(key=key, value=value, description=description)
        db.add(setting)
    db.commit()


@app.get("/system/settings", response_model=SystemSettingsResponse)
def get_system_settings(db: Session = Depends(get_db)):
    """Get all system settings (AI config)"""
    return SystemSettingsResponse(
        minimax_api_key=get_setting(db, "minimax_api_key"),
        minimax_group_id=get_setting(db, "minimax_group_id"),
        ai_enabled=bool(get_setting(db, "minimax_api_key") and get_setting(db, "minimax_group_id"))
    )


@app.put("/system/settings", response_model=SystemSettingsResponse)
def update_system_settings(settings: SystemSettingsUpdate, db: Session = Depends(get_db)):
    """Update system settings (AI config)"""
    if settings.minimax_api_key is not None:
        set_setting(db, "minimax_api_key", settings.minimax_api_key, "Minimax API Key for AI features")
    if settings.minimax_group_id is not None:
        set_setting(db, "minimax_group_id", settings.minimax_group_id, "Minimax Group ID for AI features")

    # Update ai_service instance
    if settings.minimax_api_key is not None:
        ai_service.api_key = settings.minimax_api_key
    if settings.minimax_group_id is not None:
        ai_service.group_id = settings.minimax_group_id

    return SystemSettingsResponse(
        minimax_api_key=get_setting(db, "minimax_api_key"),
        minimax_group_id=get_setting(db, "minimax_group_id"),
        ai_enabled=bool(get_setting(db, "minimax_api_key") and get_setting(db, "minimax_group_id"))
    )


@app.post("/system/settings/test-ai")
def test_ai_connection(db: Session = Depends(get_db)):
    """Test AI API connection"""
    api_key = get_setting(db, "minimax_api_key")
    group_id = get_setting(db, "minimax_group_id")

    if not api_key or not group_id:
        return {"success": False, "message": "API key or Group ID not configured"}

    # Temporarily set the credentials
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


# ============ AI Features ============

@app.post("/ai/generate-script", response_model=AIScriptResponse)
def ai_generate_script(req: AIScriptRequest):
    """Generate Python script from natural language description (Text-to-Script)"""
    code = ai_service.generate_script(req.description)
    return AIScriptResponse(code=code, used_ai=bool(ai_service.api_key))


@app.post("/ai/diagnose-error", response_model=AIDiagnoseResponse)
def ai_diagnose_error(req: AIDiagnoseRequest):
    """AI-powered error diagnosis and fix suggestions (Auto-Fix)"""
    diagnosis = ai_service.diagnose_error(req.error_traceback, req.script_content)
    return AIDiagnoseResponse(diagnosis=diagnosis, used_ai=bool(ai_service.api_key))


@app.post("/ai/code-review", response_model=AICodeReviewResponse)
def ai_code_review(req: AICodeReviewRequest):
    """AI code review for performance and best practices (Code Simplifier)"""
    review = ai_service.code_review(req.code)
    return AICodeReviewResponse(review=review, used_ai=bool(ai_service.api_key))


@app.post("/ai/nlp-to-cron", response_model=AINLPCronResponse)
def ai_nlp_to_cron(req: AINLPCronRequest):
    """Convert natural language to Cron expression (NLP to Cron)"""
    result = ai_service.nlp_to_cron(req.natural_language)

    # Parse result - expected format: "cron_expr\n说明：..."
    lines = result.strip().split('\n')
    cron_expr = lines[0].strip() if lines else req.natural_language
    description = '\n'.join(lines[1:]) if len(lines) > 1 else parse_cron_human(cron_expr)

    return AINLPCronResponse(
        cron_expr=cron_expr,
        description=description,
        used_ai=bool(ai_service.api_key)
    )


@app.post("/ai/summarize-log", response_model=AISummarizeLogResponse)
def ai_summarize_log(req: AISummarizeLogRequest):
    """AI-powered log summarization (Log Summarization)"""
    summary = ai_service.summarize_log(req.log_content)
    return AISummarizeLogResponse(summary=summary, used_ai=bool(ai_service.api_key))


@app.post("/ai/generate-doc", response_model=AIGenerateDocResponse)
def ai_generate_doc(req: AIGenerateDocRequest):
    """Auto-generate documentation from Python code (Auto-Doc)"""
    doc = ai_service.generate_doc(req.code)
    return AIGenerateDocResponse(doc=doc, used_ai=bool(ai_service.api_key))


@app.post("/ai/humanize-alert", response_model=AIHumanizeAlertResponse)
def ai_humanize_alert(req: AIHumanizeAlertRequest):
    """Convert technical alerts to human-readable messages (AI Alert)"""
    message = ai_service.humanize_alert(req.alert_type, req.task_name, req.error_info)
    return AIHumanizeAlertResponse(message=message, used_ai=bool(ai_service.api_key))


@app.get("/ai/capabilities")
def ai_capabilities():
    """Check AI service capabilities and status"""
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


# ============ Webhook Trigger System ============

@app.get("/webhook/{token}")
def trigger_webhook(token: str, db: Session = Depends(get_db)):
    """Trigger task execution via webhook (public endpoint, no auth required)"""
    # Find task by webhook token
    task = db.query(Task).filter(Task.webhook_token == token).first()

    if not task:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Invalid webhook token"}
        )

    if not task.webhook_enabled:
        return JSONResponse(
            status_code=403,
            content={"success": False, "message": "Webhook trigger is disabled for this task"}
        )

    # Execute the task
    execute_task_now(task.id)

    return {
        "success": True,
        "message": f"Task '{task.name}' execution triggered",
        "task_id": task.id,
        "task_status": "running"
    }


@app.post("/webhook/{token}")
def trigger_webhook_post(token: str, request: WebhookTriggerRequest, db: Session = Depends(get_db)):
    """Trigger task execution via webhook with payload"""
    task = db.query(Task).filter(Task.webhook_token == token).first()

    if not task:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Invalid webhook token"}
        )

    if not task.webhook_enabled:
        return JSONResponse(
            status_code=403,
            content={"success": False, "message": "Webhook trigger is disabled"}
        )

    # Store payload in environment for the task to access
    if request.payload:
        for key, value in request.payload.items():
            env_var = db.query(EnvVar).filter(
                EnvVar.key == f"WEBHOOK_PAYLOAD_{key.upper()}"
            ).first()
            if not env_var:
                env_var = EnvVar(
                    key=f"WEBHOOK_PAYLOAD_{key.upper()}",
                    value=str(value),
                    description=f"Webhook payload from trigger"
                )
                db.add(env_var)
        db.commit()

    execute_task_now(task.id)

    return {
        "success": True,
        "message": f"Task '{task.name}' triggered with payload",
        "task_id": task.id
    }


@app.post("/tasks/{task_id}/enable-webhook")
def enable_webhook(task_id: int, db: Session = Depends(get_db)):
    """Enable webhook for a task and generate token"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.webhook_token:
        task.webhook_token = generate_webhook_token()

    task.webhook_enabled = True
    db.commit()
    db.refresh(task)

    webhook_url = f"/webhook/{task.webhook_token}"

    return {
        "success": True,
        "webhook_url": webhook_url,
        "webhook_token": task.webhook_token,
        "task_id": task.id
    }


@app.post("/tasks/{task_id}/disable-webhook")
def disable_webhook(task_id: int, db: Session = Depends(get_db)):
    """Disable webhook for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.webhook_enabled = False
    db.commit()

    return {"success": True, "message": "Webhook disabled"}


@app.get("/tasks/{task_id}/webhook-info")
def get_webhook_info(task_id: int, db: Session = Depends(get_db)):
    """Get webhook URL and status for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.id,
        "task_name": task.name,
        "webhook_enabled": task.webhook_enabled,
        "webhook_token": task.webhook_token,
        "webhook_url": f"/webhook/{task.webhook_token}" if task.webhook_token else None
    }


# ============ Node Flow (Visual DAG Editor) ============

@app.get("/node-flows", response_model=List[NodeFlowResponse])
def list_node_flows(db: Session = Depends(get_db)):
    """List all node flows"""
    flows = db.query(NodeFlow).all()
    return flows


@app.get("/node-flows/{flow_id}", response_model=NodeFlowResponse)
def get_node_flow(flow_id: int, db: Session = Depends(get_db)):
    """Get a specific node flow"""
    flow = db.query(NodeFlow).filter(NodeFlow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Node flow not found")
    return flow


@app.post("/node-flows", response_model=NodeFlowResponse)
def create_node_flow(flow_data: NodeFlowCreate, db: Session = Depends(get_db)):
    """Create a new node flow"""
    flow = NodeFlow(
        name=flow_data.name,
        description=flow_data.description,
        nodes=flow_data.nodes,
        edges=flow_data.edges,
        is_active=flow_data.is_active
    )
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return flow


@app.put("/node-flows/{flow_id}", response_model=NodeFlowResponse)
def update_node_flow(flow_id: int, flow_data: NodeFlowUpdate, db: Session = Depends(get_db)):
    """Update a node flow"""
    flow = db.query(NodeFlow).filter(NodeFlow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Node flow not found")

    if flow_data.name is not None:
        flow.name = flow_data.name
    if flow_data.description is not None:
        flow.description = flow_data.description
    if flow_data.nodes is not None:
        flow.nodes = flow_data.nodes
    if flow_data.edges is not None:
        flow.edges = flow_data.edges
    if flow_data.is_active is not None:
        flow.is_active = flow_data.is_active

    db.commit()
    db.refresh(flow)
    return flow


@app.delete("/node-flows/{flow_id}")
def delete_node_flow(flow_id: int, db: Session = Depends(get_db)):
    """Delete a node flow"""
    flow = db.query(NodeFlow).filter(NodeFlow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Node flow not found")

    db.delete(flow)
    db.commit()
    return {"message": "Node flow deleted successfully"}


@app.post("/node-flows/{flow_id}/execute")
def execute_node_flow(flow_id: int, db: Session = Depends(get_db)):
    """Execute a node flow (run all tasks in topological order)"""
    import json
    from collections import deque

    flow = db.query(NodeFlow).filter(NodeFlow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Node flow not found")

    try:
        nodes = json.loads(flow.nodes)
        edges = json.loads(flow.edges)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid node/edge data")

    # Build adjacency list and in-degree map
    in_degree = {node['id']: 0 for node in nodes}
    adjacency = {node['id']: [] for node in nodes}

    for edge in edges:
        adjacency[edge['source']].append(edge['target'])
        in_degree[edge['target']] += 1

    # Use deque for O(1) popleft instead of O(n) list.pop(0)
    queue = deque([node['id'] for node in nodes if in_degree[node['id']] == 0])
    execution_order = []

    while queue:
        node_id = queue.popleft()
        execution_order.append(node_id)

        for neighbor in adjacency[node_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Pre-load all tasks in one query to avoid N+1 problem
    task_ids = [n['task_id'] for n in nodes if n.get('task_id')]
    if task_ids:
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
        task_map = {t.id: t for t in tasks}
    else:
        task_map = {}

    # Build node map for O(1) lookup instead of O(n) linear search
    node_map = {n['id']: n for n in nodes}

    # Execute tasks in order
    results = []
    for node_id in execution_order:
        node = node_map.get(node_id)
        if node and node.get('task_id'):
            task = task_map.get(node['task_id'])
            if task:
                execute_task_now(task.id)
                results.append({
                    "node_id": node_id,
                    "task_id": task.id,
                    "task_name": task.name,
                    "status": "triggered"
                })

    return {
        "success": True,
        "flow_id": flow_id,
        "execution_order": execution_order,
        "results": results
    }


# ============ Docker Sandbox Runner ============

@app.post("/docker/run", response_model=DockerRunResponse)
def docker_sandbox_run(req: DockerRunRequest, db: Session = Depends(get_db)):
    """Run Python code in an isolated Docker container"""
    if not DOCKER_AVAILABLE:
        return DockerRunResponse(
            success=False,
            output="",
            exit_code=-1,
            execution_time=0,
            error="Docker is not available on this system"
        )

    # Get environment variables
    env_vars = db.query(EnvVar).all()
    env_dict = {ev.key: ev.value for ev in env_vars}
    env_dict['PYTHONUNBUFFERED'] = '1'

    success, output, exit_code, exec_time = run_in_docker(
        code=req.code,
        requirements=req.requirements,
        docker_image=req.docker_image,
        timeout=req.timeout,
        environment=env_dict
    )

    return DockerRunResponse(
        success=success,
        output=output,
        exit_code=exit_code,
        execution_time=exec_time,
        error=None if success else output
    )


@app.post("/docker/extract-requirements")
def docker_extract_requirements(code: str = Body(..., media_type="text/plain")):
    """Extract pip requirements from Python code"""
    requirements = extract_requirements_from_code(code)
    return {"requirements": requirements}


# ============ Updated Task Endpoints with Phase 8 Fields ============

@app.post("/tasks", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        name=task_data.name,
        script_path=task_data.script_path,
        cron_expr=task_data.cron_expr,
        is_active=task_data.is_active,
        interpreter_path=task_data.interpreter_path,
        depends_on=task_data.depends_on,
        timeout=task_data.timeout or 300,
        webhook_enabled=task_data.webhook_enabled,
        webhook_token=generate_webhook_token() if task_data.webhook_enabled else None,
        description=task_data.description,
        use_docker=task_data.use_docker,
        docker_image=task_data.docker_image,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    if task.cron_expr and task.is_active:
        add_task_job(task)

    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_data.name is not None:
        task.name = task_data.name
    if task_data.script_path is not None:
        task.script_path = task_data.script_path
    if task_data.cron_expr is not None:
        task.cron_expr = task_data.cron_expr
    if task_data.is_active is not None:
        task.is_active = task_data.is_active
    if task_data.interpreter_path is not None:
        task.interpreter_path = task_data.interpreter_path
    if task_data.depends_on is not None:
        task.depends_on = task_data.depends_on
    if task_data.timeout is not None:
        task.timeout = task_data.timeout
    if task_data.webhook_enabled is not None:
        task.webhook_enabled = task_data.webhook_enabled
        if task_data.webhook_enabled and not task.webhook_token:
            task.webhook_token = generate_webhook_token()
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.use_docker is not None:
        task.use_docker = task_data.use_docker
    if task_data.docker_image is not None:
        task.docker_image = task_data.docker_image

    db.commit()
    db.refresh(task)

    if task.is_active and task.cron_expr:
        add_task_job(task)
    else:
        remove_task_job(task_id)

    return task


# ============ AI Hub API Endpoints ============

@app.get("/ai/providers", response_model=List[AIProviderResponse])
def list_ai_providers(db: Session = Depends(get_db)):
    """List all AI providers"""
    return db.query(AIProvider).order_by(AIProvider.priority).all()


@app.post("/ai/providers", response_model=AIProviderResponse)
def create_ai_provider(provider_data: AIProviderCreate, db: Session = Depends(get_db)):
    """Create a new AI provider"""
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


@app.put("/ai/providers/{provider_id}", response_model=AIProviderResponse)
def update_ai_provider(provider_id: int, provider_data: AIProviderUpdate, db: Session = Depends(get_db)):
    """Update an AI provider"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="AI Provider not found")

    for field, value in provider_data.model_dump(exclude_unset=True).items():
        setattr(provider, field, value)

    db.commit()
    db.refresh(provider)
    return provider


@app.delete("/ai/providers/{provider_id}")
def delete_ai_provider(provider_id: int, db: Session = Depends(get_db)):
    """Delete an AI provider"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="AI Provider not found")

    db.delete(provider)
    db.commit()
    return {"message": "AI Provider deleted successfully"}


@app.get("/ai/models", response_model=List[AIModelResponse])
def list_ai_models(db: Session = Depends(get_db)):
    """List all AI models"""
    return db.query(AIModel).all()


@app.post("/ai/models", response_model=AIModelResponse)
def create_ai_model(model_data: AIModelCreate, db: Session = Depends(get_db)):
    """Create a new AI model"""
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


@app.put("/ai/models/{model_id}", response_model=AIModelResponse)
def update_ai_model(model_id: int, model_data: AIModelUpdate, db: Session = Depends(get_db)):
    """Update an AI model"""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found")

    for field, value in model_data.model_dump(exclude_unset=True).items():
        setattr(model, field, value)

    db.commit()
    db.refresh(model)
    return model


@app.delete("/ai/models/{model_id}")
def delete_ai_model(model_id: int, db: Session = Depends(get_db)):
    """Delete an AI model"""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found")

    db.delete(model)
    db.commit()
    return {"message": "AI Model deleted successfully"}


@app.get("/ai/feature-routing", response_model=List[AIFeatureRoutingResponse])
def list_feature_routing(db: Session = Depends(get_db)):
    """List all feature routing configurations"""
    return db.query(AIFeatureRouting).all()


@app.post("/ai/feature-routing", response_model=AIFeatureRoutingResponse)
def create_feature_routing(routing_data: AIFeatureRoutingCreate, db: Session = Depends(get_db)):
    """Create a new feature routing configuration"""
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


@app.put("/ai/feature-routing/{routing_id}", response_model=AIFeatureRoutingResponse)
def update_feature_routing(routing_id: int, routing_data: AIFeatureRoutingUpdate, db: Session = Depends(get_db)):
    """Update a feature routing configuration"""
    routing = db.query(AIFeatureRouting).filter(AIFeatureRouting.id == routing_id).first()
    if not routing:
        raise HTTPException(status_code=404, detail="Feature routing not found")

    for field, value in routing_data.model_dump(exclude_unset=True).items():
        setattr(routing, field, value)

    db.commit()
    db.refresh(routing)
    return routing


@app.delete("/ai/feature-routing/{routing_id}")
def delete_feature_routing(routing_id: int, db: Session = Depends(get_db)):
    """Delete a feature routing configuration"""
    routing = db.query(AIFeatureRouting).filter(AIFeatureRouting.id == routing_id).first()
    if not routing:
        raise HTTPException(status_code=404, detail="Feature routing not found")

    db.delete(routing)
    db.commit()
    return {"message": "Feature routing deleted successfully"}


@app.get("/ai/prompt-templates", response_model=List[AIPromptTemplateResponse])
def list_prompt_templates(db: Session = Depends(get_db)):
    """List all prompt templates"""
    return db.query(AIPromptTemplate).all()


@app.post("/ai/prompt-templates", response_model=AIPromptTemplateResponse)
def create_prompt_template(template_data: AIPromptTemplateCreate, db: Session = Depends(get_db)):
    """Create a new prompt template"""
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


@app.put("/ai/prompt-templates/{template_id}", response_model=AIPromptTemplateResponse)
def update_prompt_template(template_id: int, template_data: AIPromptTemplateUpdate, db: Session = Depends(get_db)):
    """Update a prompt template"""
    template = db.query(AIPromptTemplate).filter(AIPromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    for field, value in template_data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template


@app.delete("/ai/prompt-templates/{template_id}")
def delete_prompt_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a prompt template"""
    template = db.query(AIPromptTemplate).filter(AIPromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    db.delete(template)
    db.commit()
    return {"message": "Prompt template deleted successfully"}


@app.get("/ai/rag-context", response_model=List[AIRAGContextResponse])
def list_rag_contexts(db: Session = Depends(get_db)):
    """List all RAG contexts"""
    return db.query(AIRAGContext).all()


@app.post("/ai/rag-context", response_model=AIRAGContextResponse)
def create_rag_context(rag_data: AIRAGContextCreate, db: Session = Depends(get_db)):
    """Create a new RAG context"""
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


@app.put("/ai/rag-context/{rag_id}", response_model=AIRAGContextResponse)
def update_rag_context(rag_id: int, rag_data: AIRAGContextUpdate, db: Session = Depends(get_db)):
    """Update a RAG context"""
    rag = db.query(AIRAGContext).filter(AIRAGContext.id == rag_id).first()
    if not rag:
        raise HTTPException(status_code=404, detail="RAG context not found")

    for field, value in rag_data.model_dump(exclude_unset=True).items():
        setattr(rag, field, value)

    db.commit()
    db.refresh(rag)
    return rag


@app.delete("/ai/rag-context/{rag_id}")
def delete_rag_context(rag_id: int, db: Session = Depends(get_db)):
    """Delete a RAG context"""
    rag = db.query(AIRAGContext).filter(AIRAGContext.id == rag_id).first()
    if not rag:
        raise HTTPException(status_code=404, detail="RAG context not found")

    db.delete(rag)
    db.commit()
    return {"message": "RAG context deleted successfully"}


@app.get("/ai/permissions", response_model=List[AIPermissionLevelResponse])
def list_permissions(db: Session = Depends(get_db)):
    """List all AI permission levels"""
    return db.query(AIPermissionLevel).all()


@app.post("/ai/permissions", response_model=AIPermissionLevelResponse)
def create_permission(perm_data: AIPermissionLevelCreate, db: Session = Depends(get_db)):
    """Create a new AI permission level"""
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


@app.put("/ai/permissions/{perm_id}", response_model=AIPermissionLevelResponse)
def update_permission(perm_id: int, perm_data: AIPermissionLevelUpdate, db: Session = Depends(get_db)):
    """Update an AI permission level"""
    perm = db.query(AIPermissionLevel).filter(AIPermissionLevel.id == perm_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission level not found")

    for field, value in perm_data.model_dump(exclude_unset=True).items():
        setattr(perm, field, value)

    db.commit()
    db.refresh(perm)
    return perm


@app.delete("/ai/permissions/{perm_id}")
def delete_permission(perm_id: int, db: Session = Depends(get_db)):
    """Delete an AI permission level"""
    perm = db.query(AIPermissionLevel).filter(AIPermissionLevel.id == perm_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission level not found")

    db.delete(perm)
    db.commit()
    return {"message": "Permission level deleted successfully"}


@app.get("/ai/usage-stats", response_model=AIUsageStatsResponse)
def get_usage_stats(db: Session = Depends(get_db)):
    """Get AI usage statistics for today"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    stats = db.query(AIUsageStats).filter(AIUsageStats.date == today).all()

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


@app.get("/ai/audit-logs", response_model=List[AIAuditLogResponse])
def list_audit_logs(db: Session = Depends(get_db)):
    """List AI audit logs"""
    return db.query(AIAuditLog).order_by(AIAuditLog.created_at.desc()).limit(100).all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
