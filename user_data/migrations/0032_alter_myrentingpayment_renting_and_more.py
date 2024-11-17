# Generated by Django 5.0.6 on 2024-08-11 14:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0031_alter_mybookingpayment_booking_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='myrentingpayment',
            name='renting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_data.myrenting'),
        ),
        migrations.AlterField(
            model_name='myrentingpayment',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]