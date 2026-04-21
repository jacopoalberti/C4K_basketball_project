from django.http import HttpResponse
from django.shortcuts import render
from .models import Player, Shot, Zone, Team, TeamShot
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



def index(request):
    # Test endpoint to confirm server is running
    return HttpResponse("Hello, this is the game app!")


@csrf_exempt  # Disables CSRF protection
def add_shot(request):
    players = Player.objects.all()
    zones = Zone.objects.all()

    if request.method == "POST":
        try:
            # Get form data
            player_id = request.POST.get("player")
            new_player_name = request.POST.get("new_player")
            zone_id = request.POST.get("zone")
            made = request.POST.get("made") == "true"  # Convert string to boolean

            # Either create a new player OR fetch an existing one
            if new_player_name:
                player = Player.objects.create(name=new_player_name)
            else:
                player = Player.objects.get(id=player_id)

            # Only create a shot if zone is provided
            if zone_id:
                try:
                    zone = Zone.objects.get(id=zone_id)
                    # Save shot to database
                    Shot.objects.create(
                        player=player,
                        zone=zone,
                        made=made
                    )
                except Zone.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "Selected zone does not exist"}, status=400)

            return JsonResponse({"status": "ok", "player_id": player.id})  # Return success + player id
        # Catch-all exception
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    # GET request → render HTML page
    return render(request, "add_shot.html", {"players": players, "zones": zones})


def get_stats(request):
    player_id = request.GET.get("player")  # Get player filter from query params (?player=1)
    shots = Shot.objects.all()
    if player_id:
        try:
            # Filter shots for a specific player
            shots = shots.filter(player_id=int(player_id))
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid player ID"}, status=400)
    else:
        # No player → return empty list
        return JsonResponse([], safe=False)

    # Group shots by zone and calculate totals + made shots
    stats = (
        shots
        .values("zone__id", "zone__name")
        .annotate(
            total=Count("id"),
            made=Count("id", filter=Q(made=True))
        )
    )

    result = []

    total_attempts = sum(s["total"] for s in stats)  # Total attempts across all zones

    for s in stats:
        percentage = (s["made"] / s["total"]) * 100 if s["total"] > 0 else 0  # Avoid division by zero

        zone_id = s["zone__id"]

        # Assign point value based on zone
        if zone_id == 1:
            value = 1  # 1 point for shots in zone 1
        elif zone_id in [2, 3]:
            value = 2  # 2 points for shots in zone 2 and 3
        else:
            value = 3  # 3 points for all other zones

        points = s["made"] * value  # If shot is made convert it into points


        result.append({
            "zone_id": zone_id,
            "zone_name": s["zone__name"],
            "percentage": percentage,
            "points": points,
        })

    return JsonResponse({
        "zones": result,
        "total_attempts": total_attempts
    })


def get_best_player(request):
    best_player = None
    best_score = -1  # Start below any possible score

    # Iterate through all players
    for player in Player.objects.all():
        total = 0
        shots = Shot.objects.filter(player=player, made=True)  # Only count made shots

        for shot in shots:
            zone_id = shot.zone.id

            # Same scoring logic repeated
            if zone_id == 1:
                total += 1
            elif zone_id in [2, 3]:
                total += 2
            else:
                total += 3

        # Track the highest scoring player
        if total > best_score:
            best_score = total
            best_player = player

    # Return best player if it exists
    if best_player:
        return JsonResponse({
            "name": best_player.name,
            "points": best_score
        })

    # Fallback if no players exist
    return JsonResponse({
        "name": "None",
        "points": 0
    })


@csrf_exempt
def reset_session(request):
    if request.method == "POST":
        # Delete all data
        Shot.objects.all().delete()
        TeamShot.objects.all().delete()
        Team.objects.all().delete()
        Player.objects.all().delete()
        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


def team_page(request):
    # Load all necessary data for team UI
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

            team = Team.objects.create(name=name)  # Create team in database

            return JsonResponse({
                "status": "ok",
                "team_id": team.id,
                "name": team.name
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


def assign_player_to_team(request):
    if request.method == "POST":
        try:
            team_id = request.POST.get("team")
            player_id = request.POST.get("player")

            # Fetch objects from Database
            team = Team.objects.get(id=team_id)
            player = Player.objects.get(id=player_id)

            team.players.add(player)  # Many-to-many relationship

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


def get_team_members(request):
    try:
        team_id = request.GET.get("team")
        team = Team.objects.get(id=team_id)

        members = list(team.players.values("id", "name"))  # Convert queryset to a list of dicts for JSON

        return JsonResponse({
            "status": "ok",
            "members": members
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


def add_team_shot(request):
    if request.method == "POST":
        try:
            team_id = request.POST.get("team")
            zone_id = request.POST.get("zone")
            made = request.POST.get("made") == "true"

            team = Team.objects.get(id=team_id)
            zone = Zone.objects.get(id=zone_id)

            # Create team-based shot record
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
        return JsonResponse([], safe=False)  # If no team selected, return empty response

    try:
        team_id = int(team_id)
    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid team ID"}, status=400)

    shots = TeamShot.objects.filter(team_id=team_id)

    # Same pattern as player stats
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


def get_team_leaderboard(request):
    teams = Team.objects.all()

    result = []

    for team in teams:
        shots = TeamShot.objects.filter(team=team)

        total_points = 0

        # same scoring logic
        for s in shots:
            if s.made:
                if s.zone.id == 1:
                    total_points += 1
                elif s.zone.id in [2, 3]:
                    total_points += 2
                else:
                    total_points += 3

        result.append({
            "team_id": team.id,
            "team_name": team.name,
            "points": total_points
        })

    result = sorted(result, key=lambda x: x["points"], reverse=True)  # sort by number of points

    return JsonResponse(result, safe=False)
