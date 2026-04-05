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


class TaskResponse(TaskBase):
    id: int
    status: str
    last_run_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

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


class AlertConfigCreate(AlertConfigBase):
    pass


class AlertConfigUpdate(BaseModel):
    name: Optional[str] = None
    webhook_url: Optional[str] = None
    events: Optional[str] = None
    is_active: Optional[bool] = None


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
