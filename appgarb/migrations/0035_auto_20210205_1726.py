# Generated by Django 3.1.5 on 2021-02-05 17:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0034_auto_20210203_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analitics',
            name='a_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 5, 17, 26, 43, 54197), verbose_name='Дата вывоза'),
        ),
        migrations.AlterField(
            model_name='containers',
            name='c_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 5, 6, 0), verbose_name='Дата измерения'),
        ),
        migrations.AlterField(
            model_name='modules',
            name='m_start',
            field=models.DateField(default=datetime.date(2021, 2, 5), verbose_name='Дата установки'),
        ),
    ]
