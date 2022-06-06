from django.urls import re_path
from django.urls import path

from . import consumers
# from games.consumers import NewChessConsumer, SingleConsumer
from games.consumers import NewChessConsumer

websocket_urlpatterns = [
    re_path(r'ws/game/clicks/$', consumers.ClicksConsumer.as_asgi()),
    # re_path(r'ws/game/chess/', consumers.SingleConsumer.as_asgi()),
    # re_path(r'game<str:game_id>', NewChessConsumer.as_asgi()),
    path(r'game/<int:game_id>', NewChessConsumer.as_asgi()),
    # path(r'game/<str:game_id>', NewChessConsumer.as_asgi()),
    # path(r'single/', SingleConsumer.as_asgi())
]
