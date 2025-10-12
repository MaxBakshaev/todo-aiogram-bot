"""
Документация:
https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
"""

from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Управление категориями."""

    # Поля, отображаемые в списке
    list_display = [
        "id",
        "name",
    ]

    # Поиск по полям
    search_fields = [
        "name",
    ]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Управление задачами."""

    # Поля, отображаемые в списке
    list_display = [
        "id",
        "name",
        "description",
        "creation_date",
        "end_date",
        "category",
        "user",
    ]

    # Фильтрация по полям
    list_filter = [
        "creation_date",
        "end_date",
        "category",
        "user",
    ]

    # Поиск по полям
    search_fields = [
        "name",
        "description",
    ]

    # Фильтрация по дате создания
    date_hierarchy = "creation_date"

    # Поля для создания и редактирования задачи
    fields = [
        "name",
        "description",
        "creation_date",
        "end_date",
        "category",
        "user",
    ]

    # Поля только для чтения
    readonly_fields = [
        "user",
    ]
