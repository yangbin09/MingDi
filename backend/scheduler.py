from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import os

from models import SessionLocal, Task, Log, EnvVar, AlertConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
task_jobs = {}  # Maps task_id to job

# Scripts directory - resolved relative to backend directory's parent
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")


def send_webhook_alert(task_name: str, event: str, message: str):
    """Send alert via webhook for task failure/timeout"""
    db = SessionLocal()
    try:
        alerts = db.query(AlertConfig).filter(AlertConfig.is_active == True).all()
        for alert in alerts:
            events = [e.strip() for e in alert.events.split(',')]
            if event in events:
                try:
                    import requests
                    payload = {
                        "msgtype": "text",
                        "text": {
                            "content": f"[PyCron-Master] {event.upper()}: {task_name}\n{message}"
                        }
                    }
                    requests.post(alert.webhook_url, json=payload, timeout=10)
                    logger.info(f"Webhook alert sent for {task_name}: {event}")
                except Exception as e:
                    logger.error(f"Failed to send webhook alert: {e}")
    finally:
        db.close()


def check_dependency(task_id: int) -> bool:
    """Check if the task's dependency completed successfully"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task or not task.depends_on:
            return True

        dep_task = db.query(Task).filter(Task.id == task.depends_on).first()
        if not dep_task:
            return True  # No dependency found, allow execution

        # Check if dependency task's last run was successful
        if dep_task.status == "success" and dep_task.last_run_time:
            # Ensure dependency ran after the last failure of this task
            last_log = db.query(Log).filter(
                Log.task_id == task_id,
                Log.exit_code != 0
            ).order_by(Log.start_time.desc()).first()

            if not last_log:
                return True  # No failures recorded

            # Dependency must have run after the last failure
            return dep_task.last_run_time > last_log.start_time

        return False
    finally:
        db.close()


def run_task(task_id: int):
    """Execute a task in a subprocess"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        # Check dependency
        if not check_dependency(task_id):
            logger.info(f"Task {task_id} skipped due to failed dependency")
            return

        task.status = "running"
        db.commit()

        log_entry = Log(
            task_id=task_id,
            start_time=datetime.now(),
            output="",
            exit_code=None,
        )
        db.add(log_entry)
        db.commit()
        log_id = log_entry.id

        import subprocess
        import sys

        # Get interpreter path
        interpreter = task.interpreter_path or sys.executable

        # Get environment variables
        env_vars = db.query(EnvVar).all()
        env_dict = {ev.key: ev.value for ev in env_vars}
        env_dict['PYTHONUNBUFFERED'] = '1'

        # Merge with current environment
        full_env = {**os.environ, **env_dict}

        # Resolve script path - extract filename and resolve from SCRIPTS_DIR
        script_name = os.path.basename(task.script_path)
        script_path = os.path.join(SCRIPTS_DIR, script_name)

        process = subprocess.Popen(
            [interpreter, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=full_env,
            cwd=SCRIPTS_DIR  # Set working directory to scripts folder
        )

        output = ""
        timeout = task.timeout or 300

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            output = stdout + stderr
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            output = f"Task timed out after {timeout} seconds"
            exit_code = -1
            task.status = "timeout"
            send_webhook_alert(task.name, "timeout", output)
        except Exception as e:
            output = f"Error: {str(e)}"
            exit_code = -1
            task.status = "failed"
            send_webhook_alert(task.name, "failed", output)
        else:
            if exit_code == 0:
                task.status = "success"
            else:
                task.status = "failed"
                send_webhook_alert(task.name, "failed", f"Exit code: {exit_code}\n{output[:500]}")

        log_entry.end_time = datetime.now()
        log_entry.output = output
        log_entry.exit_code = exit_code
        task.last_run_time = log_entry.start_time
        db.commit()

        # Trigger dependent tasks
        trigger_dependent_tasks(task_id)

    except Exception as e:
        logger.error(f"Error running task {task_id}: {e}")
        task.status = "failed"
        db.commit()
        send_webhook_alert(task.name if 'task' in locals() else "Unknown", "failed", str(e))
    finally:
        db.close()


def trigger_dependent_tasks(completed_task_id: int):
    """Trigger tasks that depend on the completed task"""
    db = SessionLocal()
    try:
        dependent_tasks = db.query(Task).filter(Task.depends_on == completed_task_id).all()
        for dep_task in dependent_tasks:
            if dep_task.is_active and dep_task.status != "running":
                if check_dependency(dep_task.id):
                    logger.info(f"Triggering dependent task {dep_task.id}: {dep_task.name}")
                    execute_task_now(dep_task.id)
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
