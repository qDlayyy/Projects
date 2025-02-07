from django.contrib import admin
from .models import Profile, Plants, Tips, Gallery, Diary


admin.site.register([Profile, Plants, Tips, Gallery, Diary])
