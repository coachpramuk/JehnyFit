# Telegram Subscription Bot

Production-ready Telegram-бот с подписками, оплатами, закрытой группой, сценариями и рассылками.

## Стек

- Python 3.11+, FastAPI, aiogram v3, PostgreSQL, Redis, SQLAlchemy 2.0, Alembic, Docker, Celery.

## Быстрый старт

1. Скопировать `.env.example` в `.env` и заполнить:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_WEBHOOK_SECRET` (опционально, для проверки webhook)
   - `PRIVATE_GROUP_ID` (ID закрытой группы)
   - `ADMIN_IDS` (telegram_id админов через запятую)
   - `DATABASE_URL`, `REDIS_URL`, при необходимости платёжный webhook secret.

2. Запуск через Docker:

```bash
docker compose up -d
```

3. Миграции (один раз, с хоста с установленным Python и доступом к БД):

```bash
# Локально с синхронным URL для Alembic
export DATABASE_URL=postgresql://bot:bot@localhost:5432/bot_db
alembic upgrade head
```

Или выполнить миграции внутри контейнера:

```bash
docker compose run --rm app alembic upgrade head
```

4. Настроить webhook Telegram (после деплоя с HTTPS):

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://your-domain.com/webhook/telegram" \
  -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```

## Структура

- `app/main.py` — FastAPI приложение.
- `app/api/routes/` — webhook Telegram, webhook платежей, health.
- `app/bot/` — aiogram: handlers, middlewares, keyboards, filters.
- `app/core/` — логика подписок, платежей (idempotency), сценариев, рассылок.
- `app/db/` — модели SQLAlchemy 2.0, сессия, миграции Alembic.
- `app/services/` — Telegram API (invite, kick, send).
- `app/tasks/` — Celery: истечение подписок, отправка инвайта после оплаты, рассылки.

## Подписки

- Тарифы: 1 месяц, 8 недель, 6 месяцев.
- После успешного webhook платежа создаётся подписка, генерируется одноразовая invite-ссылка, пользователю отправляется сообщение (через Celery).
- Ежедневная задача помечает истёкшие подписки, удаляет пользователей из группы и отправляет уведомление.

## Сценарии

- JSON в БД (таблица `scenarios`). Пример: `examples/scenario_example.json`.
- Шаги: текст, изображение, видео, аудио, файл, inline-кнопки, переходы по кнопкам.
- Админ: `/run_scenario <scenario_id> <telegram_id>`. Опция «только для подписчиков» в сценарии.

## Рассылки

- Сегменты: все, активные подписчики, по тегу.
- Контент в JSON (текст + медиа). Запуск через Celery task `run_broadcast(broadcast_id)`.

## Админ-команды

- `/stats`, `/users`, `/subscriptions`, `/broadcast`, `/add_tag`, `/remove_tag`, `/run_scenario`, `/create_tariff`, `/update_tariff`.
- Роли: admin (по ADMIN_IDS), manager (поле в БД).

## Лицензия

MIT.
