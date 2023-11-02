from typing import List
from sqlalchemy.orm import Session
from .database import models
from . import schemas


def create_project(db: Session, project: schemas.ProjectIn) -> models.Project:
    """
    Создает новый проект в БД
    """
    db_project = models.Project(
        name=project.name,
        description=project.description
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(db: Session) -> List[models.Project]:
    """
    Возвращает инфомрмацию о проектах
    """
    return db.query(models.Project).all() #TODO почему предупреждение?


def get_project(db: Session, project_id: int) -> models.Project | None:
    """
    Возвращает информацию о конкретном проекте
    """
    return db.query(models.Project) \
        .filter(models.Project.id == project_id) \
        .first()


def update_project(db: Session, project_id: int, project: schemas.ProjectIn) -> models.Project | None:
    """
    Обновляет информацию о проекте
    """
    result = db.query(models.Project) \
        .filter(models.Project.id == project_id) \
        .update(project.model_dump())
    db.commit()

    if result == 1:
        return get_project(db, project_id)
    return None


def delete_project(db: Session, project_id: int) -> models.Project | None:
    """
    Удаляет информацию о проекте
    """
    deleted_project = get_project(db, project_id)
    result = db.query(models.Project) \
        .filter(models.Project.id == project_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_project
    return None
