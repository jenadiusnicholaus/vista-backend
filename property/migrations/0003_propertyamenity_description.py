# Generated by Django 5.0.6 on 2024-07-16 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0002_remove_property_property_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyamenity',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
