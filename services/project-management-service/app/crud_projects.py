from datetime import datetime, timezone
from typing import List, Tuple
from sqlalchemy.orm import Session
from .database import models
from . import schemas


def create_project(db: Session,
                   project: schemas.ProjectCreate) -> models.Project:
    """
    Создает новый проект в БД
    """
    db_project = models.Project(
        name=project.name,
        description=project.description,
        creator_id=project.creator_id,
        completion_date=project.completion_date,
        create_date=datetime.now(timezone.utc)
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(db: Session) -> List[models.Project]:
    """
    Возвращает информацию о проектах
    """
    return (db.query(models.Project)
            .order_by(models.Project.create_date)
            .all())


def get_project(db: Session,
                project_id: int) -> models.Project | None:
    """
    Возвращает информацию о конкретном проекте
    """
    return (db.query(models.Project)
            .filter(models.Project.id == project_id)
            .first())


def update_project(db: Session,
                   project_id: int,
                   create_date: datetime,
                   project: schemas.ProjectUpdate) -> Tuple[dict | None, models.Project | None]:
    """
    Обновляет информацию о проекте
    """
    current_project = get_project(db, project_id)
    update_dict = {}

    if not current_project:
        return update_dict, None

    for field, value in project.model_dump(exclude={"user_id"}).items():
        current_value = getattr(current_project, field)
        if current_value != value:
            update_dict[field] = current_value, value

    result = (db.query(models.Project)
              .filter(models.Project.id == project_id)
              .update(project.model_dump(exclude={"user_id"}) | {"update_date": create_date}))

    db.commit()

    if result == 1:
        return update_dict, get_project(db, project_id)
    return None, None


def partial_update_project(db: Session,
                           project_id: int,
                           create_date: datetime,
                           project: schemas.ProjectPartialUpdate) -> Tuple[dict | None, models.Project | None]:
    """
    Обновляет частично информацию о проекте
    """
    current_project = get_project(db, project_id)
    update_dict = {}

    if not current_project:
        return update_dict, None

    for field, value in project.model_dump(exclude_unset=True, exclude={"user_id"}).items():
        current_value = getattr(current_project, field)
        if current_value != value:
            update_dict[field] = current_value, value

    result = (db.query(models.Project)
              .filter(models.Project.id == project_id)
              .update(project.model_dump(exclude_unset=True, exclude={"user_id"}) | {"update_date": create_date}))

    db.commit()

    if result == 1:
        return update_dict, get_project(db, project_id)
    return None, None


def delete_project(db: Session, project_id: int) -> tuple[models.Project, List[str]] | tuple[None, None]:
    """
    Удаляет информацию о проекте
    """
    deleted_project = get_project(db, project_id)
    file_paths = []
    if deleted_project:
        for document in deleted_project.documents:
            file_paths.append(document.file_path)

    result = (db.query(models.Project)
              .filter(models.Project.id == project_id)
              .delete())

    db.commit()

    if result == 1:
        return deleted_project, file_paths
    return None, None
