#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Repository - Database operations for Task entity.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from models import Task
from constants import TaskStatus
from .base import BaseRepository


class TaskRepository(BaseRepository):
    """Repository for Task entity"""

    def __init__(self) -> None:
        super().__init__(Task)

    def get_by_ids(self, db: Session, ids: List[int]) -> Dict[int, Task]:
        """Bulk fetch tasks by IDs, returns dict for O(1) lookup"""
        if not ids:
            return {}
        tasks = db.query(self.model).filter(self.model.id.in_(ids)).all()
        return {t.id: t for t in tasks}

    def get_dependents(self, db: Session, task_id: int) -> List[Task]:
        """Get tasks that depend on the given task"""
        return db.query(Task).filter(Task.depends_on == task_id).all()

    def get_running(self, db: Session) -> List[Task]:
        """Get all running tasks"""
        return db.query(Task).filter(Task.status == TaskStatus.RUNNING.value).all()

    def get_active(self, db: Session) -> List[Task]:
        """Get all active (enabled) tasks"""
        return db.query(Task).filter(Task.is_active == True)  # noqa: E712.all()

    def get_by_webhook_token(self, db: Session, token: str) -> Optional[Task]:
        """Find task by webhook token"""
        return db.query(Task).filter(Task.webhook_token == token).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Task]:
        """Find task by name"""
        return db.query(Task).filter(Task.name == name).first()


# Singleton instance
task_repo = TaskRepository()
