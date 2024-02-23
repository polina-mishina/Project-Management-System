from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy.orm import Session

from .database import models
from . import schemas


def create_task(db: Session, create_date: datetime, task: schemas.TaskCreate) -> Tuple[dict, models.Task]:
    """
    Создает новую задачу в БД
    """
    db_task = models.Task(
        name=task.name,
        description=task.description,
        project_id=task.project_id,
        parent_task_id=task.parent_task_id,
        creator_id=task.creator_id,
        executor_id=task.executor_id,
        completion_date=task.completion_date,
        create_date=create_date
    )

    update_dict = {}
    exclude_fields = {"creator_id", "project_id", "parent_task_id", "create_date"}
    for field, value in task.model_dump(exclude=exclude_fields).items():
        update_dict[field] = value

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return update_dict, db_task


def get_tasks(db: Session,
              project_id: int,
              parent_task_id: int | None) -> List[models.Task]:
    """
    Возвращает инфомрмацию о задачах
    """
    return (db.query(models.Task)
            .filter(models.Task.project_id == project_id, models.Task.parent_task_id == parent_task_id)
            .order_by(models.Task.create_date)
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
                create_date: datetime,
                task: schemas.TaskUpdate) -> Tuple[dict, models.Task | None]:
    """
    Обновляет информацию о задаче/подзадаче
    """
    current_task = get_task(db, task_id)
    update_dict = {}

    if not current_task:
        return update_dict, None

    for field, value in task.model_dump(exclude={"user_id"}).items():
        current_value = getattr(current_task, field)
        if current_value != value:
            update_dict[field] = value

    result = (db.query(models.Task)
              .filter(models.Task.id == task_id)
              .update(task.model_dump(exclude={"user_id"}) | {"update_date": create_date}))

    db.commit()

    if result == 1:
        return update_dict, get_task(db, task_id)
    return update_dict, None


def partial_update_task(db: Session,
                        task_id: int,
                        create_date: datetime,
                        task: schemas.TaskPartialUpdate) -> Tuple[dict, models.Task | None]:
    """
    Обновляет частично информацию о задаче/подзадаче
    """
    current_task = get_task(db, task_id)
    update_dict = {}

    if not current_task:
        return update_dict, None

    for field, value in task.model_dump(exclude_unset=True, exclude={"user_id"}).items():
        current_value = getattr(current_task, field)
        if current_value != value:
            update_dict[field] = value

    result = (db.query(models.Task)
              .filter(models.Task.id == task_id)
              .update(task.model_dump(exclude_unset=True, exclude={"user_id"}) | {"update_date": create_date}))

    db.commit()

    if result == 1:
        return update_dict, get_task(db, task_id)
    return update_dict, None


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
