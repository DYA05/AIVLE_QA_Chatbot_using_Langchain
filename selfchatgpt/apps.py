from django.db.models.signals import post_migrate
from django.apps import AppConfig


class SelfchatgptConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'selfchatgpt'

    def ready(self):
        from .models import ChromaDB
        post_migrate.connect(ChromaDB.add_initial_data, sender=self)

