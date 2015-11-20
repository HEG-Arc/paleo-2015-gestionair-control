# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Name used for inventory purpose', max_length=250)),
                ('label', models.CharField(help_text=b'This is the name displayed on the screen, with the article', max_length=250)),
                ('percentage', models.IntegerField(max_length=2)),
                ('stock', models.IntegerField(max_length=5)),
                ('big', models.BooleanField(default=False)),
                ('free', models.BooleanField(default=False)),
                ('picture', models.ImageField(null=True, upload_to=b'', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'prize',
                'verbose_name_plural': 'prizes',
            },
        ),
    ]
