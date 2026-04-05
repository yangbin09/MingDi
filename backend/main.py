from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from models import init_db, get_db, Task, Log
from schemas import TaskCreate, TaskUpdate, TaskResponse, LogResponse
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


# Task CRUD endpoints
@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
