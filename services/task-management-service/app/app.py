import os
import uuid

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .schemas import (Task, TaskCreate, TaskUpdate, TaskPartialUpdate,
                      Comment, UserCommentCreate, UserCommentUpdate, CommentTypeUpsert,
                      Document, DocumentCreate)
from .database import DB_INITIALIZER
from . import crud_tasks, crud_comments, crud_documents, config
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


extensions = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/x-zip-compressed": ".zip"
}


@app.post("/tasks",
          response_model=Task,
          summary='Добавляет задачу/подзадачу проекта в базу')
def add_task(task: TaskCreate,
             files: List[UploadFile] = File(None),
             db: Session = Depends(get_db)) -> Task:
    task = crud_tasks.create_task(db=db, task=task)
    for file in files:
        extension = extensions.get(file.content_type)
        if extension:
            file_path = create_file_path(storage_path=cfg.storage_path, extension=extension)
            create_file(file=file, file_path=file_path)
            crud_documents.create_document(
                db=db,
                file_name=file.filename,
                file_path=file_path,
                user_id=task.creator_id,
                task_id=task.id
            )
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
    deleted_task, file_paths = crud_tasks.delete_task(db=db, task_id=task_id)
    if deleted_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    for file_path in file_paths:
        os.remove(file_path)
    return deleted_task


@app.post("/comments",
          response_model=Comment,
          summary='Добавляет пользовательский комментарий к задаче/подзадаче в базу')
def add_user_comment(comment: UserCommentCreate,
                     files: List[UploadFile] = File(None),
                     db: Session = Depends(get_db)) -> Comment:
    if crud_tasks.get_task(db=db, task_id=comment.task_id) is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    comment = crud_comments.create_user_comment(db=db, comment=comment)
    for file in files:
        extension = extensions.get(file.content_type)
        if extension:
            file_path = create_file_path(storage_path=cfg.storage_path, extension=extension)
            create_file(file=file, file_path=file_path)
            crud_documents.create_document(
                db=db,
                file_name=file.filename,
                file_path=file_path,
                user_id=comment.user_id,
                task_id=comment.task_id,
                comment_id=comment.id
            )
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
    deleted_comment, file_paths = crud_comments.delete_comment(db=db, comment_id=comment_id)
    if deleted_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    for file_path in file_paths:
        os.remove(file_path)
    return deleted_comment


@app.post("/documents",
          response_model=list[Document],
          summary='Добавляет вложения к задаче/комментарию в базу')
def add_documents(document: DocumentCreate,
                  files: List[UploadFile] = File(None),
                  db: Session = Depends(get_db)) -> List[Document]:
    if crud_tasks.get_task(db=db, task_id=document.task_id) is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if document.comment_id:
        if crud_comments.get_task_comment(db=db, task_id=document.task_id, comment_id=document.comment_id) is None:
            raise HTTPException(status_code=404, detail="Комментарий не найден")

    for file in files:
        extension = extensions.get(file.content_type)
        if extension:
            file_path = create_file_path(storage_path=cfg.storage_path, extension=extension)
            create_file(file=file, file_path=file_path)
            document = crud_documents.create_document(
                db=db,
                file_name=file.filename,
                file_path=file_path,
                user_id=document.user_id,
                task_id=document.task_id,
                comment_id=document.comment_id
            )
    return get_documents_list(document.task_id, document.comment_id, db=db)


@app.get("/documents",
         response_model=list[Document],
         summary='Возвращает список вложений задачи/комментария')
def get_documents_list(task_id: int,
                       comment_id: uuid.UUID = None,
                       db: Session = Depends(get_db)) -> List[Document]:
    return crud_documents.get_documents(db=db, task_id=task_id, comment_id=comment_id)


@app.delete("/documents/{document_id}",
            response_model=Document,
            summary='Удаляет вложение задачи/комментария из базы')
def delete_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    deleted_document = crud_documents.delete_document(db=db, document_id=document_id)
    if deleted_document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    os.remove(deleted_document.file_path)
    return deleted_document


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


def create_file_path(storage_path: str, extension: str):
    return os.path.join(storage_path, str(uuid.uuid4()) + extension)


def create_file(file: UploadFile, file_path: str):
    try:
        with open(file_path, "wb") as out_file:
            out_file.write(file.file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при работе с файлом")
