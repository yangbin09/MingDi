#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Repository - Database operations for Log entity.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from models import Log
from .base import BaseRepository


class LogRepository(BaseRepository):
    """Repository for Log entity"""

    def __init__(self) -> None:
        super().__init__(Log)

    def get_by_task(
        self,
        db: Session,
        task_id: int,
        limit: int = 100,
        exit_code: Optional[int] = None
    ) -> List[Log]:
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
    ) -> List[Log]:
        """Get recent logs for a task within specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return db.query(self.model).filter(
            and_(
                self.model.task_id == task_id,
                self.model.start_time >= cutoff
            )
        ).order_by(self.model.start_time.desc()).limit(limit).all()

    def get_recent_logs(
        self,
        db: Session,
        hours: int = 24,
        limit: int = 100
    ) -> List[Log]:
        """Get recent logs across all tasks"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return db.query(self.model).filter(
            self.model.start_time >= cutoff
        ).order_by(self.model.start_time.desc()).limit(limit).all()

    def search_logs(
        self,
        db: Session,
        keyword: Optional[str] = None,
        task_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        exit_code: Optional[int] = None,
        exit_code_non_zero: bool = False,
        is_running: bool = False,
        page: int = 1,
        size: int = 20
    ) -> tuple[List[Log], int]:
        """
        Search logs with filters and pagination.
        Returns (logs, total_count) tuple.
        """
        query = db.query(self.model)

        if task_id is not None:
            query = query.filter(self.model.task_id == task_id)
        if exit_code is not None:
            query = query.filter(self.model.exit_code == exit_code)
        if exit_code_non_zero:
            query = query.filter(
                self.model.exit_code.isnot(None),
                self.model.exit_code != 0,
                self.model.exit_code != -1
            )
        if is_running:
            query = query.filter(
                self.model.exit_code.is_(None),
                self.model.end_time.is_(None)
            )
        if start_date:
            query = query.filter(self.model.start_time >= start_date)
        if end_date:
            query = query.filter(self.model.start_time <= end_date)
        if keyword:
            keyword_lower = keyword.lower()
            query = query.filter(
                func.lower(self.model.output).like(f"%{keyword_lower}%", escape="/")
            )

        total = query.count()
        logs = query.order_by(self.model.start_time.desc()).offset((page - 1) * size).limit(size).all()

        return logs, total

    def get_logs_by_task_since(
        self,
        db: Session,
        task_id: int,
        since_id: int,
        limit: int = 10
    ) -> List[Log]:
        """Get new logs for SSE streaming (logs with ID > since_id)"""
        return db.query(self.model).filter(
            self.model.task_id == task_id,
            self.model.id > since_id
        ).order_by(self.model.start_time.desc()).limit(limit).all()


# Singleton instance
log_repo = LogRepository()
