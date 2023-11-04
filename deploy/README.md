# Развертывание СУБД и сервисов

# Содержание
1. [Запуск](#запуск)
2. [Остановка](#остановка)
3. [PostgreSQL](#postgresql)

# Запуск
```bash
docker-compose -p project-management up -d
```
## Проверка статусов сервисов

```bash
docker ps --all --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

# Остановка
```bash
docker-compose stop
```

# PostgreSQL

За развертывание PostgreSQL отвечает следующая часть compose-файла:

```bash
volumes:
  postgresql-data:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: ./postgresql/data
services:
  postgresql:
    image: postgres:14.9-alpine3.18
    volumes:
      - postgresql-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: project-management
      POSTGRES_USER: project-management
      POSTGRES_DB: project-management
      PGDATA: /var/lib/postgresql/data/db-files/
    ports:
      - "5432:5432"
```

В нем:

- Создается диск (volume) с названием **postgresql-data**, для хранения данных используется директория ./postgresql/data. Рекомендуется добавить директорию в gitignore:

```bash
deploy/postgresql/data/*
!deploy/postgresql/data/.gitkeep
```
- Создается контейнер **postgresql** на базе образа postgres:14.9-alpine3.18
- К контейнеру монтируется volume **postgresql-data**
- Пробрасываются порты, PostreSQL будет доступен по {MACHINE_IP}:5432, например: 172.18.0.1:5432.
- Через переменные окружения задается пользователь, название первичной базы данных и директория хранения данных внутри контейнера:
```bash
POSTGRES_PASSWORD: project-management
POSTGRES_USER: project-management
 POSTGRES_DB: project-management
PGDATA: /var/lib/postgresql/data/db-files/
```

Для тестирования подключения можно использовать утилиту psql или какой-либо GUI-клиент

## [Образ на Docker-хабе](https://hub.docker.com/_/postgres)
---
