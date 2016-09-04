# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wheel', '0001_initial'),
        ('callcenter', '0003_auto_20160824_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='prize',
            field=models.ForeignKey(related_name='players', blank=True, to='wheel.Prize', help_text='The prize won by the player', null=True, verbose_name='prize'),
        ),
        migrations.AddField(
            model_name='player',
            name='unlock_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
