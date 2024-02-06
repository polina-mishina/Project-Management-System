import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import Project, ProjectIn
from .database import DB_INITIALIZER
from . import crud, config
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


@app.post("/projects/{creator_id}", response_model=Project, summary='Добавляет проект в базу')
def add_project(creator_id: uuid.UUID,
                project: ProjectIn,
                db: Session = Depends(get_db)) -> Project:
    return crud.create_project(db=db, creator_id=creator_id, project=project)


@app.get("/projects", response_model=list[Project], summary='Возвращает список проектов')
def get_projects_list(db: Session = Depends(get_db)) -> List[Project]:
    return crud.get_projects(db=db)


@app.get("/projects/{project_id}", summary='Возвращает информацию о проекте')
def get_project_info(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = crud.get_project(db=db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@app.put("/projects/{project_id}", summary='Обновляет информацию о проекте')
def update_project(project_id: int, project: ProjectIn, db: Session = Depends(get_db)) -> Project:
    project = crud.update_project(db=db, project_id=project_id, project=project)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@app.delete("/projects/{project_id}", summary='Удаляет проект из базы')
def delete_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    deleted_project = crud.delete_project(db=db, project_id=project_id)
    if deleted_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return deleted_project
