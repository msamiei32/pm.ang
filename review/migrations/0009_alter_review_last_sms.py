# Generated by Django 3.2 on 2024-07-22 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0008_alter_review_last_sms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='last_sms',
            field=models.CharField(default=1721664740.6504705, max_length=100),
        ),
    ]