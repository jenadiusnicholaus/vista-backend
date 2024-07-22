# Generated by Django 5.0.6 on 2024-07-18 10:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0011_delete_myfavoriteproperty'),
        ('user_data', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='myfavoriteproperty',
            unique_together={('user', 'property')},
        ),
    ]