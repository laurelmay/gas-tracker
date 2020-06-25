# Generated by Django 3.0.2 on 2020-01-24 04:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0007_car_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='nickname',
            field=models.CharField(max_length=90, null=True, validators=[django.core.validators.RegexValidator('\\S+')]),
        ),
    ]