# notifications-api-pg

Тот же сервис уведомлений, что и `notifications-api`, но на PostgreSQL вместо MongoDB — SQLAlchemy (async) + asyncpg вместо Motor. Бизнес-логика идентична: уведомление рождается `pending`, дальше переходит в `sent` или `failed`.

## Отличия от Mongo-версии

- `app/db.py` — async SQLAlchemy engine + сессии вместо Motor-клиента
- `app/models.py` — теперь это ORM-модель (таблица), а не Pydantic-схема
- `app/schemas.py` — Pydantic-схемы для запросов/ответов вынесены отдельно от ORM-модели (в Mongo-версии их не разделяли, так как не было ORM-слоя)
- Тип id — `UUID`, а не строка ObjectId
- Таблица создаётся автоматически при старте (`Base.metadata.create_all`) — в проде так делать не стоит, для этого используют миграции (Alembic), но для практики сойдёт

## Технологии

Python 3.11+, FastAPI, SQLAlchemy (async), asyncpg, PostgreSQL, Uvicorn

## Эндпоинты

Те же, что в Mongo-версии:

- `GET /health`
- `POST /api/v1/notifications`
- `GET /api/v1/notifications`
- `GET /api/v1/notifications/{id}`
- `PATCH /api/v1/notifications/{id}/send`
- `PATCH /api/v1/notifications/{id}/fail`
- `DELETE /api/v1/notifications/{id}`

## Развёртывание на двух серверах

Порты: `9070` приложение, `28170` проброс PostgreSQL — не пересекаются с остальными практическими проектами (Mongo-версии занимают `28110`–`28160`).

На DB-хосте нужен PostgreSQL с созданными пользователем/базой (см. `.env.example`), а не просто `docker run postgres` без параметров — почитай, какие переменные окружения принимает официальный образ `postgres` в Docker Hub, чтобы сразу создать нужного юзера и базу.

Настрой окружение, зависимости, PostgreSQL на DB-хосте и `.env` на APP-хосте самостоятельно.
