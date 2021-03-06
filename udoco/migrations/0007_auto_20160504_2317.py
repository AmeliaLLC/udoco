# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-04 23:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('udoco', '0006_game'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('so_first_choice', models.PositiveIntegerField(choices=[(0, 'Head Ref'), (1, 'Inside Pack Ref'), (2, 'Jam Ref'), (3, 'Outside Pack Ref')])),
                ('so_second_choice', models.PositiveIntegerField(choices=[(0, 'Head Ref'), (1, 'Inside Pack Ref'), (2, 'Jam Ref'), (3, 'Outside Pack Ref')])),
                ('so_third_choice', models.PositiveIntegerField(choices=[(0, 'Head Ref'), (1, 'Inside Pack Ref'), (2, 'Jam Ref'), (3, 'Outside Pack Ref')])),
                ('nso_first_choice', models.PositiveIntegerField(choices=[(0, 'Jam Timer'), (1, 'Score Keeper'), (2, 'Penalty Box Manager'), (3, 'Penalty Box Timer'), (4, 'Penalty Tracker'), (5, 'Penalty Wrangler'), (6, 'Inside Whiteboard'), (7, 'Lineup Tracker')])),
                ('nso_second_choice', models.PositiveIntegerField(choices=[(0, 'Jam Timer'), (1, 'Score Keeper'), (2, 'Penalty Box Manager'), (3, 'Penalty Box Timer'), (4, 'Penalty Tracker'), (5, 'Penalty Wrangler'), (6, 'Inside Whiteboard'), (7, 'Lineup Tracker')])),
                ('nso_third_choice', models.PositiveIntegerField(choices=[(0, 'Jam Timer'), (1, 'Score Keeper'), (2, 'Penalty Box Manager'), (3, 'Penalty Box Timer'), (4, 'Penalty Tracker'), (5, 'Penalty Wrangler'), (6, 'Inside Whiteboard'), (7, 'Lineup Tracker')])),
            ],
        ),
        migrations.AlterField(
            model_name='game',
            name='association',
            field=models.PositiveIntegerField(choices=[(0, 'WFTDA'), (1, 'MRDA'), (2, 'JRDA'), (99, 'OTHER')]),
        ),
        migrations.AlterField(
            model_name='game',
            name='game_type',
            field=models.PositiveIntegerField(choices=[(0, 'SANCTIONED'), (1, 'REGULATION'), (99, 'OTHER')]),
        ),
        migrations.AddField(
            model_name='application',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='udoco.Game'),
        ),
        migrations.AddField(
            model_name='application',
            name='official',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
