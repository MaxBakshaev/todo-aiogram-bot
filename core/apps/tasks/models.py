"""
Документация:
https://docs.djangoproject.com/en/5.2/topics/db/models/
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .utils import generate_content_based_id


class Category(models.Model):
    """Категория."""

    id = models.CharField(
        primary_key=True,
        max_length=16,
        editable=False,
        default=generate_content_based_id,
        verbose_name="ID",
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
        db_index=True,
    )
    name = models.CharField(
        verbose_name="Категория",
        max_length=32,
        unique=True,
    )

    class Meta:
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    """Задача."""

    id = models.CharField(
        primary_key=True,
        max_length=16,
        editable=False,
        default=generate_content_based_id,
        verbose_name="ID",
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=128,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
        db_index=True,
    )
    end_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата завершения",
    )
    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Напоминание отправлено",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="tasks",
        # нет жесткой привязки к категории
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        ordering = ("-creation_date",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Возвращает строковое представление задачи,
        включая название и дату завершения.

        Пример: "Завершить ТЗ до 18:00, 15.10.2025"
        """
        return f'{self.name} до {self.end_date.strftime("%H:%M, %d.%m.%Y")}'
