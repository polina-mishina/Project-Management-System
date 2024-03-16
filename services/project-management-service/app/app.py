import uuid
from datetime import datetime, timezone
import json
import os

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .schemas import (Project, ProjectCreate, ProjectUpdate, ProjectPartialUpdate,
                      CommentTypeUpsert, Document, DocumentCreate)
from .database import DB_INITIALIZER
from . import crud_projects, crud_comments, crud_documents, config
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


extensions = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/x-zip-compressed": ".zip"
}


@app.post("/projects", response_model=Project, summary='Добавляет проект в базу')
def add_project(project: ProjectCreate,
                files: List[UploadFile] = File(None),
                db: Session = Depends(get_db)) -> Project:
    project = crud_projects.create_project(db=db, project=project)
    for file in files:
        extension = extensions.get(file.content_type)
        if extension:
            file_path = create_file_path(storage_path=cfg.storage_path, extension=extension)
            create_file(file=file, file_path=file_path)
            crud_documents.create_document(
                db=db,
                file_name=file.filename,
                file_path=file_path,
                user_id=project.creator_id,
                project_id=project.id
            )
    return project


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
    deleted_project, file_paths = crud_projects.delete_project(db=db, project_id=project_id)
    if deleted_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    for file_path in file_paths:
        os.remove(file_path)
    return deleted_project


@app.post("/documents",
          response_model=list(Document),
          summary='Добавляет вложения в базу')
def add_documents(document: DocumentCreate,
                  files: List[UploadFile] = File(None),
                  db: Session = Depends(get_db)) -> List[Document]:
    if crud_projects.get_project(db=db, project_id=document.project_id) is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    added_documents = []
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
                project_id=document.project_id
            )
            added_documents.append(document)
    return added_documents


@app.get("/documents",
         response_model=list(Document),
         summary='Возвращает список вложений')
def get_documents_list(project_id: int, db: Session = Depends(get_db)) -> List[Document]:
    return crud_documents.get_documents(db=db, project_id=project_id)


@app.delete("/documents/{document_id}",
            response_model=Document,
            summary='Удаляет вложение из базы')
def delete_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    deleted_document = crud_documents.delete_document(db=db, document_id=document_id)
    if deleted_document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    os.remove(deleted_document.file_path)
    return deleted_document


def create_file_path(storage_path: str, extension: str):
    return os.path.join(storage_path, str(uuid.uuid4()) + extension)


def create_file(file: UploadFile, file_path: str):
    try:
        with open(file_path, "wb") as out_file:
            out_file.write(file.file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при работе с файлом")


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
