# Generated by Django 5.0.6 on 2024-07-16 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='property_name',
        ),
    ]
