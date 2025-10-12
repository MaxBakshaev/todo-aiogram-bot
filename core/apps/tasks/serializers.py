from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class TaskSerializer(serializers.ModelSerializer):
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
