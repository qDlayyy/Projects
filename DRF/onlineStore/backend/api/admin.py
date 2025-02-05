from django.contrib import admin
from .models import Profile, Products, CartItem, Order, OrderedItems, Promocodes, StoreBase

admin.site.register(Profile)
admin.site.register([Products, CartItem, OrderedItems, Order, Promocodes, StoreBase])
