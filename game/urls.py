# Jacopo Alberti (eby3jn)

from django.urls import path

from . import views

urlpatterns = [
    path("", views.add_shot, name="add_shot"),
]