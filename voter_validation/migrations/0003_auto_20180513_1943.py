# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-05-14 02:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voter_validation', '0002_auto_20180513_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='voter',
            name='full_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='voter',
            name='first_name',
            field=models.CharField(default='', max_length=32),
        ),
        migrations.AlterField(
            model_name='voter',
            name='last_name',
            field=models.CharField(default='', max_length=32),
        ),
        migrations.AlterField(
            model_name='voter',
            name='middle_name',
            field=models.CharField(default='', max_length=32),
        ),
    ]