# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-09 01:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rickypanel', '0002_auto_20160808_2102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='id',
        ),
        migrations.AlterField(
            model_name='project',
            name='report_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
