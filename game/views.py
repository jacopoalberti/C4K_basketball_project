from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from .models import Player, Shot, Zone
from django.http import JsonResponse

def index(request):
    return HttpResponse("Hello, this is the game app!")

def add_shot(request):
    players = Player.objects.all()
    zones = Zone.objects.all()

    if request.method == "POST":
        player_id = request.POST.get("player")
        zone_id = request.POST.get("zone")
        made = request.POST.get("result") == "make"
        name = request.POST.get("name")

        player = Player.objects.create(name=name)
        player = Player.objects.get(id=player_id)

        Shot.objects.create(
            player_id=player_id,
            zone_id=zone_id,
            made=made
        )

        return JsonResponse({
            "id": player.id,
            "name": player.name
        })


    return render(request, "add_shot.html", {
        "players": players,
        "zones": zones
    })