# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-03-22 11:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventoryitemclass', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitemclass',
            name='chartexpcostofsale',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='invclass_chartexpcostofsale_id', to='chartofaccount.Chartofaccount'),
        ),
        migrations.AlterField(
            model_name='inventoryitemclass',
            name='chartexpgenandadmin',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='invclass_chartexpgenandadmin_id', to='chartofaccount.Chartofaccount'),
        ),
        migrations.AlterField(
            model_name='inventoryitemclass',
            name='chartexpsellexp',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='invclass_chartexpsellexp_id', to='chartofaccount.Chartofaccount'),
        ),
        migrations.AlterField(
            model_name='inventoryitemclass',
            name='inventoryitemtype',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='invclass_inventoryitemtype_id', to='inventoryitemtype.Inventoryitemtype'),
        ),
        migrations.AlterField(
            model_name='inventoryitemclass',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 22, 11, 45, 19, 536330)),
        ),
    ]
