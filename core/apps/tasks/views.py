"""
Документация:
https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
https://www.django-rest-framework.org/api-guide/permissions/#isauthenticatedorreadonly
https://django-filter.readthedocs.io/en/stable/
"""

from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response

from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для категорий."""

    # Базовый queryset для всех операци
    queryset = Category.objects.all()

    # Сериализатор для преобразования данных
    serializer_class = CategorySerializer

    # Разрешения: доступ разрешен всем пользователям
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Фильтрация по имени через параметр запроса."""

        queryset = Category.objects.all()
        name = self.request.query_params.get("name")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset


class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet для создания задачи и получения списка своих задач.

    Доступные endpoints:
    - GET /api/tasks/?user_telegram_id=123 - список задач пользователя
    - POST /api/tasks/ - создание новой задачи
    """

    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Отображение для пользователей своих задач.
        """
        queryset = Task.objects.select_related(
            "user",
            "category",
        )

        telegram_id = self.request.query_params.get("user_telegram_id")
        if telegram_id:
            return queryset.filter(user__username=f"tg_{telegram_id}")

        return queryset.none()

    def list(self, request, *args, **kwargs):
        """
        Переопределение list для обязательной фильтрации.
        """
        if not request.query_params.get("user_telegram_id"):
            return Response(
                {
                    "error": "Для доступа к задачам необходимо указать user_telegram_id",  # noqa: E501
                    "example": "/api/tasks/?user_telegram_id=123456789",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().list(request, *args, **kwargs)
