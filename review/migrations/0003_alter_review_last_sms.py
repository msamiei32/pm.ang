# Generated by Django 3.2 on 2024-07-07 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0002_alter_review_last_sms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='last_sms',
            field=models.CharField(default=1720358555.843058, max_length=100),
        ),
    ]