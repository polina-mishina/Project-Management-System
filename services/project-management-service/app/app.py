from datetime import datetime, timezone
import json

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import Project, ProjectCreate, ProjectUpdate, ProjectPartialUpdate, CommentTypeUpsert
from .database import DB_INITIALIZER
from . import crud_projects, crud_comments, config
from typing import List

cfg: config.Config = config.load_config()
SessionLocal = DB_INITIALIZER.init_database(str(cfg.postgres_dsn))

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/projects", response_model=Project, summary='Добавляет проект в базу')
def add_project(project: ProjectCreate,
                db: Session = Depends(get_db)) -> Project:
    return crud_projects.create_project(db=db, project=project)


@app.get("/projects", response_model=list[Project], summary='Возвращает список проектов')
def get_projects_list(db: Session = Depends(get_db)) -> List[Project]:
    return crud_projects.get_projects(db=db)


@app.get("/projects/{project_id}",
         response_model=Project,
         summary='Возвращает информацию о проекте')
def get_project_info(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = crud_projects.get_project(db=db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@app.put("/projects/{project_id}",
         response_model=Project,
         summary='Обновляет информацию о проекте')
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)) -> Project:
    create_date = datetime.now(timezone.utc)
    update_dict, updated_project = crud_projects.update_project(
        db=db, project_id=project_id, create_date=create_date, project=project
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    for field, value in update_dict.items():
        crud_comments.create_system_comment(
            db=db,
            user_id=project.user_id,
            create_date=create_date,
            field=field,
            value=value,
            project_id=project_id
        )
    return updated_project


@app.patch("/projects/{project_id}",
           response_model=Project,
           summary='Обновляет отделные поля проекта')
def partial_update_project(project_id: int, project: ProjectPartialUpdate, db: Session = Depends(get_db)) -> Project:
    create_date = datetime.now(timezone.utc)
    update_dict, updated_project = crud_projects.partial_update_project(
        db=db, project_id=project_id, create_date=create_date, project=project
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    for field, value in update_dict.items():
        crud_comments.create_system_comment(
            db=db,
            user_id=project.user_id,
            create_date=create_date,
            field=field,
            value=value,
            project_id=project_id
        )
    return updated_project


@app.delete("/projects/{project_id}", summary='Удаляет проект из базы')
def delete_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    deleted_project = crud_projects.delete_project(db=db, project_id=project_id)
    if deleted_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return deleted_project


@app.on_event("startup")
async def on_startup():
    comment_types = []
    with open(cfg.default_project_comment_types_config_path, encoding="utf-8") as f:
        comment_types = json.load(f)

    for db in get_db():
        for comment_type in comment_types:
            crud_comments.upsert_comment_type(
                db, CommentTypeUpsert(**comment_type)
            )

