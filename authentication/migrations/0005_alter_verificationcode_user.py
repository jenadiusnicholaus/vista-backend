# Generated by Django 5.0.6 on 2024-07-11 22:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_verificationcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationcode',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_code', to=settings.AUTH_USER_MODEL),
        ),
    ]
