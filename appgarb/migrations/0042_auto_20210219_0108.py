# Generated by Django 3.1.6 on 2021-02-19 01:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0041_remove_analitics_a_average'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analitics',
            name='a_date',
            field=models.DateTimeField(default=datetime.date(2021, 2, 19), verbose_name='Дата вывоза'),
        ),
        migrations.AlterField(
            model_name='containers',
            name='c_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 19, 6, 0), verbose_name='Дата измерения'),
        ),
        migrations.AlterField(
            model_name='modules',
            name='m_start',
            field=models.DateField(default=datetime.date(2021, 2, 19), verbose_name='Дата установки'),
        ),
    ]
