# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-05-22 22:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chartofaccount', '0038_auto_20180323_1137'),
        ('companyparameter', '0022_auto_20180523_0352'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyparameter',
            name='coa_retainedearnings',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='param_coa_retainedearnings', to='chartofaccount.Chartofaccount'),
        ),
    ]
