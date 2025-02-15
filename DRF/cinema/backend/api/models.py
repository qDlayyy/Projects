import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (self.created_at + timedelta(days=1)) > timezone.now()
    

class Cinemas(models.Model):
    name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.name


class Actors(models.Model):
    name = models.CharField(max_length=20, null=False)
    surname = models.CharField(max_length=20, null=False)
    photo = models.ImageField(upload_to='actors/', blank=False, null=False)

    def __str__(self):
        return self.surname


class Directors(models.Model):
    name = models.CharField(max_length=20, null=False)
    surname = models.CharField(max_length=20, null=False)
    photo = models.ImageField(upload_to='directors/', blank=False, null=False)

    def __str__(self):
        return self.surname
    

class Genres(models.Model):
    genre = models.CharField(max_length=15, null=False)


class Films(models.Model):
    name = models.CharField(max_length=150, null=False)
    description = models.CharField(max_length=200, null=False)
    actors = models.ManyToManyField(Actors, related_name='films_by_actor')
    director = models.ForeignKey(Directors, on_delete=models.CASCADE)
    genres = models.ManyToManyField(Genres, related_name='films_by_genre')
    duration_mins = models.IntegerField(null=False)
    image = models.ImageField(upload_to='films/', blank=False, null=False)

    def __str__(self):
        return self.name


class Sessions(models.Model):
    name = models.CharField(max_length=100, null=False)
    cinema = models.ForeignKey(Cinemas, on_delete=models.CASCADE, null=False)
    film = models.ForeignKey(Films, on_delete=models.CASCADE)
    time = models.TimeField(null=False)

    def __str__(self):
        return self.name


class Tickets(models.Model):
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    seat = models.CharField(max_length=3, null=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.seat
