# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-01-03 03:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing_or', '0020_auto_20180103_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='temp_ormain',
            name='accounttype',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
