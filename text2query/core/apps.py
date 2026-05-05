from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        try:
            from .services.extract_names import load_player_names
            load_player_names()
        except Exception:
            pass