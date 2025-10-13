"""
Документация:
https://www.django-rest-framework.org/api-guide/routers/
"""

from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, TaskViewSet

app_name = "tasks"

router = DefaultRouter()

router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = router.urls
