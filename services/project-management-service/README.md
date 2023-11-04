# API сервиса управления проектами


| Ресурс                     | Метод  | Что делает                                          |
|----------------------------|--------|-----------------------------------------------------|
| /projects                  | POST   | Добавляет проект в базу                             |
| /projects                  | GET    | Возвращает список всех проектов                     |
| /projects/{project_id}     | GET    | Возвращает информацию о конкретном проекте          |
| /projects/{project_id}     | PUT    | Обновляет информацию о проекте                      |
| /projects/{project_id}     | DELETE | Удаляет проект из базы                              |


# Зависимости

Перед запуском сервиса необходимо установить зависимости из файла requirements.txt

# Запуск

```bash
uvicorn app:app --port 5000 --reload
```

# Запуск с использование файла конфигурации .env

Для запуска из файла конфигурации нужно поместить файл .env в корень сервиса

# Запуск с переопределением переменных окружения

```bash
uvicorn app:app --port 5000 --reload
```

или

```bash
export POSTGRES_DSN=postgresql://project-management:project-management@172.18.0.1:5432/project-management
uvicorn app:app --port 5000 --reload
```

# Конфигурация
| Переменная   | Назначение                      | Значение по умолчанию                         |
|--------------|---------------------------------|-----------------------------------------------|
| POSTGRES_DSN | Строка подключения к PostgreSQL | postgresql://user:pass@localhost/foobar |

# Документация

После запуска доступна документация: http://127.0.0.1:5000/docs

# Сборка образа
```bash
docker build -t project-management/project-management-service:0.1 .
```

# Модули сервиса

- App - Точка входа в приложение, реализует FastAPI-приложение соответсвии с требованиями
- Schemas - Реализует Pydantic-схемы сущностей приложения
- Database - Реализует взаимодействией с базой данных - подключение к ней и sqalchemy-модели
- CRUD - Реализует CRUD-методы для работы с сущностями сервиса
- Config - Отвечает за подгрузку конфигурации


```mermaid
graph TD
    App --> CRUD
    App --> Database
    CRUD --> Database
    CRUD --> Schemas
    App --> Schemas
    App --> Config
```
