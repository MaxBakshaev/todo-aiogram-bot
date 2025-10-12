"""
Документация:
https://docs.djangoproject.com/en/5.2/topics/db/models/
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Категория."""

    name = models.CharField(
        verbose_name="Категория",
        max_length=32,
        unique=True,
    )

    class Meta:
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    """Задача."""

    name = models.CharField(
        verbose_name="Название",
        max_length=128,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    creation_date = models.DateField(
        default=timezone.now,
        verbose_name="Дата создания",
    )
    end_date = models.DateField(
        default=timezone.now,
        verbose_name="Дата завершения",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="tasks",
        # нет жесткой привязки к категории
        on_delete=models.SET_NULL,
        null=True,
    )

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="tasks",
        # жесткая привязка к пользователю
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Задачу"
        verbose_name_plural = "Задачи"
        ordering = ("-id",)

    def __str__(self):
        """
        Возвращает строковое представление задачи,
        включая название и дату завершения.

        Пример: "Завершить ТЗ до 15.10.2025"
        """
        return f"{self.name} до {self.end_date}"
