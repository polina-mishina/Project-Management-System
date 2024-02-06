import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import Task, Subtask, TaskIn
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


@app.post("/projects/{project_id}/{creator_id}/tasks",
          response_model=Task,
          summary='Добавляет задачу в базу')
def add_task(project_id: int,
             creator_id: uuid.UUID,
             task: TaskIn, db: Session = Depends(get_db)) -> Task:
    return crud.create_task(db=db,
                            project_id=project_id,
                            creator_id=creator_id,
                            task=task)


@app.post("/projects/{project_id}/{creator_id}/tasks/{task_id}/subtasks",
          response_model=Subtask,
          summary='Добавляет подзадачу в базу')
def add_subtask(project_id: int,
                task_id: int,
                creator_id: uuid.UUID,
                task: TaskIn,
                db: Session = Depends(get_db)) -> Subtask:
    return crud.create_subtask(db=db,
                               project_id=project_id,
                               creator_id=creator_id,
                               task_id=task_id,
                               task=task)


@app.get("/projects/{project_id}/tasks",
         response_model=list[Task],
         summary='Возвращает список задач')
def get_tasks_list(project_id: int,
                   db: Session = Depends(get_db)) -> List[Task]:
    return crud.get_tasks(db=db, project_id=project_id)


@app.get("/tasks/{task_id}/subtasks",
         response_model=list[Subtask],
         summary='Возвращает список подзадач')
def get_subtasks_list(task_id: int, db: Session = Depends(get_db)) -> List[Subtask]:
    return crud.get_subtasks(db=db, task_id=task_id)


@app.get("/tasks/{task_id}",
         response_model=Task,
         summary='Возвращает информацию о задаче/подзадаче')
def get_task_info(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = crud.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@app.put("/tasks/{task_id}",
         response_model=Task,
         summary='Обновляет информацию о задаче/подзадаче')
def update_task(task_id: int,
                task: TaskIn,
                db: Session = Depends(get_db)) -> Task:
    task = crud.update_task(db, task_id, task)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@app.delete("/tasks/{task_id}",
            response_model=Task,
            summary='Удаляет задачу/подзадачу из базы')
def delete_task(task_id: int,
                db: Session = Depends(get_db)) -> Task:
    deleted_task = crud.delete_task(db, task_id)
    if deleted_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return deleted_task
