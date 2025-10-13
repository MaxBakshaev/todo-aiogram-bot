START_MESSAGE = """
Привет! 🎉

Доступные команды:
/add_task - добавить новую задачу
/tasks - посмотреть все задачи
"""

# Сообщения процесса добавления задачи
ADD_TASK_NAME = "Отправь название задачи:"
ADD_TASK_DESCRIPTION = "Отправь описание задачи:"
ADD_TASK_CATEGORY = "Укажи категорию (или напиши «пропустить»):"
ADD_TASK_END_DATE = (
    "Отправь дату завершения в формате YYYY-MM-DD HH:mm (America/Adak):"
)

# Сообщения об ошибках
ERROR_DATE_FORMAT = (
    "Неверный формат. Нужен YYYY-MM-DD HH:mm. Попробуй ещё раз:"
)
ERROR_FETCH_TASKS = "Не удалось получить задачи: {error}"
ERROR_CREATE_TASK = "Ошибка при создании задачи: {status}\n{details}"
ERROR_CONNECTION = "Ошибка соединения с сервером: {error}"
ERROR_READ_RESPONSE = "Не удалось прочитать ответ сервера"

# Сообщения об успехе
SUCCESS_TASK_CREATED = "Задача «{task_name}» успешно создана! ✅"
SUCCESS_NO_TASKS = "У вас нет задач. 🎉"

# Форматы задач
TASK_LIST_HEADER = "📋 Ваши задачи:\n\n"
TASK_FORMAT = """
📌 Задача: {name}
📃 Описание: {description}
🔖 Категория: {category}
🕒 Дата создания: {created_date}
🔥 Дата завершения: {end_date}
"""

# Пустые значения
EMPTY_FIELD = "—"
EMPTY_DESCRIPTION = "Без описания"
