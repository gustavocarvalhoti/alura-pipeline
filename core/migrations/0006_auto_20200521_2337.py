# Generated by Django 2.1.7 on 2020-05-22 02:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190325_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='created_at',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 5, 21, 23, 37, 53, 779732)),
        ),
    ]
