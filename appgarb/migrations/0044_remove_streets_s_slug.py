# Generated by Django 3.1.5 on 2021-02-23 02:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appgarb', '0043_auto_20210223_0158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='streets',
            name='s_slug',
        ),
    ]
