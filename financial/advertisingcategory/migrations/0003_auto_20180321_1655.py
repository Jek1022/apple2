# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-03-21 08:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisingcategory', '0002_auto_20180321_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisingcategory',
            name='modifydate',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
