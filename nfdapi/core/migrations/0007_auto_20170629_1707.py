# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-29 17:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20170628_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voucher',
            name='voucher_number',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
