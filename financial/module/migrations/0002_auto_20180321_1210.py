# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-03-21 04:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 12, 10, 53, 729000)),
        ),
    ]
