# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-11-08 09:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chartofaccount', '0025_auto_20171107_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chartofaccount',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 8, 17, 47, 32, 104000)),
        ),
    ]
