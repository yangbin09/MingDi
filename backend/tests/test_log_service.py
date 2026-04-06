#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for LogService.
Tests business logic in isolation.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import Log, Task
from services.log_service import log_service


class TestLogService:
    """Test suite for LogService"""

    def test_get_task_logs_empty(self, db: Session) -> None:
        """Test getting logs for a task with no logs"""
        logs = log_service.get_task_logs(db, 9999)
        assert logs == []

    def test_get_task_logs_with_data(self, db: Session, sample_task: Task, sample_log: Log) -> None:
        """Test getting logs for a task returns all logs"""
        logs = log_service.get_task_logs(db, sample_task.id)
        assert len(logs) == 1
        assert logs[0].output == "Test output"

    def test_get_log_found(self, db: Session, sample_log: Log) -> None:
        """Test getting an existing log by ID"""
        log = log_service.get_log(db, sample_log.id)
        assert log is not None
        assert log.output == "Test output"

    def test_get_log_not_found(self, db: Session) -> None:
        """Test getting a non-existent log returns None"""
        log = log_service.get_log(db, 9999)
        assert log is None

    def test_delete_log_success(self, db: Session, sample_log: Log) -> None:
        """Test deleting an existing log"""
        result = log_service.delete_log(db, sample_log.id)
        assert result is True

        # Verify log is gone
        log = log_service.get_log(db, sample_log.id)
        assert log is None

    def test_delete_log_not_found(self, db: Session) -> None:
        """Test deleting non-existent log returns False"""
        result = log_service.delete_log(db, 9999)
        assert result is False

    def test_batch_delete_logs(self, db: Session, sample_task: Task) -> None:
        """Test batch deleting logs"""
        # Create multiple logs
        for i in range(5):
            log = Log(
                task_id=sample_task.id,
                start_time=datetime.now(),
                output=f"Log {i}",
                exit_code=0,
            )
            db.add(log)
        db.commit()

        # Get log IDs
        logs = log_service.get_task_logs(db, sample_task.id)
        log_ids = [log.id for log in logs]

        # Delete first 3
        count = log_service.batch_delete_logs(db, log_ids[:3])
        assert count == 3

        # Verify only 2 remain
        remaining = log_service.get_task_logs(db, sample_task.id)
        assert len(remaining) == 2

    def test_search_logs_basic(self, db: Session, sample_task: Task) -> None:
        """Test basic log search"""
        # Create logs with different outputs
        for i in range(3):
            log = Log(
                task_id=sample_task.id,
                start_time=datetime.now(),
                output=f"Output {i}",
                exit_code=0,
            )
            db.add(log)
        db.commit()

        items, total = log_service.search_logs(db, keyword="Output 1")
        assert total == 1
        assert items[0]["output"] == "Output 1"

    def test_search_logs_pagination(self, db: Session, sample_task: Task) -> None:
        """Test log search with pagination"""
        # Create 10 logs
        for i in range(10):
            log = Log(
                task_id=sample_task.id,
                start_time=datetime.now(),
                output=f"Log entry {i}",
                exit_code=0,
            )
            db.add(log)
        db.commit()

        # Get page 1 with size 3
        items, total = log_service.search_logs(db, page=1, size=3)
        assert total == 10
        assert len(items) == 3

        # Get page 2
        items, total = log_service.search_logs(db, page=2, size=3)
        assert total == 10
        assert len(items) == 3

    def test_search_logs_by_exit_code(self, db: Session, sample_task: Task) -> None:
        """Test filtering logs by exit code"""
        # Create logs with different exit codes
        for exit_code in [0, 0, 1, 1, 1]:
            log = Log(
                task_id=sample_task.id,
                start_time=datetime.now(),
                output=f"Exit {exit_code}",
                exit_code=exit_code,
            )
            db.add(log)
        db.commit()

        # Filter by exit_code=0
        items, total = log_service.search_logs(db, exit_code=0)
        assert total == 2

        # Filter by exit_code=1
        items, total = log_service.search_logs(db, exit_code=1)
        assert total == 3

    def test_search_logs_non_zero(self, db: Session, sample_task: Task) -> None:
        """Test filtering non-zero exit codes"""
        for exit_code in [0, 1, 2, -1]:
            log = Log(
                task_id=sample_task.id,
                start_time=datetime.now(),
                output=f"Exit {exit_code}",
                exit_code=exit_code,
            )
            db.add(log)
        db.commit()

        items, total = log_service.search_logs(db, exit_code_non_zero=True)
        # -1 (timeout) is excluded by the query logic
        assert total == 2  # only 1 and 2

    def test_search_logs_running(self, db: Session, sample_task: Task) -> None:
        """Test filtering running (no exit code) logs"""
        # Create a running log (no end_time, no exit_code)
        running_log = Log(
            task_id=sample_task.id,
            start_time=datetime.now(),
            output="Still running...",
            exit_code=None,
            end_time=None,
        )
        # Create a completed log
        completed_log = Log(
            task_id=sample_task.id,
            start_time=datetime.now(),
            end_time=datetime.now(),
            output="Completed",
            exit_code=0,
        )
        db.add(running_log)
        db.add(completed_log)
        db.commit()

        items, total = log_service.search_logs(db, is_running=True)
        assert total == 1
        assert items[0]["exit_code"] is None

    def test_search_logs_by_date_range(self, db: Session, sample_task: Task) -> None:
        """Test filtering logs by date range"""
        now = datetime.now()

        # Create old log
        old_log = Log(
            task_id=sample_task.id,
            start_time=now - timedelta(days=7),
            end_time=now - timedelta(days=7),
            output="Old log",
            exit_code=0,
        )
        # Create recent log
        recent_log = Log(
            task_id=sample_task.id,
            start_time=now,
            end_time=now,
            output="Recent log",
            exit_code=0,
        )
        db.add(old_log)
        db.add(recent_log)
        db.commit()

        # Query for last 24 hours
        today = now.strftime("%Y-%m-%d")
        items, total = log_service.search_logs(db, start_date=today)
        assert total == 1
        assert items[0]["output"] == "Recent log"

    def test_get_timeline_empty(self, db: Session) -> None:
        """Test timeline with no logs returns empty list"""
        timeline = log_service.get_timeline(db)
        assert timeline == []

    def test_get_timeline_with_logs(self, db: Session, sample_task: Task, sample_log: Log) -> None:
        """Test timeline returns formatted log data"""
        timeline = log_service.get_timeline(db)

        assert len(timeline) == 1
        assert timeline[0]["task_id"] == sample_task.id
        assert timeline[0]["task_name"] == "Test Task"
        assert timeline[0]["exit_code"] == 0

    def test_format_log_for_download(self, db: Session, sample_log: Log) -> None:
        """Test log download formatting"""
        content = log_service.format_log_for_download(db, sample_log.id)

        assert content is not None
        assert "鸣镝 Log" in content
        assert "Test output" in content
        assert "Exit Code: 0" in content

    def test_format_log_for_download_not_found(self, db: Session) -> None:
        """Test log download for non-existent log returns None"""
        content = log_service.format_log_for_download(db, 9999)
        assert content is None

    def test_log_service_singleton(self) -> None:
        """Test that log_service is a singleton instance"""
        from services.log_service import LogService
        assert isinstance(log_service, LogService)
