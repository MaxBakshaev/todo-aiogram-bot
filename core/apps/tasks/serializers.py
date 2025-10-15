"""
Документация:
https://www.django-rest-framework.org/api-guide/serializers/
https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Category

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    class Meta:
        model = Category
        fields = [
            "id",
            "creation_date",
            "name",
        ]


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для задач.

    Документация для полей:
    https://www.django-rest-framework.org/api-guide/fields/
    """

    category = CategorySerializer(
        required=False,
        allow_null=True,
        read_only=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
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
            "id",
            "name",
            "description",
            "creation_date",
            "end_date",
            "category",
            "category_id",
            "user",
            "user_telegram_id",
        ]
        read_only_fields = (
            "id",
            "creation_date",
            "user",
            "category",
        )

    def create(self, validated_data):
        """
        Создает задачу и связывает с пользователем по Telegram ID.

        Документация:
        https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
        """

        tg_id = validated_data.pop("user_telegram_id")

        # Создание или получение пользователя с username в формате tg_123456
        user, _ = User.objects.get_or_create(
            username=f"tg_{tg_id}",
            defaults={"first_name": f"Telegram User {tg_id}"},
        )
        validated_data["user"] = user
        return super().create(validated_data)
