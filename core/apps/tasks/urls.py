"""
Документация:
https://www.django-rest-framework.org/api-guide/routers/
"""

from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, TaskViewSet

app_name = "tasks"

router = DefaultRouter()

router.register(r"categories", CategoryViewSet)
router.register(r"tasks", TaskViewSet)

urlpatterns = router.urls
