# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-24 03:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('udoco', '0010_auto_20160601_2357'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alt_games', to=settings.AUTH_USER_MODEL)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roster', to='udoco.Game')),
                ('hr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hr_games', to=settings.AUTH_USER_MODEL)),
                ('ipr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ipr_games', to=settings.AUTH_USER_MODEL)),
                ('jr1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jr1_games', to=settings.AUTH_USER_MODEL)),
                ('jr2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jr2_games', to=settings.AUTH_USER_MODEL)),
                ('opr1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opr1_games', to=settings.AUTH_USER_MODEL)),
                ('opr2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opr2_games', to=settings.AUTH_USER_MODEL)),
                ('opr3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opr3_games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]