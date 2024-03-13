import uuid
from datetime import datetime
from pydantic import BaseModel


class CommentTypeUpsert(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True


class Comment(BaseModel):
    id: uuid.UUID
    type_id: int
    project_id: int
    create_date: datetime
    user_id: uuid.UUID
    data: dict

    class ConfigDict:
        from_attributes = True
