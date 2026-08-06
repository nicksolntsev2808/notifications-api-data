# notifications-api

API для очереди уведомлений (email/sms/push) на FastAPI с MongoDB. Уведомление рождается в статусе `pending`, дальше переходит либо в `sent`, либо в `failed`.

## Возможности

- Создание уведомления (`pending` по умолчанию)
- Список уведомлений с фильтром по статусу и каналу
- Получение уведомления по id
- Пометить как отправленное (`/send`)
- Пометить как неудавшееся (`/fail`)
- Удаление
- Проверка состояния сервиса через `/health`

## Технологии

- Python 3.11+
- FastAPI
- Motor
- MongoDB
- Uvicorn

## Эндпоинты

- `GET /health`
- `POST /api/v1/notifications`
- `GET /api/v1/notifications`
- `GET /api/v1/notifications/{id}`
- `PATCH /api/v1/notifications/{id}/send`
- `PATCH /api/v1/notifications/{id}/fail`
- `DELETE /api/v1/notifications/{id}`

## Развёртывание на двух серверах

Этот проект рассчитан на сценарий, где приложение и база данных живут на разных машинах — см. `.env.example`: `MONGO_URI` указывает не на `localhost`, а на отдельный `<DB-HOST>`. Порты (`9020` для приложения, `28120` для проброса MongoDB) выбраны так, чтобы не пересекаться с другими сервисами на тех же хостах — при необходимости смени их под свою среду.

Настрой окружение, зависимости, MongoDB на DB-хосте и `.env` на APP-хосте самостоятельно — см. `requirements.txt` и `.env.example` как отправную точку.
