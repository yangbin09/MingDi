from pydantic import BaseModel, ConfigDict
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
    # Log retention settings
    log_retention_count: int = 100


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
    # Log retention settings
    log_retention_count: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    status: str
    last_run_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    webhook_token: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LogBase(BaseModel):
    task_id: int


class LogResponse(LogBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    output: str
    exit_code: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedLogResponse(BaseModel):
    total: int
    items: List[LogResponse]


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


# ============ System Settings Schemas ============

class SystemSettingsItem(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None


class SystemSettingsResponse(BaseModel):
    minimax_api_key: Optional[str] = None
    minimax_group_id: Optional[str] = None
    ai_enabled: bool = False


class SystemSettingsUpdate(BaseModel):
    minimax_api_key: Optional[str] = None
    minimax_group_id: Optional[str] = None


# ============ AI Hub Schemas ============

class AIProviderBase(BaseModel):
    name: str
    display_name: str
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: bool = True
    is_primary: bool = False
    priority: int = 100
    rate_limit_rpm: Optional[int] = None
    rate_limit_tpm: Optional[int] = None


class AIProviderCreate(AIProviderBase):
    pass


class AIProviderUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: Optional[bool] = None
    is_primary: Optional[bool] = None
    priority: Optional[int] = None
    rate_limit_rpm: Optional[int] = None
    rate_limit_tpm: Optional[int] = None


class AIProviderResponse(AIProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIModelBase(BaseModel):
    model_config = {'protected_namespaces': ()}

    provider_id: int
    model_id: str
    display_name: str
    model_type: str = "chat"
    context_window: Optional[int] = None
    is_enabled: bool = True
    cost_per_input_token: float = 0
    cost_per_output_token: float = 0


class AIModelCreate(AIModelBase):
    pass


class AIModelUpdate(BaseModel):
    provider_id: Optional[int] = None
    model_id: Optional[str] = None
    display_name: Optional[str] = None
    model_type: Optional[str] = None
    context_window: Optional[int] = None
    is_enabled: Optional[bool] = None
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None


class AIModelResponse(AIModelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIFeatureRoutingBase(BaseModel):
    feature: str
    display_name: str
    primary_model_id: Optional[int] = None
    fallback_model_ids: str = "[]"
    is_enabled: bool = True


class AIFeatureRoutingCreate(AIFeatureRoutingBase):
    pass


class AIFeatureRoutingUpdate(BaseModel):
    feature: Optional[str] = None
    display_name: Optional[str] = None
    primary_model_id: Optional[int] = None
    fallback_model_ids: Optional[str] = None
    is_enabled: Optional[bool] = None


class AIFeatureRoutingResponse(AIFeatureRoutingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIPromptTemplateBase(BaseModel):
    feature: str
    display_name: str
    system_prompt: Optional[str] = None
    user_template: Optional[str] = None
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    context_lines: int = 100
    is_enabled: bool = True


class AIPromptTemplateCreate(AIPromptTemplateBase):
    pass


class AIPromptTemplateUpdate(BaseModel):
    feature: Optional[str] = None
    display_name: Optional[str] = None
    system_prompt: Optional[str] = None
    user_template: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    context_lines: Optional[int] = None
    is_enabled: Optional[bool] = None


class AIPromptTemplateResponse(AIPromptTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIRAGContextBase(BaseModel):
    context_type: str
    context_key: str
    content: str
    is_enabled: bool = True
    injection_position: str = "system"


class AIRAGContextCreate(AIRAGContextBase):
    pass


class AIRAGContextUpdate(BaseModel):
    context_type: Optional[str] = None
    context_key: Optional[str] = None
    content: Optional[str] = None
    is_enabled: Optional[bool] = None
    injection_position: Optional[str] = None


class AIRAGContextResponse(AIRAGContextBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIPermissionLevelBase(BaseModel):
    permission_level: int = 1
    permission_name: str
    description: Optional[str] = None
    requires_confirm: bool = True
    is_enabled: bool = True


class AIPermissionLevelCreate(AIPermissionLevelBase):
    pass


class AIPermissionLevelUpdate(BaseModel):
    permission_level: Optional[int] = None
    permission_name: Optional[str] = None
    description: Optional[str] = None
    requires_confirm: Optional[bool] = None
    is_enabled: Optional[bool] = None


class AIPermissionLevelResponse(AIPermissionLevelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIUsageStatsResponse(BaseModel):
    total_requests: int = 0
    total_cost: float = 0
    input_tokens: int = 0
    output_tokens: int = 0


class AIAuditLogResponse(BaseModel):
    id: int
    feature: str
    model_id: Optional[int] = None
    provider_id: Optional[int] = None
    prompt: str
    system_prompt: Optional[str] = None
    response: Optional[str] = None
    error_message: Optional[str] = None
    status: str
    latency_ms: Optional[int] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0
    cache_hit: bool = False
    fallback_used: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
