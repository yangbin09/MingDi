#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Service - Business logic for Task operations.
Encapsulates scheduler integration and webhook token generation.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from models import Task
from schemas import TaskCreate, TaskUpdate
from repositories import task_repo
from scheduler import add_task_job, remove_task_job, execute_task_now
from ai_service import generate_webhook_token


class TaskService:
    """Service layer for Task business logic"""

    def list_tasks(self, db: Session) -> List[Task]:
        """Get all tasks"""
        return task_repo.get_all(db)

    def get_task(self, db: Session, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        return task_repo.get_by_id(db, task_id)

    def create_task(self, db: Session, task_data: TaskCreate) -> Task:
        """Create a new task and register with scheduler if active"""
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
            log_retention_count=task_data.log_retention_count or 100,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        if task.cron_expr and task.is_active:
            add_task_job(task)

        return task

    def update_task(self, db: Session, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update task and sync scheduler state"""
        task = task_repo.get_by_id(db, task_id)
        if not task:
            return None

        update_dict = task_data.model_dump(exclude_unset=True)

        # Handle webhook token generation
        if update_dict.get("webhook_enabled") and not task.webhook_token:
            update_dict["webhook_token"] = generate_webhook_token()

        # Apply updates
        for key, value in update_dict.items():
            if value is not None and hasattr(task, key):
                setattr(task, key, value)

        db.commit()
        db.refresh(task)

        # Sync scheduler
        if task.is_active and task.cron_expr:
            add_task_job(task)
        else:
            remove_task_job(task_id)

        return task

    def delete_task(self, db: Session, task_id: int) -> bool:
        """Delete task and remove from scheduler"""
        task = task_repo.get_by_id(db, task_id)
        if not task:
            return False

        remove_task_job(task_id)
        db.delete(task)
        db.commit()
        return True

    def run_task_now(self, db: Session, task_id: int) -> Optional[Task]:
        """Trigger immediate task execution"""
        task = task_repo.get_by_id(db, task_id)
        if not task:
            return None

        if task.status == "running":
            raise ValueError("Task is already running")

        execute_task_now(task_id)
        return task

    def get_task_dependents(self, db: Session, task_id: int) -> List[Task]:
        """Get tasks that depend on this task"""
        return task_repo.get_dependents(db, task_id)

    def enable_webhook(self, db: Session, task_id: int) -> Optional[Dict[str, Any]]:
        """Enable webhook for task"""
        task = task_repo.get_by_id(db, task_id)
        if not task:
            return None

        if not task.webhook_token:
            task.webhook_token = generate_webhook_token()
        task.webhook_enabled = True
        db.commit()
        db.refresh(task)

        return {
            "success": True,
            "webhook_url": f"/webhook/{task.webhook_token}",
            "webhook_token": task.webhook_token,
            "task_id": task.id
        }

    def disable_webhook(self, db: Session, task_id: int) -> bool:
        """Disable webhook for task"""
        task = task_repo.get_by_id(db, task_id)
        if not task:
            return False

        task.webhook_enabled = False
        db.commit()
        return True

    def get_webhook_info(self, db: Session, task_id: int) -> Optional[Dict[str, Any]]:
        """Get webhook info for task"""
        task = task_repo.get_by_id(db, task_id)
        if not task:
            return None

        return {
            "task_id": task.id,
            "task_name": task.name,
            "webhook_enabled": task.webhook_enabled,
            "webhook_token": task.webhook_token,
            "webhook_url": f"/webhook/{task.webhook_token}" if task.webhook_token else None
        }

    def find_by_webhook_token(self, db: Session, token: str) -> Optional[Task]:
        """Find task by webhook token"""
        return task_repo.get_by_webhook_token(db, token)


# Singleton instance
task_service = TaskService()
