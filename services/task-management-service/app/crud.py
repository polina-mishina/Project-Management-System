import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from .database import models
from . import schemas


def create_task(db: Session,
                project_id: int,
                creator_id: uuid.UUID,
                task: schemas.TaskIn) -> models.Task:
    """
    Создает новую задачу в БД
    """
    db_task = models.Task(
        name=task.name,
        description=task.description,
        executor_id=task.executor_id,
        project_id=project_id,
        creator_id=creator_id,
        add_date=datetime.now(timezone.utc)
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def create_subtask(db: Session,
                   project_id: int,
                   creator_id: uuid.UUID,
                   task_id: int,
                   task: schemas.TaskIn) -> models.Task:
    """
    Создает новую подзадачу в БД
    """
    db_task = models.Task(
        name=task.name,
        description=task.description,
        executor_id=task.executor_id,
        project_id=project_id,
        creator_id=creator_id,
        add_date=datetime.now(timezone.utc),
        parent_task_id=task_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session,
              project_id: int) -> List[models.Task]:
    """
    Возвращает инфомрмацию о задачах
    """
    return (db.query(models.Task)
            .filter(models.Task.project_id == project_id, models.Task.parent_task_id == None)
            .order_by(models.Task.add_date)
            .all())


def get_subtasks(db: Session,
                 task_id: int) -> List[models.Task]:
    """
    Возвращает инфомрмацию о подзадачах
    """
    return (db.query(models.Task)
            .filter(models.Task.parent_task_id == task_id)
            .order_by(models.Task.add_date)
            .all())


def get_task(db: Session,
             task_id: int) -> models.Task | None:
    """
    Возвращает информацию о конкретной задаче/подзадаче
    """
    return (db.query(models.Task)
            .filter(models.Task.id == task_id)
            .first())


def update_task(db: Session,
                task_id: int,
                task: schemas.TaskIn) -> models.Task | None:
    """
    Обновляет информацию о задаче/подзадаче
    """
    result = (db.query(models.Task)
              .filter(models.Task.id == task_id)
              .update(task.model_dump() | {"update_date": datetime.now(timezone.utc)}))

    db.commit()

    if result == 1:
        return get_task(db, task_id)
    return None


def delete_task(db: Session,
                task_id: int) -> models.Task | None:
    """
    Удаляет информацию о задаче/подзадаче
    """
    deleted_task = get_task(db, task_id)
    result = (db.query(models.Task)
              .filter(models.Task.id == task_id)
              .delete())

    db.commit()

    if result == 1:
        return deleted_task
    return None
