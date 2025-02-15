from django.contrib import admin
from .models import User, EmailVerification, Cinemas, Sessions, Actors, Directors, Tickets, Genres, Films

admin.site.register([EmailVerification, Cinemas, Sessions, Actors, Directors, Tickets, Genres, Films])

# Register your models here.
