# Generated by Django 3.1.4 on 2021-01-20 17:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0021_auto_20210120_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analitics',
            name='a_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 20, 17, 48, 20, 385758), verbose_name='Дата вывоза'),
        ),
        migrations.AlterField(
            model_name='containers',
            name='c_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 20, 17, 48, 20, 384759), verbose_name='Дата измерения'),
        ),
    ]
