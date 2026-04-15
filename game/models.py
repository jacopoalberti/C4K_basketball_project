from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Zone(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Shot(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    made = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player} - {self.zone} - {'Made' if self.made else 'Missed'}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    players = models.ManyToManyField(Player)

    def __str__(self):
        return self.name


class TeamShot(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    made = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
