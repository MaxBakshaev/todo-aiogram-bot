"""
Документация:
https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
https://www.django-rest-framework.org/api-guide/permissions/#isauthenticatedorreadonly
"""

from rest_framework import viewsets
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """viewset для работы с задачами."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]


class TaskViewSet(viewsets.ModelViewSet):
    """viewset для работы с категориями."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
