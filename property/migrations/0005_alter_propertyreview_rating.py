# Generated by Django 5.0.6 on 2024-07-16 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0004_propertyfacility_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertyreview',
            name='rating',
            field=models.FloatField(),
        ),
    ]
