# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_code', models.CharField(max_length=10, verbose_name='Event code')),
                ('event_name', models.CharField(max_length=250, null=True, verbose_name='Name of the event', blank=True)),
                ('stats_date', models.DateField(verbose_name='Date of the statistics')),
                ('creation', models.DateTimeField(auto_now_add=True, null=True)),
                ('stats', jsonfield.fields.JSONField()),
            ],
        ),
    ]
