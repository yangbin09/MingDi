from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./pycron.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    script_path = Column(String(512), nullable=False)
    cron_expr = Column(String(100), nullable=True)
    status = Column(String(50), default="idle")  # idle, running, success, failed, timeout
    last_run_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # New fields for Phase 3
    interpreter_path = Column(String(512), nullable=True)  # Python interpreter/venv path
    depends_on = Column(Integer, nullable=True)  # Task ID this task depends on (DAG)
    timeout = Column(Integer, default=300)  # Timeout in seconds

    logs = relationship("Log", back_populates="task", cascade="all, delete-orphan")


class EnvVar(Base):
    __tablename__ = "env_vars"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(String(512), nullable=True)
    is_secret = Column(Boolean, default=False)  # Hide value in UI
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    webhook_url = Column(String(1024), nullable=False)
    events = Column(String(255), default="failed,timeout")  # Comma-separated events
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    output = Column(Text, default="")
    exit_code = Column(Integer, nullable=True)

    task = relationship("Task", back_populates="logs")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
