# Generated by Django 3.1.5 on 2021-02-12 20:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0035_auto_20210205_1726'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='containers',
            options={'ordering': ['c_module', 'c_date', '-c_is_collected'], 'verbose_name': 'Контейнер', 'verbose_name_plural': 'Контейнеры'},
        ),
        migrations.AddField(
            model_name='containers',
            name='c_incr',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Суточный прирост, %'),
        ),
        migrations.AlterField(
            model_name='analitics',
            name='a_date',
            field=models.DateTimeField(default=datetime.date(2021, 2, 12), verbose_name='Дата вывоза'),
        ),
        migrations.AlterField(
            model_name='containers',
            name='c_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 12, 6, 0), verbose_name='Дата измерения'),
        ),
        migrations.AlterField(
            model_name='modules',
            name='m_start',
            field=models.DateField(default=datetime.date(2021, 2, 12), verbose_name='Дата установки'),
        ),
    ]
