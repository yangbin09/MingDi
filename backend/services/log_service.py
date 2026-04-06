#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Service - Business logic for Log operations.
Handles log retrieval, search, and streaming.
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, time as dt_time
from sqlalchemy.orm import Session

from models import Log
from schemas import LogResponse
from repositories import log_repo, task_repo
from constants import TIMELINE_HOURS


class LogService:
    """Service layer for Log business logic"""

    def get_task_logs(
        self,
        db: Session,
        task_id: int,
        limit: int = 100
    ) -> List[Log]:
        """Get logs for a specific task"""
        task = task_repo.get_by_id(db, task_id)
        if not task:
            return []
        return log_repo.get_by_task(db, task_id, limit=limit)

    def get_log(self, db: Session, log_id: int) -> Optional[Log]:
        """Get a single log entry"""
        return log_repo.get_by_id(db, log_id)

    def delete_log(self, db: Session, log_id: int) -> bool:
        """Delete a single log entry"""
        return log_repo.delete(db, log_id)

    def batch_delete_logs(self, db: Session, log_ids: List[int]) -> int:
        """Batch delete log entries"""
        deleted_count = 0
        for log_id in log_ids:
            if log_repo.delete(db, log_id):
                deleted_count += 1
        return deleted_count

    def search_logs(
        self,
        db: Session,
        keyword: Optional[str] = None,
        task_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        exit_code: Optional[int] = None,
        exit_code_non_zero: bool = False,
        is_running: bool = False,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search logs with filters and pagination.
        Returns (items, total) tuple with serialized data.
        """
        # Parse datetime parameters
        start_dt = None
        end_dt = None

        if start_date:
            start_dt = self._parse_datetime(start_date, is_end=False)
        if end_date:
            end_dt = self._parse_datetime(end_date, is_end=True)

        logs, total = log_repo.search_logs(
            db,
            keyword=keyword,
            task_id=task_id,
            start_date=start_dt,
            end_date=end_dt,
            exit_code=exit_code,
            exit_code_non_zero=exit_code_non_zero,
            is_running=is_running,
            page=page,
            size=size
        )

        items = [
            LogResponse.model_validate(log).model_dump(mode='json')
            for log in logs
        ]

        return items, total

    def _parse_datetime(self, value: str, *, is_end: bool) -> datetime:
        """Parse datetime string to datetime object"""
        v = value.strip()
        try:
            if len(v) == 10:
                d = date.fromisoformat(v)
                return datetime.combine(d, dt_time.max if is_end else dt_time.min)
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid datetime format: {value}")

    def get_logs_for_streaming(
        self,
        db: Session,
        task_id: int,
        since_id: int = 0,
        limit: int = 10
    ) -> List[Log]:
        """Get new logs for SSE streaming"""
        return log_repo.get_logs_by_task_since(db, task_id, since_id, limit=limit)

    def get_timeline(self, db: Session, hours: int = TIMELINE_HOURS) -> List[Dict[str, Any]]:
        """Get task execution timeline for last N hours"""
        logs = log_repo.get_recent_logs(db, hours=hours)

        if not logs:
            return []

        # Bulk fetch tasks to avoid N+1
        task_ids = list(set(log.task_id for log in logs))
        tasks = task_repo.get_by_ids(db, task_ids) if task_ids else {}

        timeline = []
        for log in logs:
            duration = None
            if log.end_time and log.start_time:
                duration = (log.end_time - log.start_time).total_seconds()

            task = tasks.get(log.task_id)

            timeline.append({
                "id": log.id,
                "task_id": log.task_id,
                "task_name": task.name if task else "Unknown",
                "start_time": log.start_time.isoformat() if log.start_time else None,
                "end_time": log.end_time.isoformat() if log.end_time else None,
                "duration": duration,
                "exit_code": log.exit_code,
                "status": "success" if log.exit_code == 0 else "failed"
            })

        return timeline

    def format_log_for_download(self, db: Session, log_id: int) -> Optional[str]:
        """Format log entry for download as .log file"""
        log = self.get_log(db, log_id)
        if not log:
            return None

        content = f"=== 鸣镝 Log #{log.id} ===\n"
        content += f"Task ID: {log.task_id}\n"
        content += f"Start Time: {log.start_time}\n"
        content += f"End Time: {log.end_time}\n"
        content += f"Exit Code: {log.exit_code}\n"
        content += f"\n=== Output ===\n{log.output or '// No output'}\n"

        return content


# Singleton instance
log_service = LogService()
