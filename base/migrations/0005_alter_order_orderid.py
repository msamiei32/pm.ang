# Generated by Django 3.2 on 2024-07-22 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_order_orderid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='orderId',
            field=models.CharField(max_length=50),
        ),
    ]