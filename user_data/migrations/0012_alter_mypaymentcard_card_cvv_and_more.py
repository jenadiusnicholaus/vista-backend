# Generated by Django 5.0.6 on 2024-07-24 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0011_mybookingpayment_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mypaymentcard',
            name='card_cvv',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='mypaymentcard',
            name='card_expiry',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]