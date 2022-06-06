from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'games'
    # def ready(self):
    #     from .models import Game2
    #     g = Game2.objects.all()
    #     for i in g:
    #         i.opponent_online = i.owner_online = False
    #         i.save()
    #     print("Resetting online statuses")
