# Архитектура Telegram Subscription Bot

## Обзор

```
┌─────────────────┐     webhook      ┌──────────────────┐
│  Telegram API   │ ◄───────────────►│  FastAPI + Bot   │
└─────────────────┘                  └────────┬─────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
             ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
             │  PostgreSQL │           │    Redis    │           │   Celery    │
             │  (данные)   │           │  (кэш,      │           │  (фоновые   │
             │             │           │   idempotency)           │   задачи)   │
             └─────────────┘           └─────────────┘           └─────────────┘
                    ▲                         ▲                         ▲
                    │                         │                         │
                    └─────────────────────────┴─────────────────────────┴─────────
                                              │
                                    ┌─────────┴─────────┐
                                    │ Payment Provider  │
                                    │     (webhook)     │
                                    └───────────────────┘
```

## Компоненты

| Компонент | Назначение |
|-----------|------------|
| **FastAPI** | Webhook endpoint для Telegram, webhook для платежей, health, admin API |
| **aiogram v3** | Обработка сообщений, сценарии, рассылки, команды |
| **PostgreSQL** | User, Subscription, Payment, Scenario, Broadcast |
| **Redis** | Idempotency keys для webhook, кэш, Celery broker |
| **Celery** | Ежедневная проверка истёкших подписок, отложенные шаги сценариев, рассылки |

## Потоки данных

1. **Оплата**: Payment Provider → webhook FastAPI → idempotency check (Redis) → создание Subscription → Celery: invite в группу + уведомление.
2. **Истечение подписки**: Celery beat (daily) → выборка expired → удаление из группы (Telegram API) → status=expired → уведомление.
3. **Сценарий**: Admin запускает → Bot отправляет шаги по JSON → переходы по кнопкам / отложенные шаги через Celery.

## Структура папок

```
telegram-subscription-bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── webhook_telegram.py
│   │   │   ├── webhook_payment.py
│   │   │   └── health.py
│   │   └── deps.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── loader.py        # bot, dp, storage
│   │   ├── handlers/
│   │   │   ├── user.py
│   │   │   ├── admin.py
│   │   │   └── scenarios.py
│   │   ├── middlewares/
│   │   │   ├── subscription.py
│   │   │   └── user_db.py
│   │   ├── keyboards.py
│   │   └── filters.py
│   ├── core/
│   │   ├── subscription.py  # логика подписки, invite
│   │   ├── payments.py      # idempotency, создание подписки
│   │   ├── scenarios.py     # движок сценариев
│   │   └── broadcast.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── subscription.py
│   │   │   ├── payment.py
│   │   │   ├── scenario.py
│   │   │   └── broadcast.py
│   │   └── repos/           # опционально, для сложной логики
│   ├── services/
│   │   ├── telegram_api.py  # invite link, kick from group
│   │   └── payment_provider.py  # абстракция платёжки
│   └── tasks/
│       ├── __init__.py
│       ├── celery_app.py
│       ├── subscription_expiry.py
│       ├── scenario_delayed.py
│       └── broadcast_tasks.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── ARCHITECTURE.md
```

## Безопасность и надёжность

- **Idempotency**: ключ `payment:{provider}:{external_id}` в Redis, TTL 24h.
- **Race conditions**: `SELECT ... FOR UPDATE` при продлении подписки (добавление к end_date).
- **Webhook secret**: проверка подписи от платёжной системы.
- **Роли**: admin / manager — проверка в filters для команд.
