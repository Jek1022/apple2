# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-05-24 15:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaseorder', '0015_auto_20170524_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podetail',
            name='itemdetailkey',
        ),
        migrations.AlterField(
            model_name='podata',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 24, 15, 0, 47, 298000)),
        ),
        migrations.AlterField(
            model_name='podetail',
            name='enterdate',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 24, 15, 0, 47, 291000)),
        ),
        migrations.AlterField(
            model_name='podetail',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 24, 15, 0, 47, 291000)),
        ),
        migrations.AlterField(
            model_name='podetailtemp',
            name='enterdate',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 24, 15, 0, 47, 295000)),
        ),
        migrations.AlterField(
            model_name='podetailtemp',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 24, 15, 0, 47, 295000)),
        ),
        migrations.AlterField(
            model_name='pomain',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 24, 15, 0, 47, 287000)),
        ),
    ]
