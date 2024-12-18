# Generated by Django 5.0.6 on 2024-07-22 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0007_rename_mymobilemoney_mymobilemoneypaymentinfos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mybookingpayment',
            name='payment_method',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='mypropertypurchasepayment',
            name='payment_method',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='myrentingpayment',
            name='payment_method',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='PaymentMethod',
        ),
    ]
