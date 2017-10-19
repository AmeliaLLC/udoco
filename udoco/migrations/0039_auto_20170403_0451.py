# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-04-03 04:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('udoco', '0038_auto_20170402_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='alt_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='hnso_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='hr_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='ipr_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='iwb_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='jr1_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='jr2_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='jt_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='lt1_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='lt2_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='nsoalt_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='opr1_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='opr2_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='opr3_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='pbm_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='pbt1_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='pbt2_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='pt1_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='pt2_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='ptimer_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='pw_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='sk1_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='sk2_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
        migrations.AddField(
            model_name='roster',
            name='so_x',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='udoco.Loser'),
        ),
    ]