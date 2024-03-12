import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import (Task, TaskCreate, TaskUpdate, TaskPartialUpdate,
                      Comment, UserCommentCreate, UserCommentUpdate, CommentTypeUpsert)
from .database import DB_INITIALIZER
from . import crud_tasks, crud_comments, config
from typing import List
from datetime import datetime, timezone
import json

cfg: config.Config = config.load_config()
SessionLocal = DB_INITIALIZER.init_database(str(cfg.postgres_dsn))

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/tasks",
          response_model=Task,
          summary='Добавляет задачу/подзадачу проекта в базу')
def add_task(task: TaskCreate, db: Session = Depends(get_db)) -> Task:
    task = crud_tasks.create_task(db=db, task=task)
    return task


@app.get("/tasks",
         response_model=list[Task],
         summary='Возвращает список задач проекта или подзадач задачи')
def get_tasks_list(project_id: int, parent_task_id: int = None, db: Session = Depends(get_db)) -> List[Task]:
    return crud_tasks.get_tasks(db=db, project_id=project_id, parent_task_id=parent_task_id)


@app.get("/tasks/{task_id}",
         response_model=Task,
         summary='Возвращает информацию о задаче/подзадаче')
def get_task_info(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = crud_tasks.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@app.put("/tasks/{task_id}",
         response_model=Task,
         summary='Обновляет информацию о задаче/подзадаче')
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    create_date = datetime.now(timezone.utc)
    update_dict, updated_task = crud_tasks.update_task(db=db, task_id=task_id, create_date=create_date, task=task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for field, value in update_dict.items():
        crud_comments.create_system_comment(
            db=db,
            user_id=task.user_id,
            create_date=create_date,
            field=field,
            value=value,
            task_id=task_id
        )
    return updated_task


@app.patch("/tasks/{task_id}",
           response_model=Task,
           summary='Обновляет отделные поля задачи/подзадачи')
def partial_update_task(task_id: int, task: TaskPartialUpdate, db: Session = Depends(get_db)) -> Task:
    create_date = datetime.now(timezone.utc)
    update_dict, updated_task = crud_tasks.partial_update_task(
        db=db, task_id=task_id, create_date=create_date, task=task
    )
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for field, value in update_dict.items():
        crud_comments.create_system_comment(
            db=db,
            user_id=task.user_id,
            create_date=create_date,
            field=field,
            value=value,
            task_id=task_id
        )
    return updated_task


@app.delete("/tasks/{task_id}",
            response_model=Task,
            summary='Удаляет задачу/подзадачу из базы')
def delete_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    deleted_task = crud_tasks.delete_task(db=db, task_id=task_id)
    if deleted_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return deleted_task


@app.post("/comments",
          response_model=Comment,
          summary='Добавляет пользовательский комментарий к задаче/подзадаче в базу')
def add_user_comment(comment: UserCommentCreate, db: Session = Depends(get_db)) -> Comment:
    if crud_tasks.get_task(db=db, task_id=comment.task_id) is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    comment = crud_comments.create_user_comment(db=db, comment=comment)
    return comment


@app.get("/comments",
         response_model=list[Comment],
         summary='Возвращает список комментариев задачи/подзадачи')
def get_comments_list(task_id: int, db: Session = Depends(get_db)) -> List[Comment]:
    return crud_comments.get_comments(db=db, task_id=task_id)


@app.put("/comments/{comment_id}",
         response_model=Comment,
         summary='Обновляет пользовательский комментарий')
def update_user_comment(comment_id: uuid.UUID, comment: UserCommentUpdate, db: Session = Depends(get_db)) -> Comment:
    comment = crud_comments.update_user_comment(db=db, comment_id=comment_id, comment=comment)
    if comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return comment


@app.delete("/comments/{comment_id}",
            response_model=Comment,
            summary='Удаляет пользовательский комментарий из базы')
def delete_user_comment(comment_id: uuid.UUID, db: Session = Depends(get_db)) -> Comment:
    deleted_comment = crud_comments.delete_comment(db=db, comment_id=comment_id)
    if deleted_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return deleted_comment


@app.on_event("startup")
async def on_startup():
    comment_types = []
    with open(cfg.default_comment_types_config_path, encoding="utf-8") as f:
        comment_types = json.load(f)

    for db in get_db():
        for comment_type in comment_types:
            crud_comments.upsert_comment_type(
                db, CommentTypeUpsert(**comment_type)
            )
