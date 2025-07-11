# Generated by Django 5.2.3 on 2025-06-29 10:17

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
            name='SmartcarsProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(blank=True, max_length=64, unique=True)),
                ('acars_token', models.CharField(blank=True, max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='smartcars_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SmartCARS Profile',
                'verbose_name_plural': 'SmartCARS Profiles',
                'db_table': 'acars_smartcars_profile',
            },
        ),
    ]
