"""
Документация:
https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
https://www.django-rest-framework.org/api-guide/permissions/#isauthenticatedorreadonly
"""

from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
)
from rest_framework import viewsets, permissions

from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


class TaskFilter(FilterSet):
    user_telegram_id = CharFilter(method="filter_by_tg")

    def filter_by_tg(
        self,
        queryset,
        name,
        value,
    ):
        return queryset.filter(user__username=f"tg_{value}")

    class Meta:
        model = Task
        fields = [
            "user_telegram_id",
            "category",
        ]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related(
        "user",
        "category",
    ).all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
