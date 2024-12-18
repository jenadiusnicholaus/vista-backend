# Generated by Django 5.0.6 on 2024-07-16 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0005_alter_propertyreview_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='currency',
            field=models.CharField(choices=[('Tsh', 'Tsh'), ('USD', 'USD'), ('Ksh', 'Ksh'), ('EUR', 'EUR')], default='Tsh', max_length=10),
        ),
        migrations.AddField(
            model_name='property',
            name='period',
            field=models.CharField(choices=[('night', 'Night'), ('minute', 'Minute'), ('hour', 'Hour'), ('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], default='night', max_length=10),
        ),
    ]
