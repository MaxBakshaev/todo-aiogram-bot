"""
Документация:
https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
"""

from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Task."""

    category = CategorySerializer()
    user = serializers.StringRelatedField()

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "creation_date",
            "end_date",
            "category",
            "user",
        ]
