# Generated by Django 5.0.6 on 2024-07-20 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0020_alter_delivergeoregion_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertyasproduct',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]