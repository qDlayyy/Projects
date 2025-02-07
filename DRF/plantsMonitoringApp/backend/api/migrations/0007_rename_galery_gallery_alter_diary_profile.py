# Generated by Django 5.1.6 on 2025-02-06 23:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_galery_image'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Galery',
            new_name='Gallery',
        ),
        migrations.AlterField(
            model_name='diary',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.profile'),
        ),
    ]
