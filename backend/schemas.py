from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    name: str
    script_path: str
    cron_expr: Optional[str] = None
    is_active: bool = True


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    script_path: Optional[str] = None
    cron_expr: Optional[str] = None
    is_active: Optional[bool] = None


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
