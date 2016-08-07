# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-04 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rickypanel', '0003_event_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='os',
            field=models.CharField(default='OS X', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='prop1',
            field=models.CharField(default='blue', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='prop2',
            field=models.CharField(default='Mixpanel', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='prop3',
            field=models.CharField(default='Sales Engineer', max_length=100),
            preserve_default=False,
        ),
    ]