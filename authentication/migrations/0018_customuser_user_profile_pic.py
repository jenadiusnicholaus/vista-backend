# Generated by Django 5.0.6 on 2024-07-14 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_customuser_agreed_to_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='user_profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
