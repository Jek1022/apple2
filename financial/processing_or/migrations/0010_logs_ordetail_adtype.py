# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-12-19 02:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing_or', '0009_logs_ordetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='logs_ordetail',
            name='adtype',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
