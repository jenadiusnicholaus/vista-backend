# Generated by Django 5.0.6 on 2024-07-11 23:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_customuser_llogin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='llogin',
        ),
    ]
