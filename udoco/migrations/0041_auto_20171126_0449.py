# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-26 04:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('udoco', '0040_auto_20171019_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='official',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
    ]
