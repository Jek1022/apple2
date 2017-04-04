# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-04-03 13:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requisitionform', '0008_auto_20170327_1346'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfdetail',
            name='invitem_unitofmeasure',
            field=models.CharField(default='cm', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rfdetailtemp',
            name='invitem_unitofmeasure',
            field=models.CharField(default='cm', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='rfdetail',
            name='enterdate',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 3, 13, 44, 13, 861000)),
        ),
        migrations.AlterField(
            model_name='rfdetail',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 3, 13, 44, 13, 861000)),
        ),
        migrations.AlterField(
            model_name='rfdetailtemp',
            name='enterdate',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 3, 13, 44, 13, 864000)),
        ),
        migrations.AlterField(
            model_name='rfdetailtemp',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 3, 13, 44, 13, 864000)),
        ),
        migrations.AlterField(
            model_name='rfmain',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 4, 3, 13, 44, 13, 856000)),
        ),
    ]
