from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI()


class Project(BaseModel):
    name: str
    description: Optional[str] = None


projects_db: Dict[int, Project] = {}


@app.post("/projects", response_model=Project, summary='Добавляет проект в базу')
def create_project(project: Project):
    projects_db[len(projects_db) + 1] = project
    return project


@app.get("/projects", response_model=Dict[int, Project], summary='Возвращает список проектов')
def get_projects():
    return projects_db


@app.get("/projects/{project_id}", response_model=Project, summary='Возвращает информацию о проекте')
def get_project(project_id: int):
    if project_id in projects_db:
        return projects_db[project_id]
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})


@app.put("/projects/{project_id}", response_model=Project, summary='Обновляет информацию о проекте')
def update_project(project_id: int, project: Project):
    if project_id in projects_db:
        projects_db[project_id] = project
        return projects_db[project_id]
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})


@app.delete("/projects/{project_id}", response_model=Project, summary='Удаляет проект из базы')
def delete_project(project_id: int):
    if project_id in projects_db:
        del projects_db[project_id]
        return JSONResponse(status_code=200, content={"message": "Проект успешно удален"})
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})
