# Generated by Django 5.0.6 on 2024-07-25 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0023_myrenting_renting_duration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myrentingstatus',
            old_name='renting_canceled',
            new_name='renting_request_confirmed',
        ),
        migrations.RemoveField(
            model_name='myrentingstatus',
            name='renting_confirmed',
        ),
        migrations.RemoveField(
            model_name='myrentingstatus',
            name='renting_started',
        ),
        migrations.AddField(
            model_name='myrentingstatus',
            name='renting_status',
            field=models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='ongoing', max_length=100),
        ),
    ]
