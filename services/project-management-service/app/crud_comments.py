import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from .database import models
from . import schemas


def upsert_comment_type(db: Session, comment_type: schemas.CommentTypeUpsert) -> models.ProjectCommentType | None:
    """
    Обновляет или добавляет тип комментария в БД
    """

    stm = insert(models.ProjectCommentType).values(comment_type.model_dump())
    stm = stm.on_conflict_do_update(
        constraint='project_comment_type_pkey',
        set_={"name": comment_type.name}
    )
    result = db.execute(stm)

    db.commit()
    if result:
        return get_comment_type(db, comment_type.id)
    return None


def get_comment_type(db: Session,
                     type_id: int) -> models.ProjectCommentType:
    """
    Возвращает информацию о типе комментария
    """
    result = db.execute(select(models.ProjectCommentType).filter(models.ProjectCommentType.id == type_id).limit(1))
    return result.scalars().one_or_none()


def create_system_comment(db: Session,
                          project_id: int,
                          user_id: uuid.UUID,
                          create_date: datetime,
                          field: str,
                          value: Any) -> models.ProjectComment:
    """
    Создает новый системный комментарий в БД
    """
    data = {}
    type_id = 1

    if field == "name":
        data["early_name"] = value[0]
        data["name"] = value[1]
    elif field == "description":
        data["description"] = None
    elif field == "completion_date":
        type_id = 2
        if not value[0]:
            data["early_completion_date"] = ""
            data["completion_date"] = str(value[1])
        elif not value[1]:
            data["early_completion_date"] = str(value[0])
            data["completion_date"] = ""
        else:
            data["early_completion_date"] = str(value[0])
            data["completion_date"] = str(value[1])

    db_comment = models.ProjectComment(
        user_id=user_id,
        data=data,
        create_date=create_date,
        type_id=type_id,
        project_id=project_id
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
