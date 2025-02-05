# Generated by Django 5.1.5 on 2025-02-03 22:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_storebase_cashback_access_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storebase',
            name='cashback_percentage',
            field=models.IntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)]),
        ),
    ]
