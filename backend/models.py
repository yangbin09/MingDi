from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
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
    # Log retention settings
    log_retention_count = Column(Integer, default=100)  # 0 = unlimited

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


class SystemSettings(Base):
    """System configuration stored in database"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=True)
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ============ AI Hub Models ============

class AIProvider(Base):
    """AI Provider configuration (OpenAI, DeepSeek, Claude, Ollama, Minimax)"""
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # openai, deepseek, claude, ollama, minimax
    display_name = Column(String(255), nullable=False)
    api_base_url = Column(String(512), nullable=True)  # Custom endpoint for Ollama
    api_key = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary provider for fallback
    priority = Column(Integer, default=100)  # Lower = higher priority
    rate_limit_rpm = Column(Integer, nullable=True)  # Requests per minute
    rate_limit_tpm = Column(Integer, nullable=True)  # Tokens per minute
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIModel(Base):
    """AI Model instances per provider"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    model_id = Column(String(100), nullable=False)  # gpt-4o, gpt-4o-mini, deepseek-chat, claude-3-5-sonnet, llama3, etc.
    display_name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # chat, completion
    context_window = Column(Integer, nullable=True)  # Max tokens
    is_enabled = Column(Boolean, default=True)
    cost_per_input_token = Column(Float, default=0)  # USD
    cost_per_output_token = Column(Float, default=0)  # USD
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    provider = relationship("AIProvider", backref="models")


class AIFeatureRouting(Base):
    """Feature-level routing configuration"""
    __tablename__ = "ai_feature_routing"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(100), nullable=False, unique=True)  # generate_script, diagnose_error, code_review, etc.
    display_name = Column(String(255), nullable=False)
    primary_model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)
    fallback_model_ids = Column(Text, default="[]")  # JSON array of model IDs
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIPromptTemplate(Base):
    """Custom prompt templates per feature"""
    __tablename__ = "ai_prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    system_prompt = Column(Text, nullable=True)  # Custom system prompt
    user_template = Column(Text, nullable=True)  # User message template with {{variables}}
    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=0.9)
    max_tokens = Column(Integer, default=2048)
    context_lines = Column(Integer, default=100)  # Lines of context for error diagnosis
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AISemanticCache(Base):
    """Semantic caching for AI responses"""
    __tablename__ = "ai_semantic_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(64), nullable=False, index=True)  # Hash of prompt
    feature = Column(String(100), nullable=False)
    prompt_hash = Column(String(64), nullable=False)
    response = Column(Text, nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)
    hit_count = Column(Integer, default=0)
    first_hit_at = Column(DateTime, default=datetime.now)
    last_hit_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)


class AIRAGContext(Base):
    """Local RAG context for environment knowledge injection"""
    __tablename__ = "ai_rag_context"

    id = Column(Integer, primary_key=True, index=True)
    context_type = Column(String(50), nullable=False)  # python_version, dependencies, api_docs, custom
    context_key = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_enabled = Column(Boolean, default=True)
    injection_position = Column(String(20), default="system")  # system, user, both
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIPermissionLevel(Base):
    """AI action permission levels"""
    __tablename__ = "ai_permissions"

    id = Column(Integer, primary_key=True, index=True)
    permission_level = Column(Integer, default=1)  # 1=Dry-run only, 2=Allow script replace, 3=Full autonomy
    permission_name = Column(String(100), nullable=False)  # dry_run, script_replace, config_modify
    description = Column(Text, nullable=True)
    requires_confirm = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIUsageStats(Base):
    """Token usage statistics"""
    __tablename__ = "ai_usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(100), nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0)
    request_count = Column(Integer, default=0)
    cache_hit_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    model = relationship("AIModel", backref="usage_stats")
    provider = relationship("AIProvider", backref="usage_stats")


class AIAuditLog(Base):
    """Full AI interaction audit log"""
    __tablename__ = "ai_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(100), nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)  # success, error, fallback, cached
    latency_ms = Column(Integer, nullable=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0)
    cache_hit = Column(Boolean, default=False)
    fallback_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


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
