# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-03-22 03:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainsupplier_supplier', '0002_auto_20180321_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainsupplier_supplier',
            name='modifydate',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
