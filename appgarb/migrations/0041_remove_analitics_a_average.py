# Generated by Django 3.1.5 on 2021-02-13 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0040_auto_20210213_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analitics',
            name='a_average',
        ),
    ]