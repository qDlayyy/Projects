from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32, default=None, null=True)


class Plants(models.Model):

    LIGHTNING_TYPES = [
        ('darkness', 'Darkness'),
        ('moderate', 'Moderate'),
        ('daylight', 'Daylight')
    ]

    plant = models.CharField(max_length=50, null=False, blank=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=False)
    description = models.CharField(max_length=100, null=True, blank=True)
    lightning = models.CharField(max_length=8, choices=LIGHTNING_TYPES, default='Moderate')
    fertilizers = models.CharField(max_length=200, null=True, blank=True)
    watering_periods_days = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(1 )])
    last_watering_date = models.DateField(null=False, blank=False)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.plant


class Tips(models.Model):
    plant = models.ForeignKey(Plants, on_delete=models.CASCADE)
    tip = models.CharField(max_length=200)

    def __str__(self):
        return f'I would recomend to "{self.tip}" for {self.plant}.'


class Gallery(models.Model):
    plant = models.ForeignKey(Plants, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    state = models.CharField(max_length=20, null=False, blank=False)
    date = models.DateField(auto_created=True)


class Diary(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plants, on_delete=models.CASCADE)
    note = models.CharField(max_length=300, null=False, blank=False)

    def __str__(self):
        return f'Note for {self.plant}: {self.note}'
