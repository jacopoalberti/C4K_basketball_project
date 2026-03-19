from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Player, Shot

def index(request):
    return HttpResponse("Hello, this is the game app!")

def add_shot(request):
    if request.method == "POST":
        player_id = request.POST.get("player")
        zone = request.POST.get("zone")
        is_make = request.POST.get("result") == "make"

        player = Player.objects.get(id=player_id)

        Shot.objects.create(
            player=player,
            zone=zone,
            is_make=is_make
        )

        return redirect("dashboard")

    players = Player.objects.all()
    return render(request, "add_shot.html", {"players": players})