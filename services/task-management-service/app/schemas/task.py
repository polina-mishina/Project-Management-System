import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    """
    Базовая модель задачи
    """
    name: Optional[str] = None
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
    creator_id: uuid.UUID
    create_date: datetime
    update_date: Optional[datetime] = None
    name: str


class TaskCreate(TaskBase):
    """
    Модель для добавления задачи
    """
    project_id: int
    parent_task_id: Optional[int] = None
    creator_id: uuid.UUID
    name: str


class TaskUpdate(TaskBase):
    """
    Модель для обновления задачи
    """
    user_id: uuid.UUID
    name: str


class TaskPartialUpdate(TaskBase):
    """
    Модель для частичного обновления задачи
    """
    user_id: uuid.UUID
