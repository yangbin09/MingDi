#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for 鸣镝 backend tests.
Uses in-memory SQLite to ensure test isolation.
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from models import Base, get_db, Task, Log, EnvVar, AlertConfig
from main import app


# ============ Test Database Setup ============

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override FastAPI dependency to use test database"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task(db: Session) -> Task:
    """Create a sample task for testing"""
    task = Task(
        name="Test Task",
        script_path="./test_script.py",
        cron_expr="* * * * *",
        is_active=True,
        timeout=300,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def sample_log(db: Session, sample_task: Task) -> Log:
    """Create a sample log for testing"""
    from datetime import datetime
    log = Log(
        task_id=sample_task.id,
        start_time=datetime.now(),
        end_time=datetime.now(),
        output="Test output",
        exit_code=0,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@pytest.fixture
def sample_env_var(db: Session) -> EnvVar:
    """Create a sample environment variable for testing"""
    env_var = EnvVar(
        key="TEST_VAR",
        value="test_value",
        description="Test variable",
        is_secret=False,
    )
    db.add(env_var)
    db.commit()
    db.refresh(env_var)
    return env_var


@pytest.fixture
def sample_alert(db: Session) -> AlertConfig:
    """Create a sample alert config for testing"""
    alert = AlertConfig(
        name="Test Alert",
        webhook_url="http://test.com/webhook",
        events="failed,timeout",
        is_active=True,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
