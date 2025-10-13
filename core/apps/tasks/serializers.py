from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Category

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    creation_date = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "creation_date",
            "name",
        ]

    def get_creation_date(self, obj):
        """Возвращает значение первичного ключа (creation_date) категории."""

        return obj.pk


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач."""

    category = CategorySerializer(
        required=False,
        allow_null=True,
        read_only=True,
    )
    category_creation_date = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    user = serializers.StringRelatedField(read_only=True)
    user_telegram_id = serializers.IntegerField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "creation_date",
            "end_date",
            "category",
            "category_creation_date",
            "user",
            "user_telegram_id",
        ]
        read_only_fields = (
            "creation_date",
            "user",
            "category",
        )

    def create(self, validated_data):
        """
        СОЗДАЕТ НОВУЮ ЗАДАЧУ В БАЗЕ ДАННЫХ

        Что делает:
        1. Извлекает Telegram ID из входящих данных
        2. Создает или находит пользователя Django
        3. Связывает задачу с пользователем
        4. Сохраняет задачу в базу данных

        Параметры:
        - validated_data: Проверенные и валидированные данные от API

        Пример validated_data:
        {
            "name": "Купить молоко",
            "description": "Не забыть",
            "end_date": "2025-10-15T08:00:00-10:00",
            "user_telegram_id": 123456789,
            "category_id": "2025-10-15T08:00:00-10:00"
        }
        """

        tg_id = validated_data.pop("user_telegram_id")

        # Создание или получение пользователя с username в формате tg_123456
        user, _ = User.objects.get_or_create(
            username=f"tg_{tg_id}",
            defaults={"first_name": f"Telegram User {tg_id}"},
        )
        validated_data["user"] = user
        return super().create(validated_data)
