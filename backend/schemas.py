from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    name: str
    script_path: str
    cron_expr: Optional[str] = None
    is_active: bool = True
    interpreter_path: Optional[str] = None
    depends_on: Optional[int] = None
    timeout: Optional[int] = 300
    # Phase 8
    webhook_enabled: bool = False
    description: Optional[str] = None
    use_docker: bool = False
    docker_image: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    script_path: Optional[str] = None
    cron_expr: Optional[str] = None
    is_active: Optional[bool] = None
    interpreter_path: Optional[str] = None
    depends_on: Optional[int] = None
    timeout: Optional[int] = None
    # Phase 8
    webhook_enabled: Optional[bool] = None
    description: Optional[str] = None
    use_docker: Optional[bool] = None
    docker_image: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    status: str
    last_run_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    webhook_token: Optional[str] = None

    class Config:
        from_attributes = True


class LogBase(BaseModel):
    task_id: int


class LogResponse(LogBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    output: str
    exit_code: Optional[int] = None

    class Config:
        from_attributes = True


class EnvVarBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    is_secret: bool = False


class EnvVarCreate(EnvVarBase):
    pass


class EnvVarUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    is_secret: Optional[bool] = None


class EnvVarResponse(EnvVarBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertConfigBase(BaseModel):
    name: str
    webhook_url: str
    events: str = "failed,timeout"
    is_active: bool = True
    ai_humanize: bool = False


class AlertConfigCreate(AlertConfigBase):
    pass


class AlertConfigUpdate(BaseModel):
    name: Optional[str] = None
    webhook_url: Optional[str] = None
    events: Optional[str] = None
    is_active: Optional[bool] = None
    ai_humanize: Optional[bool] = None


class AlertConfigResponse(AlertConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_used_gb: float
    disk_total_gb: float


class ScratchpadRequest(BaseModel):
    code: str
    interpreter_path: Optional[str] = None


class ScratchpadResponse(BaseModel):
    output: str
    exit_code: int
    execution_time: float


class ExportData(BaseModel):
    tasks: List[TaskResponse]
    env_vars: List[EnvVarResponse]
    alert_configs: List[AlertConfigResponse]
    version: str = "1.0.0"


# ============ AI Feature Schemas ============

class AIScriptRequest(BaseModel):
    description: str


class AIScriptResponse(BaseModel):
    code: str
    used_ai: bool = True


class AIDiagnoseRequest(BaseModel):
    error_traceback: str
    script_content: Optional[str] = ""


class AIDiagnoseResponse(BaseModel):
    diagnosis: str
    used_ai: bool = True


class AICodeReviewRequest(BaseModel):
    code: str


class AICodeReviewResponse(BaseModel):
    review: str
    used_ai: bool = True


class AINLPCronRequest(BaseModel):
    natural_language: str


class AINLPCronResponse(BaseModel):
    cron_expr: str
    description: str
    used_ai: bool = True


class AISummarizeLogRequest(BaseModel):
    log_content: str


class AISummarizeLogResponse(BaseModel):
    summary: str
    used_ai: bool = True


class AIGenerateDocRequest(BaseModel):
    code: str


class AIGenerateDocResponse(BaseModel):
    doc: str
    used_ai: bool = True


class AIHumanizeAlertRequest(BaseModel):
    alert_type: str
    task_name: str
    error_info: str


class AIHumanizeAlertResponse(BaseModel):
    message: str
    used_ai: bool = True


# ============ Webhook & Node Flow Schemas ============

class WebhookTriggerRequest(BaseModel):
    payload: Optional[dict] = None


class WebhookTriggerResponse(BaseModel):
    success: bool
    message: str
    task_id: int
    execution_id: Optional[int] = None


class NodeFlowBase(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: str = "[]"
    edges: str = "[]"
    is_active: bool = True


class NodeFlowCreate(NodeFlowBase):
    pass


class NodeFlowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[str] = None
    edges: Optional[str] = None
    is_active: Optional[bool] = None


class NodeFlowResponse(NodeFlowBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DockerRunRequest(BaseModel):
    code: str
    requirements: List[str] = []
    timeout: int = 60
    docker_image: str = "python:3.11-slim"


class DockerRunResponse(BaseModel):
    success: bool
    output: str
    exit_code: int
    execution_time: float
    error: Optional[str] = None
