# Generated by Django 3.2 on 2024-07-22 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0007_alter_review_last_sms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='last_sms',
            field=models.CharField(default=1721664556.4693918, max_length=100),
        ),
    ]
