import uuid
from django.db import models
from django.contrib.auth.models import User


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Museums(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Era(models.Model):
    name = models.CharField(max_length=30)
    century_of_beginning = models.IntegerField()
    century_of_ending = models.IntegerField()

    def __str__(self):
        return self.name


class Authors(models.Model):
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30, null=True, blank=True)
    era = models.ForeignKey(Era, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='authors', null=True, blank=True)

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Exhibits(models.Model):
    name = models.CharField(max_length=30)
    museum = models.ForeignKey(Museums, on_delete=models.CASCADE)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    category = models.ManyToManyField(Categories)
    photo = models.ImageField(upload_to='exhibits/')

    def __str__(self):
        return self.name

