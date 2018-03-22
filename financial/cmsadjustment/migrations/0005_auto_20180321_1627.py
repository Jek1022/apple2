# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-03-21 08:27
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cmsadjustment', '0004_auto_20180118_0927'),
    ]

    operations = [
        migrations.AddField(
            model_name='cmitem',
            name='closeby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cmitem_close', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cmitem',
            name='closedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cmmain',
            name='closeby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cmmain_close', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cmmain',
            name='closedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cmitem',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 41, 59000)),
        ),
        migrations.AlterField(
            model_name='cmmain',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 21, 16, 27, 41, 57000)),
        ),
    ]
