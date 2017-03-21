# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-03-21 09:28
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventoryitemtype', '0002_auto_20170321_0928'),
        ('requisitionform', '0002_auto_20170320_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfmain',
            name='inventoryitemtype',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='inventoryitemtype_id', to='inventoryitemtype.Inventoryitemtype'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='rfdetail',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 21, 9, 28, 37, 376000)),
        ),
        migrations.AlterField(
            model_name='rfdetail',
            name='postdate',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 21, 9, 28, 37, 376000)),
        ),
        migrations.AlterField(
            model_name='rfdetailtemp',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 21, 9, 28, 37, 378000)),
        ),
        migrations.AlterField(
            model_name='rfdetailtemp',
            name='postdate',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 21, 9, 28, 37, 378000)),
        ),
        migrations.AlterField(
            model_name='rfmain',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 21, 9, 28, 37, 374000)),
        ),
        migrations.AlterField(
            model_name='rfmain',
            name='postdate',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 21, 9, 28, 37, 374000)),
        ),
    ]
