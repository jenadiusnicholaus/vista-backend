# Generated by Django 5.0.6 on 2024-07-23 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0010_mypaymentcard_bank_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='mybookingpayment',
            name='transaction_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]