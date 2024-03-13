import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from .database import models


def create_document(db: Session,
                    file_name: str,
                    file_path: str,
                    user_id: uuid.UUID,
                    task_id: int) -> models.TaskDocument:
    """
    Создает новый документ в БД
    """
    db_document = models.TaskDocument(
        user_id=user_id,
        name=file_name,
        file_path=file_path,
        create_date=datetime.now(timezone.utc),
        task_id=task_id
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_documents(db: Session,
                  task_id: int) -> List[models.TaskDocument]:
    """
    Возвращает вложения
    """
    return (db.query(models.TaskDocument)
            .filter(models.TaskDocument.task_id == task_id)
            .order_by(models.TaskDocument.create_date)
            .all())


def get_document(db: Session,
                 document_id: int) -> models.TaskDocument | None:
    """
    Возвращает вложение
    """
    return (db.query(models.TaskDocument)
            .filter(models.TaskDocument.id == document_id)
            .first())


def delete_document(db: Session,
                    document_id: int) -> models.TaskDocument | None:
    """
    Удаляет вложение
    """
    deleted_document = get_document(db, document_id)
    result = (db.query(models.TaskDocument)
              .filter(models.TaskDocument.id == document_id)
              .delete())

    db.commit()

    if result == 1:
        return deleted_document
    return None
