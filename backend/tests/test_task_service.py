#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for TaskService.
Tests business logic in isolation using mocked dependencies.
"""
from sqlalchemy.orm import Session

from models import Task
from schemas import TaskCreate, TaskUpdate
from services.task_service import task_service


class TestTaskService:
    """Test suite for TaskService"""

    def test_list_tasks_empty(self, db: Session) -> None:
        """Test listing tasks when database is empty"""
        tasks = task_service.list_tasks(db)
        assert tasks == []

    def test_list_tasks_with_data(self, db: Session, sample_task: Task) -> None:
        """Test listing tasks returns all tasks"""
        tasks = task_service.list_tasks(db)
        assert len(tasks) == 1
        assert tasks[0].name == "Test Task"

    def test_get_task_found(self, db: Session, sample_task: Task) -> None:
        """Test getting an existing task by ID"""
        task = task_service.get_task(db, sample_task.id)
        assert task is not None
        assert task.name == "Test Task"

    def test_get_task_not_found(self, db: Session) -> None:
        """Test getting a non-existent task returns None"""
        task = task_service.get_task(db, 9999)
        assert task is None

    def test_create_task_basic(self, db: Session) -> None:
        """Test creating a basic task"""
        task_data = TaskCreate(
            name="New Task",
            script_path="./new_script.py",
            is_active=True,
        )
        task = task_service.create_task(db, task_data)

        assert task.id is not None
        assert task.name == "New Task"
        assert task.script_path == "./new_script.py"
        assert task.is_active is True

    def test_create_task_with_webhook(self, db: Session) -> None:
        """Test creating a task with webhook enabled generates token"""
        task_data = TaskCreate(
            name="Webhook Task",
            script_path="./webhook_script.py",
            webhook_enabled=True,
        )
        task = task_service.create_task(db, task_data)

        assert task.webhook_enabled is True
        assert task.webhook_token is not None
        assert len(task.webhook_token) > 0

    def test_create_task_without_webhook_no_token(self, db: Session) -> None:
        """Test creating a task without webhook does not generate token"""
        task_data = TaskCreate(
            name="Normal Task",
            script_path="./normal_script.py",
            webhook_enabled=False,
        )
        task = task_service.create_task(db, task_data)

        assert task.webhook_enabled is False
        assert task.webhook_token is None

    def test_update_task_name(self, db: Session, sample_task: Task) -> None:
        """Test updating task name"""
        update_data = TaskUpdate(name="Updated Task Name")
        updated = task_service.update_task(db, sample_task.id, update_data)

        assert updated is not None
        assert updated.name == "Updated Task Name"

    def test_update_task_not_found(self, db: Session) -> None:
        """Test updating non-existent task returns None"""
        update_data = TaskUpdate(name="Should Not Work")
        result = task_service.update_task(db, 9999, update_data)
        assert result is None

    def test_delete_task_success(self, db: Session, sample_task: Task) -> None:
        """Test deleting an existing task"""
        result = task_service.delete_task(db, sample_task.id)
        assert result is True

        # Verify task is gone
        task = task_service.get_task(db, sample_task.id)
        assert task is None

    def test_delete_task_not_found(self, db: Session) -> None:
        """Test deleting non-existent task returns False"""
        result = task_service.delete_task(db, 9999)
        assert result is False

    def test_enable_webhook(self, db: Session, sample_task: Task) -> None:
        """Test enabling webhook for a task"""
        result = task_service.enable_webhook(db, sample_task.id)

        assert result is not None
        assert result["success"] is True
        assert result["webhook_url"] is not None
        assert result["webhook_token"] is not None

    def test_enable_webhook_already_enabled(self, db: Session, sample_task: Task) -> None:
        """Test enabling webhook when already enabled keeps existing token"""
        # First enable
        result1 = task_service.enable_webhook(db, sample_task.id)
        token1 = result1["webhook_token"]

        # Second enable - should keep same token
        result2 = task_service.enable_webhook(db, sample_task.id)
        token2 = result2["webhook_token"]

        assert token1 == token2

    def test_disable_webhook(self, db: Session, sample_task: Task) -> None:
        """Test disabling webhook for a task"""
        # First enable
        task_service.enable_webhook(db, sample_task.id)

        # Then disable
        result = task_service.disable_webhook(db, sample_task.id)
        assert result is True

        # Verify webhook is disabled
        task = task_service.get_task(db, sample_task.id)
        assert task.webhook_enabled is False

    def test_get_webhook_info(self, db: Session, sample_task: Task) -> None:
        """Test getting webhook info for a task"""
        info = task_service.get_webhook_info(db, sample_task.id)

        assert info is not None
        assert info["task_id"] == sample_task.id
        assert info["webhook_enabled"] is False
        assert info["webhook_token"] is None

    def test_get_webhook_info_with_webhook(self, db: Session, sample_task: Task) -> None:
        """Test getting webhook info when webhook is enabled"""
        task_service.enable_webhook(db, sample_task.id)

        info = task_service.get_webhook_info(db, sample_task.id)

        assert info["webhook_enabled"] is True
        assert info["webhook_token"] is not None
        assert "/webhook/" in info["webhook_url"]

    def test_find_by_webhook_token(self, db: Session, sample_task: Task) -> None:
        """Test finding task by webhook token"""
        # Enable webhook first
        result = task_service.enable_webhook(db, sample_task.id)
        token = result["webhook_token"]

        # Find by token
        task = task_service.find_by_webhook_token(db, token)

        assert task is not None
        assert task.id == sample_task.id

    def test_find_by_webhook_token_not_found(self, db: Session) -> None:
        """Test finding task by invalid token returns None"""
        task = task_service.find_by_webhook_token(db, "invalid_token")
        assert task is None

    def test_task_service_singleton(self) -> None:
        """Test that task_service is a singleton instance"""
        from services.task_service import TaskService
        assert isinstance(task_service, TaskService)
