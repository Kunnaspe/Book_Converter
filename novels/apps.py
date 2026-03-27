from django.apps import AppConfig


class NovelsConfig(AppConfig):
    # Use bigautofield as the default so all auto-generated primary keys; use 64-bit integers and avoid integer overflow on large datasets
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'novels'
