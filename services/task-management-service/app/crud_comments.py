import uuid
from datetime import datetime, timezone
from typing import Any, List

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from .database import models
from . import schemas


def upsert_comment_type(db: Session, comment_type: schemas.CommentTypeUpsert) -> models.CommentType | None:
    """
    Обновляет или добавляет тип комментария в БД
    """

    stm = insert(models.CommentType).values(comment_type.model_dump())
    stm = stm.on_conflict_do_update(
        constraint='comment_type_pkey',
        set_={"name": comment_type.name}
    )
    result = db.execute(stm)

    db.commit()
    if result:
        return get_comment_type(db, comment_type.id)
    return None


def get_comment_type(db: Session,
                     type_id: int) -> models.CommentType:
    """
    Возвращает информацию о типе комментария
    """
    result = db.execute(select(models.CommentType).filter(models.CommentType.id == type_id).limit(1))
    return result.scalars().one_or_none()


def create_system_comment(db: Session,
                          task_id: int,
                          user_id: uuid.UUID,
                          create_date: datetime,
                          field: str,
                          value: Any) -> models.Comment:
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
    elif field == "executor_id":
        type_id = 2
        if not value[0]:
            data["early_executor_id"] = ""
            data["executor_id"] = str(value[1])
        elif not value[1]:
            data["early_executor_id"] = str(value[0])
            data["executor_id"] = ""
        else:
            data["early_executor_id"] = str(value[0])
            data["executor_id"] = str(value[1])
    elif field == "completion_date":
        type_id = 3
        if not value[0]:
            data["early_completion_date"] = ""
            data["completion_date"] = str(value[1])
        elif not value[1]:
            data["early_completion_date"] = str(value[0])
            data["completion_date"] = ""
        else:
            data["early_completion_date"] = str(value[0])
            data["completion_date"] = str(value[1])

    db_comment = models.Comment(
        user_id=user_id,
        data=data,
        create_date=create_date,
        type_id=type_id,
        task_id=task_id
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def create_user_comment(db: Session,
                        comment: schemas.UserCommentCreate) -> models.Comment:
    """
    Создает новый пользовательский комментарий в БД
    """
    data = {"message": comment.message}
    db_comment = models.Comment(
        user_id=comment.user_id,
        data=data,
        create_date=datetime.now(timezone.utc),
        type_id=4,
        task_id=comment.task_id
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments(db: Session,
                 task_id: int) -> List[models.Comment]:
    """
    Возвращает инфомрмацию о задачах
    """
    return (db.query(models.Comment)
            .filter(models.Comment.task_id == task_id)
            .order_by(models.Comment.create_date)
            .all())


def get_comment(db: Session,
                comment_id: uuid.UUID) -> models.Comment | None:
    """
    Возвращает информацию о комментарии
    """
    return (db.query(models.Comment)
            .filter(models.Comment.id == comment_id)
            .first())


def get_task_comment(db: Session,
                     task_id: int,
                     comment_id: uuid.UUID | None) -> models.Comment | None:
    """
    Возвращает информацию о комментарии задачи
    """
    return (db.query(models.Comment)
            .filter(models.Comment.id == comment_id, models.Comment.task_id == task_id)
            .first())


def update_user_comment(db: Session,
                        comment_id: uuid.UUID,
                        comment: schemas.UserCommentUpdate) -> models.Comment | None:
    """
    Обновляет пользовательский комментарий
    """
    data = {"message": comment.message}
    result = (db.query(models.Comment)
              .filter(models.Comment.id == comment_id)
              .update({"data": data}))

    db.commit()

    if result == 1:
        return get_comment(db, comment_id)
    return None


def delete_comment(db: Session,
                   comment_id: uuid.UUID) -> tuple[models.Comment, List[str]] | tuple[None, None]:
    """
    Удаляет пользовательский комментарий
    """
    deleted_comment = get_comment(db, comment_id)
    file_paths = []
    if deleted_comment:
        for document in deleted_comment.documents:
            file_paths.append(document.file_path)
    result = (db.query(models.Comment)
              .filter(models.Comment.id == comment_id, models.Comment.type_id == 4)
              .delete())

    db.commit()

    if result == 1:
        return deleted_comment, file_paths
    return None, None
