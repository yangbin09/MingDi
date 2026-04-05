from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from models import SessionLocal, Task, Log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
task_jobs = {}  # Maps task_id to job


def run_task(task_id: int):
    """Execute a task in a subprocess"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        task.status = "running"
        db.commit()

        log_entry = Log(
            task_id=task_id,
            start_time=datetime.utcnow(),
            output="",
            exit_code=None,
        )
        db.add(log_entry)
        db.commit()
        log_id = log_entry.id

        import subprocess
        import sys

        process = subprocess.Popen(
            [sys.executable, task.script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        output = ""
        try:
            stdout, stderr = process.communicate(timeout=300)
            output = stdout + stderr
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            output = "Task timed out after 300 seconds"
            exit_code = -1
            task.status = "timeout"
        except Exception as e:
            output = f"Error: {str(e)}"
            exit_code = -1
            task.status = "failed"
        else:
            if exit_code == 0:
                task.status = "success"
            else:
                task.status = "failed"

        log_entry.end_time = datetime.utcnow()
        log_entry.output = output
        log_entry.exit_code = exit_code
        task.last_run_time = log_entry.start_time
        db.commit()

    except Exception as e:
        logger.error(f"Error running task {task_id}: {e}")
        task.status = "failed"
        db.commit()
    finally:
        db.close()


def add_task_job(task: Task):
    """Add or update a scheduled job for a task"""
    if task.id in task_jobs:
        task_jobs[task.id].remove()
        del task_jobs[task.id]

    if task.is_active and task.cron_expr:
        try:
            parts = task.cron_expr.split()
            if len(parts) == 5:
                trigger = CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                )
            elif len(parts) == 6:
                trigger = CronTrigger(
                    second=parts[0],
                    minute=parts[1],
                    hour=parts[2],
                    day=parts[3],
                    month=parts[4],
                    day_of_week=parts[5],
                )
            else:
                trigger = CronTrigger.from_crontab(task.cron_expr)

            job = scheduler.add_job(
                run_task,
                trigger=trigger,
                args=[task.id],
                id=str(task.id),
                replace_existing=True,
            )
            task_jobs[task.id] = job
            logger.info(f"Scheduled task {task.id} with cron: {task.cron_expr}")
        except Exception as e:
            logger.error(f"Error scheduling task {task.id}: {e}")


def remove_task_job(task_id: int):
    """Remove a scheduled job"""
    if task_id in task_jobs:
        task_jobs[task_id].remove()
        del task_jobs[task_id]


def execute_task_now(task_id: int):
    """Execute a task immediately (bypass scheduler)"""
    import threading
    thread = threading.Thread(target=run_task, args=(task_id,))
    thread.start()


def load_active_tasks():
    """Load and reschedule all active tasks (for self-healing on restart)"""
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.is_active == True).all()
        for task in tasks:
            if task.cron_expr:
                add_task_job(task)
                if task.status == "running":
                    task.status = "idle"
                    db.commit()
        logger.info(f"Loaded {len(tasks)} active tasks")
    finally:
        db.close()


def start_scheduler():
    """Start the scheduler"""
    load_active_tasks()
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
