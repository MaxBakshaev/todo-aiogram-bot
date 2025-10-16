"""
Документация:
https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
https://www.django-rest-framework.org/api-guide/permissions/#isauthenticatedorreadonly
https://django-filter.readthedocs.io/en/stable/
"""

from typing import Any
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
    mixins.ListModelMixin,  # ← добавляет list()
    mixins.UpdateModelMixin,  # ← добавляет update(), partial_update()
    mixins.DestroyModelMixin,  # ← добавляет destroy(), perform_destroy()
    viewsets.GenericViewSet,
):
    """
    ViewSet для создания задачи и получения списка своих задач.

    Доступные endpoints:
    - GET /api/tasks/?user_telegram_id=123 - список задач пользователя
    - POST /api/tasks/ - создание новой задачи
    - GET /api/tasks/{id}/ - получение конкретной задачи
    - PUT /api/tasks/{id}/ - полное обновление задачи
    - PATCH /api/tasks/{id}/ - частичное обновление задачи
    - DELETE /api/tasks/{id}/ - удаление задачи
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

    def list(self, request, *args, **kwargs) -> Response | Any:
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

    def retrieve(self, request, *args, **kwargs) -> Response:
        """Получение конкретной задачи с проверкой принадлежности."""
        instance = self.get_object()
        telegram_id = request.query_params.get("user_telegram_id")

        # Проверка, что задача принадлежит пользователю
        if telegram_id and instance.user.username != f"tg_{telegram_id}":
            return Response(
                {"error": "Задача не найдена или у вас нет прав доступа"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs) -> Response:
        """Обновление задачи с проверкой принадлежности."""
        instance = self.get_object()
        telegram_id = request.query_params.get("user_telegram_id")

        # Проверка принадлежности задачи
        if telegram_id and instance.user.username != f"tg_{telegram_id}":
            return Response(
                {"error": "Задача не найдена или у вас нет прав доступа"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs) -> Response:
        """
        Частичное обновление задачи с проверкой принадлежности.
        """
        instance = self.get_object()
        telegram_id = request.query_params.get("user_telegram_id")

        # Проверка принадлежности задачи
        if telegram_id and instance.user.username != f"tg_{telegram_id}":
            return Response(
                {"error": "Задача не найдена или у вас нет прав доступа"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        """Удаление задачи с проверкой принадлежности."""
        instance = self.get_object()
        telegram_id = request.query_params.get("user_telegram_id")

        # Проверка принадлежности задачи
        if telegram_id and instance.user.username != f"tg_{telegram_id}":
            return Response(
                {"error": "Задача не найдена или у вас нет прав доступа"},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        """Добавление user_telegram_id в контекст сериализатора."""

        context = super().get_serializer_context()
        context["user_telegram_id"] = self.request.query_params.get(
            "user_telegram_id",
        )
        return context
