# Generated by Django 5.0.6 on 2024-07-20 15:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0014_supportedgeoregions_alter_property_business_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='supported_geo_region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supported_geo_region', to='property.supportedgeoregions'),
        ),
    ]
