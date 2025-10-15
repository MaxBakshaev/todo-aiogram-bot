# Команды бота
START_MESSAGE = """Привет! 🎉

Доступные команды:
/add_task - добавить новую задачу
/tasks - посмотреть все задачи"""

# Сообщения диалога добавления задачи
TASK_NAME_PROMPT = "📝 Введите название задачи:"
TASK_DESCRIPTION_PROMPT = "📋 Введите описание задачи:"
TASK_CATEGORY_PROMPT = "🏷️ Введите категорию задачи (или - ):"
TASK_END_DATE_PROMPT = "⏰ Введите дату завершения в формате YYYY-MM-DD HH:mm ({timezone}):\n\nПример: 2025-10-20 14:30"  # noqa: E501

# Сообщения об ошибках
ERROR_DATE_FORMAT = "❌ Неверный формат даты. Используйте YYYY-MM-DD HH:mm"
ERROR_FETCH_TASKS = "Не удалось получить задачи: {error}"
ERROR_CREATE_TASK = "❌ Ошибка при создании задачи: {error}"

# Сообщения об успехе
SUCCESS_TASK_CREATED = "✅ Задача успешно создана!"
SUCCESS_NO_TASKS = "У вас нет задач. 🎉"
TASK_CREATION_CANCELLED = "❌ Создание задачи отменено"

# Форматы задач
TASK_LIST_HEADER = "📋 Ваши задачи:\n\n"
TASK_FORMAT = """📌 Задача: {name}
📃 Описание: {description}
🔖 Категория: {category}
🕒 Дата создания: {created_date}
🔥 Дата завершения: {end_date}"""

# Пустые значения
EMPTY_FIELD = "—"
EMPTY_DESCRIPTION = "Без описания"

# Кнопки
BUTTON_BACK = "◀️ Назад"
BUTTON_CANCEL = "❌ Отменить"
