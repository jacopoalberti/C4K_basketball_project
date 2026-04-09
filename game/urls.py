# Jacopo Alberti (eby3jn)

from django.urls import path

from . import views

urlpatterns = [
    path("", views.add_shot, name="add_shot"),
    path("stats/", views.get_stats, name="get_stats"),
    path("best_player/", views.get_best_player, name="get_best_player"),
    path("reset/", views.reset_session, name="reset_session"),
]