# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-03-21 08:27
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountspayable', '0029_auto_20180309_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apdetail',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 949000)),
        ),
        migrations.AlterField(
            model_name='apdetail',
            name='postdate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 950000)),
        ),
        migrations.AlterField(
            model_name='apdetailbreakdown',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 952000)),
        ),
        migrations.AlterField(
            model_name='apdetailbreakdown',
            name='postdate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 952000)),
        ),
        migrations.AlterField(
            model_name='apdetailbreakdowntemp',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 956000)),
        ),
        migrations.AlterField(
            model_name='apdetailbreakdowntemp',
            name='postdate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 956000)),
        ),
        migrations.AlterField(
            model_name='apdetailtemp',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 954000)),
        ),
        migrations.AlterField(
            model_name='apdetailtemp',
            name='postdate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 954000)),
        ),
        migrations.AlterField(
            model_name='apmain',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 40, 947000)),
        ),
    ]
