# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-01-24 02:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processing_jv', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temp_jvdetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jvdate', models.CharField(blank=True, max_length=500, null=True)),
                ('chartofaccount', models.CharField(blank=True, max_length=500, null=True)),
                ('department', models.CharField(blank=True, max_length=500, null=True)),
                ('balancecode', models.CharField(blank=True, max_length=500, null=True)),
                ('debitamount', models.CharField(blank=True, max_length=500, null=True)),
                ('creditamount', models.CharField(blank=True, max_length=500, null=True)),
                ('batchkey', models.CharField(blank=True, max_length=500, null=True)),
                ('postingstatus', models.CharField(choices=[('F', 'Failed'), ('S', 'Success')], default='F', max_length=1)),
                ('postingremarks', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['-pk'],
                'db_table': 'temp_jvdetail',
            },
        ),
        migrations.CreateModel(
            name='Temp_jvmain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jvdate', models.CharField(blank=True, max_length=500, null=True)),
                ('particulars', models.CharField(blank=True, max_length=1000, null=True)),
                ('batchkey', models.CharField(blank=True, max_length=500, null=True)),
                ('postingstatus', models.CharField(choices=[('F', 'Failed'), ('S', 'Success')], default='F', max_length=1)),
                ('postingremarks', models.CharField(blank=True, max_length=255, null=True)),
                ('importby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='temp_jvmain_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-pk'],
                'db_table': 'temp_jvmain',
            },
        ),
    ]
