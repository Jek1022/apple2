# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-03-23 11:09
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventoryitemtype', '0007_auto_20170323_1109'),
        ('unit', '0008_auto_20170323_1109'),
        ('inventoryitem', '0004_auto_20170323_1109'),
        ('branch', '0008_auto_20170323_1109'),
        ('department', '0011_auto_20170323_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rfdetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_counter', models.IntegerField()),
                ('invitem_code', models.CharField(max_length=25)),
                ('invitem_name', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('remarks', models.CharField(blank=True, max_length=250, null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive'), ('C', 'Cancelled'), ('O', 'Posted'), ('P', 'Printed')], default='A', max_length=1)),
                ('enterdate', models.DateTimeField(auto_now_add=True)),
                ('modifydate', models.DateTimeField(default=datetime.datetime(2017, 3, 23, 11, 9, 22, 265000))),
                ('postdate', models.DateTimeField(default=datetime.datetime(2017, 3, 23, 11, 9, 22, 265000))),
                ('isdeleted', models.IntegerField(default=0)),
                ('enterby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetail_enter', to=settings.AUTH_USER_MODEL)),
                ('invitem_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rfdetail_invitem_id', to='inventoryitem.Inventoryitem')),
                ('modifyby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetail_modify', to=settings.AUTH_USER_MODEL)),
                ('postby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetail_post', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-pk'],
                'db_table': 'rfdetail',
            },
        ),
        migrations.CreateModel(
            name='Rfdetailtemp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_counter', models.IntegerField()),
                ('invitem_code', models.CharField(max_length=25)),
                ('invitem_name', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('remarks', models.CharField(blank=True, max_length=250, null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive'), ('C', 'Cancelled'), ('O', 'Posted'), ('P', 'Printed')], default='A', max_length=1)),
                ('enterdate', models.DateTimeField(auto_now_add=True)),
                ('modifydate', models.DateTimeField(default=datetime.datetime(2017, 3, 23, 11, 9, 22, 267000))),
                ('postdate', models.DateTimeField(default=datetime.datetime(2017, 3, 23, 11, 9, 22, 267000))),
                ('isdeleted', models.IntegerField(default=0)),
                ('secretkey', models.CharField(max_length=255)),
                ('enterby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetailtemp_enter', to=settings.AUTH_USER_MODEL)),
                ('invitem_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rfdetailtemp_invitem_id', to='inventoryitem.Inventoryitem')),
                ('modifyby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetailtemp_modify', to=settings.AUTH_USER_MODEL)),
                ('postby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetailtemp_post', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-pk'],
                'db_table': 'rfdetailtemp',
            },
        ),
        migrations.CreateModel(
            name='Rfmain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rfnum', models.CharField(max_length=10, unique=True)),
                ('rfdate', models.DateField()),
                ('refnum', models.CharField(blank=True, max_length=150, null=True)),
                ('rftype', models.CharField(default='REGULAR', max_length=150)),
                ('urgencytype', models.CharField(choices=[('N', 'Normal'), ('R', 'Rush')], default='N', max_length=1)),
                ('dateneeded', models.DateField()),
                ('particulars', models.TextField()),
                ('rfstatus', models.CharField(choices=[('F', 'For Approval'), ('A', 'Approved'), ('D', 'Disapproved')], default='F', max_length=1)),
                ('approverresponse', models.CharField(blank=True, choices=[('A', 'Approved'), ('D', 'Disapproved')], max_length=1, null=True)),
                ('responsedate', models.DateTimeField(blank=True, null=True)),
                ('remarks', models.CharField(blank=True, max_length=250, null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive'), ('C', 'Cancelled'), ('O', 'Posted'), ('P', 'Printed')], default='A', max_length=1)),
                ('enterdate', models.DateTimeField(auto_now_add=True)),
                ('modifydate', models.DateTimeField(default=datetime.datetime(2017, 3, 23, 11, 9, 22, 263000))),
                ('postdate', models.DateTimeField(blank=True, null=True)),
                ('isdeleted', models.IntegerField(default=0)),
                ('actualapprover', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actual_approver', to=settings.AUTH_USER_MODEL)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rfmain_branch_id', to='branch.Branch')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rfmain_department_id', to='department.Department')),
                ('designatedapprover', models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='designated_approver', to=settings.AUTH_USER_MODEL)),
                ('enterby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfmain_enter', to=settings.AUTH_USER_MODEL)),
                ('inventoryitemtype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rfmain_inventoryitemtype_id', to='inventoryitemtype.Inventoryitemtype')),
                ('modifyby', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rfmain_modify', to=settings.AUTH_USER_MODEL)),
                ('postby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rfmain_post', to=settings.AUTH_USER_MODEL)),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rfmain_unit_id', to='unit.Unit')),
            ],
            options={
                'ordering': ['-pk'],
                'db_table': 'rfmain',
            },
        ),
        migrations.AddField(
            model_name='rfdetailtemp',
            name='rfmain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetailtemp_rfmain_id', to='requisitionform.Rfmain'),
        ),
        migrations.AddField(
            model_name='rfdetail',
            name='rfmain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rfdetail_rfmain_id', to='requisitionform.Rfmain'),
        ),
    ]
