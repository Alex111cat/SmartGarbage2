# Generated by Django 3.1.4 on 2021-01-20 21:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0023_auto_20210120_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analitics',
            name='a_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 20, 21, 16, 33, 887668), verbose_name='Дата вывоза'),
        ),
        migrations.AlterField(
            model_name='containers',
            name='c_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 20, 6, 0), verbose_name='Дата измерения'),
        ),
    ]
