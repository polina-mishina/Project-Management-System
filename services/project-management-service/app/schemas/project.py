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


class ProjectIn(ProjectBase):
    """
    Модель для добавления/обновления проекта, т.к при добавлении/обновлении
    id не передается или передается через url, а не через тело запроса
    """
    pass
