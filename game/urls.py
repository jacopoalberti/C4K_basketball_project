# Jacopo Alberti (eby3jn)

from django.urls import path

from . import views

urlpatterns = [
    path("", views.add_shot, name="add_shot"),
    path("stats/", views.get_stats, name="get_stats"),
    path("best_player/", views.get_best_player, name="get_best_player"),
    path("reset/", views.reset_session, name="reset_session"),
    path("team/", views.team_page, name="team_page"),
    path("create-team/", views.create_team),
    path("team-shot/", views.add_team_shot),
    path("team-stats/", views.get_team_stats, name="team_stats"),
]