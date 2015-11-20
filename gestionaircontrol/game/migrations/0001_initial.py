# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('key', models.CharField(max_length=250, serialize=False, verbose_name='Config key', primary_key=True)),
                ('value', models.TextField(null=True, verbose_name='value of this option', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description of the key', blank=True)),
            ],
        ),
    ]
