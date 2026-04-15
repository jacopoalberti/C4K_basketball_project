from django.http import HttpResponse
from django.shortcuts import render
from .models import Player, Shot, Zone, Team, TeamShot
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

            if zone_id:
                try:
                    zone = Zone.objects.get(id=zone_id)
                    Shot.objects.create(
                        player=player,
                        zone=zone,
                        made=made
                    )
                except Zone.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "Selected zone does not exist"}, status=400)

            return JsonResponse({ "status": "ok", "player_id": player.id })
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


def get_best_player(request):
    best_player = None
    best_score = -1

    for player in Player.objects.all():
        total = 0
        shots = Shot.objects.filter(player=player, made=True)

        for shot in shots:
            zone_id = shot.zone.id

            if zone_id == 1:
                total += 1
            elif zone_id in [2, 3]:
                total += 2
            else:
                total += 3

        if total > best_score:
            best_score = total
            best_player = player

    if best_player:
        return JsonResponse({
            "name": best_player.name,
            "points": best_score
        })

    return JsonResponse({
        "name": "None",
        "points": 0
    })


@csrf_exempt
def reset_session(request):
    if request.method == "POST":
        Shot.objects.all().delete()
        for team in Team.objects.all():
            team.players.clear()
        Player.objects.all().delete()
        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


def team_page(request):
    teams = Team.objects.all()
    zones = Zone.objects.all()
    players = Player.objects.all()

    return render(request, "team.html", {
        "teams": teams,
        "zones": zones,
        "players": players
    })


def create_team(request):
    if request.method == "POST":
        try:
            name = request.POST.get("name")

            if not name:
                return JsonResponse({"status": "error", "message": "Name required"}, status=400)

            team = Team.objects.create(name=name)

            return JsonResponse({
                "status": "ok",
                "team_id": team.id,
                "name": team.name
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


def add_team_shot(request):
    if request.method == "POST":
        try:
            team_id = request.POST.get("team")
            zone_id = request.POST.get("zone")
            made = request.POST.get("made") == "true"

            team = Team.objects.get(id=team_id)
            zone = Zone.objects.get(id=zone_id)

            TeamShot.objects.create(
                team=team,
                zone=zone,
                made=made
            )

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


def get_team_stats(request):
    team_id = request.GET.get("team")

    if not team_id:
        return JsonResponse([], safe=False)

    try:
        team_id = int(team_id)
    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid team ID"}, status=400)

    shots = TeamShot.objects.filter(player_team_id=team_id)

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
