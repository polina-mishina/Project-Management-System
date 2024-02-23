import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    """
    Базовая модель задачи
    """
    name: str
    description: Optional[str] = None
    executor_id: Optional[uuid.UUID] = None
    completion_date: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True


class Task(TaskBase):
    """
    Модель используемая при запросе информации о задаче
    """
    id: int
    project_id: int
    parent_task_id: Optional[int] = None
    create_date: datetime
    update_date: Optional[datetime] = None
    creator_id: uuid.UUID


class TaskCreate(TaskBase):
    """
    Модель для добавления задачи
    """
    project_id: int
    parent_task_id: Optional[int] = None
    creator_id: uuid.UUID


class TaskUpdate(TaskBase):
    """
    Модель для обновления задачи
    """
    user_id: uuid.UUID


class TaskPartialUpdate(BaseModel):
    """
    Модель для частичного обновления задачи
    """
    name: Optional[str] = None
    description: Optional[str] = None
    user_id: uuid.UUID
    executor_id: Optional[uuid.UUID] = None
    completion_date: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True
