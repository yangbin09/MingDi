#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Utility Module
Provides context managers and helpers for database operations.
"""
from contextlib import contextmanager
from typing import Generator, Dict, List, Optional
from sqlalchemy.orm import Session

from models import SessionLocal, Task, EnvVar, AlertConfig


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Automatically handles close() in finally block.

    Usage:
        with get_db_session() as db:
            tasks = db.query(Task).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_env_dict(db: Session, include_defaults: bool = True) -> Dict[str, str]:
    """
    Build environment variables dictionary from database.

    Args:
        db: Database session
        include_defaults: Whether to include default values like PYTHONUNBUFFERED

    Returns:
        Dictionary of environment variables
    """
    env_vars = db.query(EnvVar).all()
    env_dict = {ev.key: ev.value for ev in env_vars}
    if include_defaults:
        env_dict['PYTHONUNBUFFERED'] = '1'
    return env_dict


def get_active_alerts(db: Session) -> List[AlertConfig]:
    """Get all active alert configurations."""
    return db.query(AlertConfig).filter(AlertConfig.is_active).all()


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """Get a task by ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_ids(db: Session, task_ids: List[int]) -> Dict[int, Task]:
    """
    Bulk fetch tasks by IDs.
    Returns a dictionary mapping ID to Task for O(1) lookup.

    Args:
        db: Database session
        task_ids: List of task IDs to fetch

    Returns:
        Dictionary {task_id: Task}
    """
    if not task_ids:
        return {}
    tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
    return {t.id: t for t in tasks}


def get_dependent_tasks(db: Session, task_id: int) -> List[Task]:
    """Get all tasks that depend on the given task."""
    return db.query(Task).filter(Task.depends_on == task_id).all()
