# Generated by Django 5.0.6 on 2024-08-04 14:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fcm', '0002_fcmdevice_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FcmNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('data', models.TextField()),
                ('device_registration_token', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fcm_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FcmTokenModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fcm_token', models.CharField(max_length=255)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('is_stale', models.BooleanField(default=False)),
                ('stale_time', models.CharField(choices=[('1', '1 Day'), ('3', '3 Days'), ('7', '1 Week'), ('14', '2 Weeks'), ('30', '1 Month'), ('90', '3 Months'), ('180', '6 Months'), ('365', '1 Year')], default='30', max_length=255)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fcm_tokens', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='FcmDevice',
        ),
    ]
