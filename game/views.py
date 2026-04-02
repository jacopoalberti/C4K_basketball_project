from django.http import HttpResponse
from django.shortcuts import render
from .models import Player, Shot, Zone
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



def index(request):
    return HttpResponse("Hello, this is the game app!")

@csrf_exempt
def add_shot(request):
    players = Player.objects.all()
    zones = Zone.objects.all()

    if request.method == "POST":
        try:
            player_id = request.POST.get("player")
            new_player_name = request.POST.get("new_player")
            zone_id = request.POST.get("zone")
            made = request.POST.get("made") == "true"

            if new_player_name:
                player = Player.objects.create(name=new_player_name)
            else:
                player = Player.objects.get(id=player_id)

            zone = Zone.objects.get(id=zone_id)

            Shot.objects.create(
                player=player,
                zone=zone,
                made=made
            )

            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return render(request, "add_shot.html", {"players": players, "zones": zones})


def get_stats(request):
    player_id = request.GET.get("player")
    shots = Shot.objects.all()
    if player_id:
        try:
            shots = shots.filter(player_id=int(player_id))
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid player ID"}, status=400)
    else:
        return JsonResponse([], safe=False)


    stats = (
        shots
        .values("zone__id", "zone__name")
        .annotate(
            total=Count("id"),
            made=Count("id", filter=Q(made=True))
        )
    )

    result = []

    for s in stats:
        percentage = (s["made"] / s["total"]) * 100 if s["total"] > 0 else 0

        zone_id = s["zone__id"]

        if zone_id == 1:
            value = 1
        elif zone_id in [2, 3]:
            value = 2
        else:
            value = 3

        points = s["made"] * value

        result.append({
            "zone_id": zone_id,
            "zone_name": s["zone__name"],
            "percentage": percentage,
            "points": points
        })

    return JsonResponse(result, safe=False)