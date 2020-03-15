# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-06-26 06:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('voter_validation', '0004_auto_20180513_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validationrecord',
            name='last_updated',
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now),
        ),
    ]