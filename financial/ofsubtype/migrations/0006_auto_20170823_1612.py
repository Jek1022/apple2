# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-08-23 08:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ofsubtype', '0005_auto_20170818_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ofsubtype',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 23, 16, 12, 50, 135000)),
        ),
    ]
