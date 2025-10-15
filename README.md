# Todo List Bot - Тестовое задание для бекенд-разработчика

📋 Сервис управления задачами (Todo List), работающий с  телеграм-ботом, основным бекендом на Django и связкой через API.

## 🏗️ Архитектура решения

### Стек технологий:
- **Backend**: Django, Django REST Framework
- **Bot**: Aiogram, Aiogram Dialog
- **Async Tasks**: Celery, Redis
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose

### 1. Клонируйте репозиторий и перейдите в директорию проекта:
```
git clone https://github.com/MaxBakshaev/todo-aiogram-bot.git
```
```
cd todo-aiogram-bot
```

### 2. Настройка переменных окружения:
Создайте файл .env в корне проекта:

SECRET_KEY=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DATABASE_URL=
TOKEN=
API_URL=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

### 3. Запуск проекта:
make bup

### 4. Проверка работы:

- Django API: http://localhost:8000/api/

- Admin Panel: http://localhost:8000/admin/

- Bot: Найти в Telegram по имени бота

### 📁 Структура проекта

```
project/
├── bot/                          # Telegram бот
│   ├── bot.py                   # Основной файл бота
│   ├── config.py                # Конфигурация и константы
│   └── messages.py              # Тексты сообщений
├── core/                        # Django проект
│   ├── apps/
│   │   └── tasks/               # Приложение задач
│   │       ├── models.py        # Модели Task и Category
│   │       ├── serializers.py   # Сериализаторы API
│   │       ├── views.py         # ViewSets и фильтры
│   │       ├── tasks.py         # Celery задачи
│   │       ├── signals.py       # Django сигналы
│   │       └── constants.py     # Константы и тексты
│   ├── project/
│   │   ├── settings.py          # Настройки Django
│   │   ├── celery.py            # Конфигурация Celery
│   │   └── urls.py              # Маршруты API
├── docker/
│   ├── docker-compose.yml       # Конфигурация Docker
│   ├── Dockerfile.django        # Образ Django
│   └── Dockerfile.bot           # Образ бота
└── .env                         # Переменные окружения
```

### Особенности реализации:

- PK моделей категорий и задач - id с хэшем
- Timezone Support: Все даты в America/Adak с конвертацией в UTC для Celery