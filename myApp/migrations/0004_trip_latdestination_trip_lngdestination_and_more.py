# Generated by Django 4.1.4 on 2022-12-25 20:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0003_trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='latDestination',
            field=models.FloatField(default=0.0, verbose_name='lat_destination'),
        ),
        migrations.AddField(
            model_name='trip',
            name='lngDestination',
            field=models.FloatField(default=0.0, verbose_name='lng_destination'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='lngClient',
            field=models.FloatField(default=0.0, verbose_name='lng_client'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='rider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='rider_id'),
        ),
        migrations.DeleteModel(
            name='Rider',
        ),
    ]
