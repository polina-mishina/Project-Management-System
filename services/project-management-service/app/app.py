from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .schemas import Project, ProjectIn
from .database import Base, engine, SessionLocal
from . import crud
from typing import List

# Создание таблиц базы данных
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Создание сессии для запроса
# с закрытием сеанса после завершения запроса,
# даже если было исключение при обработке запроса
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/projects", response_model=Project, summary='Добавляет проект в базу')
def add_project(project: ProjectIn, db: Session = Depends(get_db)) -> Project:
    return crud.create_project(db=db, project=project)


@app.get("/projects", response_model=list[Project], summary='Возвращает список проектов')
def get_projects_list(db: Session = Depends(get_db)) -> List[Project]:
    return crud.get_projects(db)


@app.get("/projects/{project_id}", summary='Возвращает информацию о проекте')
def get_project_info(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = crud.get_project(db, project_id)
    if project is not None:
        return project
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})


@app.put("/projects/{project_id}", summary='Обновляет информацию о проекте')
def update_project(project_id: int, project: ProjectIn, db: Session = Depends(get_db)) -> Project:
    project = crud.update_project(db, project_id, project)
    if project is not None:
        return project
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})


@app.delete("/projects/{project_id}", summary='Удаляет проект из базы')
def delete_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    deleted_project = crud.delete_project(db, project_id)
    if deleted_project is not None:
        return deleted_project
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})
