# Generated by Django 5.0.6 on 2024-08-04 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fcm', '0005_alter_fcmtokenmodel_user_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fcmtokenmodel',
            options={'verbose_name': 'FCM Token', 'verbose_name_plural': 'FCM Tokens'},
        ),
        migrations.AlterUniqueTogether(
            name='fcmtokenmodel',
            unique_together=set(),
        ),
    ]