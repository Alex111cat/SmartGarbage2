# Generated by Django 3.1.5 on 2021-01-17 04:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0016_auto_20210117_0421'),
    ]

    operations = [
        migrations.AddField(
            model_name='modules',
            name='m_cont',
            field=models.PositiveSmallIntegerField(blank=True, default=100, verbose_name='Тип контейнера'),
        ),
        migrations.AlterField(
            model_name='containers',
            name='c_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 17, 4, 34, 45, 212770), verbose_name='Дата измерения'),
        ),
    ]
