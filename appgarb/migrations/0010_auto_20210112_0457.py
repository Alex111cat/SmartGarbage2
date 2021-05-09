# Generated by Django 3.1.5 on 2021-01-12 01:57

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0009_auto_20210111_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modules',
            name='m_entrance',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Подъезд'),
        ),
        migrations.AlterField(
            model_name='modules',
            name='m_start',
            field=models.DateField(default=datetime.date(2021, 1, 12), verbose_name='Дата установки'),
        ),
    ]