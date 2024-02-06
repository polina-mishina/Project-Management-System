import uuid

from fastapi_users import schemas
from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str

    class ConfigDict:
        from_attributes = True


class GroupRead(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True


class GroupUpsert(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True


class GroupUpdate(BaseModel):
    name: str

    class ConfigDict:
        from_attributes = True


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str | None = None
    last_name: str | None = None
    group_id: int | None = None


class UserCreate(schemas.BaseUserCreate):
    first_name: str = None
    last_name: str = None
    group_id: int | None = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str = None
    last_name: str = None
    group_id: int | None = None
