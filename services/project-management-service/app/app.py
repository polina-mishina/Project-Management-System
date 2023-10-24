from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .schemas import Project, ProjectBase
from typing import Dict

app = FastAPI()

projects_db: Dict[int, Project] = {}


@app.post("/projects", response_model=Project, summary='Добавляет проект в базу')
def create_project(project: ProjectBase):
    result = Project(
        **project.model_dump(),
        id=len(projects_db) + 1,
    )
    projects_db[result.id] = result
    return result


@app.get("/projects", response_model=list[Project], summary='Возвращает список проектов')
def get_projects():
    return list(projects_db.values())


@app.get("/projects/{project_id}", summary='Возвращает информацию о проекте')
def get_project(project_id: int):
    if project_id in projects_db:
        return projects_db[project_id]
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})


@app.put("/projects/{project_id}", summary='Обновляет информацию о проекте')
def update_project(project_id: int, project: ProjectBase):
    if project_id in projects_db:
        result = Project(
            **project.model_dump(),
            id=project_id,
        )
        projects_db[project_id] = result
        return projects_db[project_id]
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})


@app.delete("/projects/{project_id}", summary='Удаляет проект из базы')
def delete_project(project_id: int):
    if project_id in projects_db:
        result = projects_db[project_id]
        del projects_db[project_id]
        return result
    return JSONResponse(status_code=404, content={"message": "Проект не найден"})
