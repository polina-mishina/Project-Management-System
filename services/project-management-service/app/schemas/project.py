import json
import uuid
from datetime import datetime
from pydantic import BaseModel, model_validator
from typing import Optional


class ProjectBase(BaseModel):
    """
    Базовая модель проекта
    """
    name: Optional[str] = None
    description: Optional[str] = None
    completion_date: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True


class Project(ProjectBase):
    """
    Модель используемая при запросе информации о проекте
    """
    id: int
    creator_id: uuid.UUID
    create_date: datetime
    update_date: Optional[datetime] = None
    name: str


class ProjectCreate(ProjectBase):
    """
    Модель для добавления проекта
    """
    creator_id: uuid.UUID
    name: str

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class ProjectUpdate(ProjectBase):
    """
    Модель для обновления проекта
    """
    user_id: uuid.UUID
    name: str


class ProjectPartialUpdate(ProjectBase):
    """
    Модель для частичного обновления проекта
    """
    user_id: uuid.UUID
