from django.urls import path

from . import views

urlpatterns = [
 
    path('', views.index, name='index'),
    path('games', views.games, name='sneetch-games'),
    path('chess', views.game_chess, name='game-chess'),
    path('clicks', views.game_clicks, name='sneetch-game-clicks'),
    path('singleplay', views.game_ai, name='sneetch-game-chess'),
    path('profile/', views.profile.as_view(), name='profile'),




    # new chess stuff
    path('lobby', views.lobby, name='lobby'),
    path('newchess', views.multiplayerchess, name='new-game-chess'),
    path('game/<int:game_id>',  views.game, name = 'game'),
    path('single/',  views.single, name = 'single'),
    path('create/',  views.createGame.as_view(), name = 'create'),
    path('ongoing/',  views.ongoing, name = 'ongoing'),
]
