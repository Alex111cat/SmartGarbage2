# Generated by Django 3.1.5 on 2021-02-23 01:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0042_auto_20210219_0108'),
    ]

    operations = [
        migrations.CreateModel(
            name='Methods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('me_methods', models.CharField(db_index=True, max_length=30, unique=True, verbose_name='Название метода')),
            ],
            options={
                'verbose_name': 'Метод',
                'verbose_name_plural': 'Методы',
                'ordering': ['me_methods'],
            },
        ),
        migrations.AlterField(
            model_name='analitics',
            name='a_date',
            field=models.DateTimeField(default=datetime.date(2021, 2, 23), verbose_name='Дата вывоза'),
        ),
        migrations.AlterField(
            model_name='containers',
            name='c_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 23, 6, 0), verbose_name='Дата измерения'),
        ),
        migrations.AlterField(
            model_name='modules',
            name='m_start',
            field=models.DateField(default=datetime.date(2021, 2, 23), verbose_name='Дата установки'),
        ),
        migrations.AlterField(
            model_name='modules',
            name='m_street',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='appgarb.streets', verbose_name='Название улицы'),
        ),
        migrations.AddField(
            model_name='modules',
            name='m_methods',
            field=models.ManyToManyField(blank=True, to='appgarb.Methods', verbose_name='Название метода'),
        ),
    ]
