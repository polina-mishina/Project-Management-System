import json
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator


class DocumentBase(BaseModel):
    task_id: int
    user_id: uuid.UUID

    class ConfigDict:
        from_attributes = True


class Document(DocumentBase):
    id: int
    name: str
    file_path: str
    create_date: datetime


class DocumentCreate(DocumentBase):

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
