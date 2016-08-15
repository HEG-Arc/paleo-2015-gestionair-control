# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='cups printer name')),
                ('uri', models.CharField(max_length=250, verbose_name='uri to printer')),
                ('ppd', models.CharField(max_length=250, verbose_name='ppd file location')),
            ],
        ),
    ]
