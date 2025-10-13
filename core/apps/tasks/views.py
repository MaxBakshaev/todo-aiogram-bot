"""
Документация:
https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
https://www.django-rest-framework.org/api-guide/permissions/#isauthenticatedorreadonly
https://django-filter.readthedocs.io/en/stable/
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
    """Фильтр для задач."""

    user_telegram_id = CharFilter(method="filter_by_tg")

    def filter_by_tg(
        self,
        queryset,
        name,
        value,
    ):
        """Возвращает отфильтрованный queryset задач пользователя"""

        return queryset.filter(user__username=f"tg_{value}")

    class Meta:
        model = Task
        fields = [
            "user_telegram_id",
            "category",
        ]


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для категорий."""

    # Базовый queryset для всех операци
    queryset = Category.objects.all()

    # Сериализатор для преобразования данных
    serializer_class = CategorySerializer

    # Разрешения: доступ разрешен всем пользователям
    permission_classes = [permissions.AllowAny]

    # Бэкенды фильтрации
    filter_backends = [DjangoFilterBackend]

    # Поля, по которым доступна фильтрация
    filterset_fields = ["name"]


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для задач."""

    # Queryset с оптимизацией через select_related
    queryset = Task.objects.select_related(
        "user",
        "category",
    ).all()

    # Сериализатор для преобразования данных задачи
    serializer_class = TaskSerializer

    # Разрешения: доступ разрешен всем пользователям
    permission_classes = [permissions.AllowAny]

    # Бэкенды фильтрации
    filter_backends = [DjangoFilterBackend]

    # Кастомный класс фильтра для задач
    filterset_class = TaskFilter
