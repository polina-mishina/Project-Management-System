from pydantic import BaseModel
from typing import Optional


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class Project(ProjectBase):
    id: int
