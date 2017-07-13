# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-29 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20170629_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementspecies',
            name='bblab_number',
            field=models.CharField(blank=True, default='', max_length=6),
        ),
        migrations.AlterField(
            model_name='elementspecies',
            name='epa_numeric_code',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='elementspecies',
            name='ibp_english',
            field=models.CharField(blank=True, default='', max_length=4),
        ),
        migrations.AlterField(
            model_name='elementspecies',
            name='ibp_scientific',
            field=models.CharField(blank=True, default='', max_length=6),
        ),
        migrations.AlterField(
            model_name='elementspecies',
            name='nrcs_usda_symbol',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='elementspecies',
            name='synonym_nrcs_usda_symbol',
            field=models.TextField(blank=True, default=''),
        ),
    ]
