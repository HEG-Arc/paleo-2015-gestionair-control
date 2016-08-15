# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('callcenter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='languages',
            field=jsonfield.fields.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='state',
            field=models.CharField(default=b'CREATED', help_text='The current state of the player in the game', max_length=20, verbose_name='player state', choices=[(b'CREATED', 'Registered'), (b'PRINTED', 'Code printed'), (b'PLAYING', 'Playing'), (b'LIMIT_REACHED', 'Limit reached'), (b'SCANNED', 'Scanned'), (b'WON', 'Won')]),
        ),
    ]
