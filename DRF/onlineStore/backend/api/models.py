from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class StoreBase(models.Model):
    name = models.CharField(max_length=20, unique=True, null=False, default='Admin')
    cashback_access_from = models.DecimalField(max_digits=7, decimal_places=2, default=300, validators=[MinValueValidator(Decimal(0))])
    cashback_percentage = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(99)])


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, null=False, blank=False)
    is_subscribed = models.BooleanField(default=False)
    cashback = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    token = models.CharField(max_length=32, blank=True, null=True)


class Products(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount_percentage = models.IntegerField(default=0)


    def __str__(self):
        return self.name
    

    def get_final_price(self):
        discount = self.price * self.discount_percentage / 100
        return round(self.price - discount, 2)


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return f'{self.item} * {self.quantity} for {self.user.username}.'


class OrderedItems(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.item} * {self.quantity} for {self.user.username}.'
    

class Order(models.Model):

    NOTIFICATION_CHOICES = [
        ('1h', 'An Hour Before'),
        ('6h', '6 Hours Before'),
        ('24h', '24 Hours Before'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(null=False)
    orders = models.ManyToManyField(OrderedItems)
    address = models.CharField(max_length=255, null=False)
    notification_time = models.CharField(max_length=3, choices=NOTIFICATION_CHOICES, default='1h')
    price = models.DecimalField(max_digits=7, decimal_places=2)


class Promocodes(models.Model):
    code = models.CharField(max_length=6, null=False, unique=True)
    sale_percentage = models.IntegerField(null=False, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_active = models.BooleanField(default=False)
    summarizes_with_other_sales = models.BooleanField(default=False)


    def __str__(self):
        return self.code