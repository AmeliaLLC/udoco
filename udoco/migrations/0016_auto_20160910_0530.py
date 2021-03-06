# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-10 05:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('udoco', '0015_auto_20160909_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='iwb',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='iwb_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='jt',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jt_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='lt1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lt1_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='lt2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lt2_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='pbm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pbm_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='pbt1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pbt1_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='pbt2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pbt2_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='pw',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pw_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='sk1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sk1_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='roster',
            name='sk2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sk2_games', to=settings.AUTH_USER_MODEL),
        ),
    ]
