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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # Phase 3 fields
    interpreter_path = Column(String(512), nullable=True)
    depends_on = Column(Integer, nullable=True)
    timeout = Column(Integer, default=300)
    # Phase 8 AI & Webhook fields
    webhook_enabled = Column(Boolean, default=False)
    webhook_token = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)  # AI-generated doc
    use_docker = Column(Boolean, default=False)  # Run in Docker sandbox
    docker_image = Column(String(255), nullable=True)  # Custom Docker image

    logs = relationship("Log", back_populates="task", cascade="all, delete-orphan")


class NodeFlow(Base):
    """Visual DAG flow for node-based task orchestration"""
    __tablename__ = "node_flows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    nodes = Column(Text, default="[]")  # JSON: list of {id, task_id, x, y, type}
    edges = Column(Text, default="[]")  # JSON: list of {id, source, target}
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class EnvVar(Base):
    __tablename__ = "env_vars"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=False)
    description = Column(String(512), nullable=True)
    is_secret = Column(Boolean, default=False)  # Hide value in UI
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    webhook_url = Column(String(1024), nullable=False)
    events = Column(String(255), default="failed,timeout")  # Comma-separated events
    is_active = Column(Boolean, default=True)
    ai_humanize = Column(Boolean, default=False)  # Phase 8: AI humanized alerts
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


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
