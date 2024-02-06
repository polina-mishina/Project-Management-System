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
    executor_id: uuid.UUID

    class ConfigDict:
        from_attributes = True


class Task(TaskBase):
    """
    Модель используемая при запросе информации о задаче
    """
    id: int
    project_id: int
    creator_id: uuid.UUID
    add_date: Optional[datetime] = None
    update_date: Optional[datetime] = None


class Subtask(Task):
    """
    Модель используемая при запросе информации о подзадаче
    """
    parent_task_id: int


class TaskIn(TaskBase):
    """
    Модель для добавления/обновления задачи, т.к при добавлении/обновлении
    id не передается или передается через url, а не через тело запроса
    """
    pass
