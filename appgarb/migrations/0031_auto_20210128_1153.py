# Generated by Django 3.1.5 on 2021-01-28 11:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0030_auto_20210128_1148'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='containers',
            options={'ordering': ['c_module', 'c_date'], 'verbose_name': 'Контейнер', 'verbose_name_plural': 'Контейнеры'},
        ),
        migrations.AlterField(
            model_name='analitics',
            name='a_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 28, 11, 53, 2, 851718), verbose_name='Дата вывоза'),
        ),
        migrations.AlterUniqueTogether(
            name='containers',
            unique_together={('c_module', 'c_date', 'c_is_collected')},
        ),
    ]
