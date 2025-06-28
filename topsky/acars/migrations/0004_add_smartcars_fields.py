# Generated manually for smartCARS API fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acars', '0003_add_acars_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='acarsmessage',
            name='message_type',
            field=models.CharField(default='ACARS', max_length=20, verbose_name='Typ wiadomości'),
        ),
        migrations.AddField(
            model_name='acarsmessage',
            name='departure_airport',
            field=models.CharField(blank=True, max_length=4, verbose_name='Lotnisko startu'),
        ),
        migrations.AddField(
            model_name='acarsmessage',
            name='arrival_airport',
            field=models.CharField(blank=True, max_length=4, verbose_name='Lotnisko lądowania'),
        ),
        migrations.AddField(
            model_name='acarsmessage',
            name='flight_time',
            field=models.CharField(blank=True, max_length=10, verbose_name='Czas lotu'),
        ),
        migrations.AddField(
            model_name='acarsmessage',
            name='distance',
            field=models.CharField(blank=True, max_length=10, verbose_name='Dystans'),
        ),
        migrations.AlterField(
            model_name='acarsmessage',
            name='payload',
            field=models.JSONField(blank=True, null=True, verbose_name='Pełne dane JSON'),
        ),
    ] 