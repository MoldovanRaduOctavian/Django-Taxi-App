# Generated by Django 4.1.4 on 2022-12-22 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='driver',
            old_name='rider',
            new_name='driver',
        ),
    ]
