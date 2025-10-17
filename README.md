### 📋 <b>"ToDoAiogramBot"</b> - сервис для управления задачами и отправки напоминаний, связанный с телеграм-ботом.

## 🛠️ Используемые технологии

- **Бэкенд**: Django, Django REST Framework
- **Телеграм-бот**: Aiogram, Aiogram Dialog
- **Очередь задач**: Celery, Redis
- **СУБД**: PostgreSQL
- **Контейнеризация**: Docker, Docker Compose

## ⚙️ Эндпоинты

### 🔸 Категории
- `GET /api/categories` — список всех вопросов

### 🔸 Ответы (`Answers`)
- GET /api/tasks/?user_telegram_id=123 - список задач пользователя
- POST /api/tasks/ - создание новой задачи
- GET /api/tasks/{id}/ - получение конкретной задачи
- PUT /api/tasks/{id}/ - полное обновление задачи
- PATCH /api/tasks/{id}/ - частичное обновление задачи
- DELETE /api/tasks/{id}/ - удаление задачи


## ⚙️ Установка и запуск:

### 🔹 1. Клонируйте репозиторий и перейдите в директорию проекта:
```
git clone https://github.com/MaxBakshaev/todo-aiogram-bot.git
```
```
cd todo-aiogram-bot
```

### 🔹 2. Создайте файл `.env`.

Для Windows:
```
type nul > .env
```

Для Linux или macOS:
```
touch .env
```

### 🔹 3. Настройте переменные окружения:

3.1. 🔑 Сгенерируйте секретный ключ и добавьте в SECRET_KEY
```
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
3.2. ✏️ Замените на ваши значения в POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, DATABASE_URL:

- `user` — имя пользователя БД
- `pwd` — пароль
- `DBname` — название БД

3.3. По ссылке: https://t.me/botfather создайте бота, получите токен и добавьте в TOKEN

```
SECRET_KEY=ваш_секретный_ключ
POSTGRES_DB=DBname
POSTGRES_USER=user
POSTGRES_PASSWORD=pwd
DATABASE_URL=postgres://user:pwd@postgres:5432/DBname
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
TOKEN=токен_вашего_телеграм_бота
API_URL=http://django:8000/api
```

### 🔹 4. Запуск контейнеров:

Убедитесь, что Docker Desktop запущен. Затем создайте и запустите докер контейнеры:
```
make up
```
Остановить:
```
make stop
```
Очистить контейнеры, сети, тома и образы:
```
make clean
```

- 📄 Дополнительные команды смотрите в `Makefile`.

### 🔹 5. Для проверки работы откройте в браузере:

- Django API: http://localhost:8000/api/
- Администрирование Django: http://localhost:8000/admin/
- Телеграм-бот: http://t.me/название_вашего_бота/

## 💬 Команды телеграм-бота:

- /start - начало работы с ботом
- /tasks - показать список задач
- /add_task - добавить задачу