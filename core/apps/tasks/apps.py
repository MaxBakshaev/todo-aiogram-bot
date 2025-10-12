from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.apps.tasks"

    def ready(self):
        import core.apps.tasks.signals  # noqa: F401
