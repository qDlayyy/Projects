from django.contrib import admin
from .models import EmailVerification, Museums, Era, Authors, Categories, Exhibits

admin.site.register([EmailVerification, Museums, Era, Authors, Categories, Exhibits])
