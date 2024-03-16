import json
import uuid
from datetime import datetime

from pydantic import BaseModel, model_validator


class CommentTypeUpsert(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True


class Comment(BaseModel):
    id: uuid.UUID
    type_id: int
    task_id: int
    create_date: datetime
    user_id: uuid.UUID
    data: dict

    class ConfigDict:
        from_attributes = True


class UserCommentCreate(BaseModel):
    task_id: int
    user_id: uuid.UUID
    message: str

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class ConfigDict:
        from_attributes = True


class UserCommentUpdate(BaseModel):
    message: str

    class ConfigDict:
        from_attributes = True
