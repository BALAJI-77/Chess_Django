from django.urls import path
from . import views

urlpatterns = [
    path('play', views.play, name='return_ai_move'),
    path('play_stockfish', views.play_stockfish,
         name='return_ai_move_stockfish'),
    path('play_random', views.play_random, name='return_ai_move_random'),
    path('validate', views.validate, name='return_validate'),
    path('move_validate', views.move_validate, name='return_move_validate'),
    path('fen', views.fen, name='return_fen'),
    path('move_count', views.move_count, name='return_move_count'),
    path('total_count', views.total_count, name='return_total_count'),
    path('score', views.score, name='return_score'),
    path('current_score', views.current_score, name='return_current_score'),
    path('getcount', views.getcount, name='return_getcount'),
    path('DualPlayer_current_score', views.DualPlayer_current_score, name ='return_DualPlayer_current_score'),
    path('DualPlayerScore', views.DualPlayerScore, name ='return_DualPlayerScore'),
    path('getCurrent_count', views.getCurrent_count, name='return_getCurrent_count'),
]
