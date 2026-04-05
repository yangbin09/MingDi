from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import time

from models import init_db, get_db, Task, Log, EnvVar, AlertConfig
from schemas import (
    TaskCreate, TaskUpdate, TaskResponse, LogResponse,
    EnvVarCreate, EnvVarUpdate, EnvVarResponse,
    AlertConfigCreate, AlertConfigUpdate, AlertConfigResponse,
    SystemStats, ScratchpadRequest, ScratchpadResponse, ExportData
)
from scheduler import add_task_job, remove_task_job, execute_task_now, start_scheduler, stop_scheduler

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
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    start_scheduler()


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
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

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
    tasks = db.query(Task).all()
    task_map = {t.id: t.name for t in tasks}

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

    db.commit()
    db.refresh(task)

    if task.is_active and task.cron_expr:
        add_task_job(task)
    else:
        remove_task_job(task_id)

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


# Log endpoints
@app.get("/tasks/{task_id}/logs", response_model=List[LogResponse])
def get_task_logs(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    logs = db.query(Log).filter(Log.task_id == task_id).order_by(Log.start_time.desc()).all()
    return logs


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


# Advanced log search
@app.get("/logs/search")
def search_logs(
    keyword: Optional[str] = None,
    task_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    exit_code: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Search logs with filters"""
    query = db.query(Log)

    if task_id:
        query = query.filter(Log.task_id == task_id)
    if exit_code is not None:
        query = query.filter(Log.exit_code == exit_code)
    if start_date:
        query = query.filter(Log.start_time >= start_date)
    if end_date:
        query = query.filter(Log.start_time <= end_date)

    logs = query.order_by(Log.start_time.desc()).limit(100).all()

    # Filter by keyword in memory (for partial matching)
    if keyword:
        keyword = keyword.lower()
        logs = [l for l in logs if keyword in (l.output or "").lower()]

    return logs


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
