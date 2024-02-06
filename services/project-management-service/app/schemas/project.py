import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ProjectBase(BaseModel):
    """
    Базовая модель проекта
    """
    name: str
    description: Optional[str] = None

    class ConfigDict:
        from_attributes = True


class Project(ProjectBase):
    """
    Модель используемая при запросе информации о проекте
    """
    id: int
    creator_id: uuid.UUID
    add_date: Optional[datetime] = None
    update_date: Optional[datetime] = None


class ProjectIn(ProjectBase):
    """
    Модель для добавления/обновления проекта, т.к при добавлении/обновлении
    id не передается или передается через url, а не через тело запроса
    """
    pass
