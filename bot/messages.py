# Команды бота
START_MESSAGE = """Привет! 🎉

Доступные команды:
/add_task - добавить новую задачу
/tasks - посмотреть все задачи
/edit_task - редактировать задачу
/delete_task - удалить задачу"""

# Сообщения диалога добавления задачи
TASK_NAME_PROMPT = "📝 Введите название задачи:"
TASK_DESCRIPTION_PROMPT = "📋 Введите описание задачи:"
TASK_CATEGORY_PROMPT = "🏷️ Введите категорию задачи (или - ):"
TASK_END_DATE_PROMPT = "⏰ Введите дату завершения в формате YYYY-MM-DD HH:mm (МСК):\n\nПример: 2025-10-20 14:30"  # noqa: E501

# Сообщения для редактирования и удаления задачи
SUCCESS_TASK_UPDATED = "✅ Задача успешно обновлена!"
SUCCESS_TASK_DELETED = "✅ Задача успешно удалена!"
TASK_UPDATE_CANCELLED = "❌ Редактирование задачи отменено"
TASK_DELETION_CANCELLED = "❌ Удаление задачи отменено"

# Сообщения об ошибках
ERROR_DATE_FORMAT = "❌ Неверный формат даты. Используйте YYYY-MM-DD HH:mm"
ERROR_FETCH_TASKS = "Не удалось получить задачи: {error}"
ERROR_CREATE_TASK = "❌ Ошибка при создании задачи: {error}"
ERROR_LOAD_TASK = "Ошибка загрузки задачи: {error}"
ERROR_UPDATE_TASK = "❌ Ошибка обновления: {error}"
ERROR_DELETE_TASK = "❌ Ошибка удаления: {error}"
ERROR_CREATE_CATEGORY = "❌ Ошибка при создании категории"
ERROR_CREATE_TASK_API = "❌ Ошибка при создании задачи: {error}"

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

# Тексты для диалогов
SELECT_TASK_EDIT = "📝 Выберите задачу для редактирования:"
SELECT_TASK_DELETE = "🗑️ Выберите задачу для удаления:"
EDIT_TASK_HEADER = "✏️ Редактирование задачи: {task_name}\n\nВыберите поле для редактирования:"  # noqa: E501
CONFIRM_DELETE = "❓ Вы уверены, что хотите удалить задачу:\n\n{task_name}\n\n{task_description}"  # noqa: E501

# Кнопки
BUTTON_BACK = "◀️ Назад"
BUTTON_CANCEL = "❌ Отменить"
BUTTON_EDIT_NAME = "📝 Название"
BUTTON_EDIT_DESCRIPTION = "📋 Описание"
BUTTON_EDIT_CATEGORY = "🏷️ Категория"
BUTTON_EDIT_END_DATE = "⏰ Дата завершения"
BUTTON_CONFIRM_DELETE = "✅ Да, удалить"
BUTTON_CANCEL_DELETE = "❌ Нет, отменить"

# Пустые значения
EMPTY_FIELD = "—"
EMPTY_DESCRIPTION = "Без описания"
NO_DESCRIPTION = "Без описания"
NO_CATEGORY = "—"
