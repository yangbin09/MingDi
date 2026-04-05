#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Pattern for PyCron-Master
Encapsulates database query logic for each entity.
"""
from typing import List, Optional, Dict, Any, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import Base

T = TypeVar('T', bound=Base)


class BaseRepository:
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session) -> List[T]:
        return db.query(self.model).all()

    def get_active(self, db: Session) -> List[T]:
        if hasattr(self.model, 'is_active'):
            return db.query(self.model).filter(self.model.is_active == True).all()
        return self.get_all(db)

    def delete(self, db: Session, id: int) -> bool:
        obj = self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def update(self, db: Session, id: int, **kwargs) -> Optional[T]:
        obj = self.get_by_id(db, id)
        if not obj:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj


class TaskRepository(BaseRepository):
    """Repository for Task entity"""

    def __init__(self):
        from models import Task
        super().__init__(Task)

    def get_by_ids(self, db: Session, ids: List[int]) -> Dict[int, T]:
        """Bulk fetch tasks by IDs, returns dict for O(1) lookup"""
        if not ids:
            return {}
        tasks = db.query(self.model).filter(self.model.id.in_(ids)).all()
        return {t.id: t for t in tasks}

    def get_dependents(self, db: Session, task_id: int) -> List[T]:
        """Get tasks that depend on the given task"""
        from models import Task
        return db.query(Task).filter(Task.depends_on == task_id).all()

    def get_running(self, db: Session) -> List[T]:
        from models import Task
        from constants import TaskStatus
        return db.query(Task).filter(Task.status == TaskStatus.RUNNING.value).all()


class LogRepository(BaseRepository):
    """Repository for Log entity"""

    def __init__(self):
        from models import Log
        super().__init__(Log)

    def get_by_task(
        self,
        db: Session,
        task_id: int,
        limit: int = 100,
        exit_code: Optional[int] = None
    ) -> List[T]:
        """Get logs for a specific task"""
        query = db.query(self.model).filter(self.model.task_id == task_id)
        if exit_code is not None:
            query = query.filter(self.model.exit_code == exit_code)
        return query.order_by(self.model.start_time.desc()).limit(limit).all()

    def get_recent_by_task(
        self,
        db: Session,
        task_id: int,
        hours: int = 24,
        limit: int = 100
    ) -> List[T]:
        """Get recent logs for a task within specified hours"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        return db.query(self.model).filter(
            and_(
                self.model.task_id == task_id,
                self.model.start_time >= cutoff
            )
        ).order_by(self.model.start_time.desc()).limit(limit).all()


class AlertRepository(BaseRepository):
    """Repository for AlertConfig entity"""

    def __init__(self):
        from models import AlertConfig
        super().__init__(AlertConfig)

    def get_active(self, db: Session) -> List[T]:
        from models import AlertConfig
        return db.query(AlertConfig).filter(AlertConfig.is_active == True).all()


# Singleton instances
task_repo = TaskRepository()
log_repo = LogRepository()
alert_repo = AlertRepository()
