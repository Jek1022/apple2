# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-02-05 08:45
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companyparameter', '0012_auto_20180110_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyparameter',
            name='budgetapprover',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='companyparameter_budgetapprover', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='companyparameter',
            name='modifydate',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 5, 16, 45, 29, 547000)),
        ),
    ]
