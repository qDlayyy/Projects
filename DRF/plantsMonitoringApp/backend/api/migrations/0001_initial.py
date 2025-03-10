# Generated by Django 5.1.6 on 2025-02-06 13:55

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Plants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateField(auto_created=True)),
                ('plant', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('lightning', models.CharField(choices=[('darkness', 'Darkness'), ('moderate', 'Moderate lightning'), ('daylight', 'Daylight')], default='moderate', max_length=8)),
                ('fertilizers', models.CharField(blank=True, max_length=200, null=True)),
                ('watering_periods_days', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('last_watering_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Galery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_created=True)),
                ('image', models.ImageField(upload_to='')),
                ('state', models.CharField(max_length=20)),
                ('plant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plants')),
            ],
        ),
        migrations.CreateModel(
            name='Diary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(max_length=300)),
                ('plant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plants')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=None, max_length=32)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='plants',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.profile'),
        ),
        migrations.CreateModel(
            name='Tips',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tip', models.CharField(max_length=200)),
                ('plant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plants')),
            ],
        ),
    ]
