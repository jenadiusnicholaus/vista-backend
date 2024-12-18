# Generated by Django 5.0.6 on 2024-07-11 22:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_verificationcode_code_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verificationcode',
            name='code_type',
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='verification_code', to=settings.AUTH_USER_MODEL),
        ),
    ]
