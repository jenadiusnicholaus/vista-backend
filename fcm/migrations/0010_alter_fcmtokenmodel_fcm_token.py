# Generated by Django 5.0.6 on 2024-08-04 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fcm', '0009_remove_fcmnotification_exchange_payload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fcmtokenmodel',
            name='fcm_token',
            field=models.CharField(max_length=1000),
        ),
    ]
