# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('callcenter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('booking_position', models.IntegerField(default=0, help_text='The position of the game in the time slot', verbose_name='booking position')),
                ('game', models.OneToOneField(related_name='slot', null=True, to='callcenter.Game', blank=True, help_text='The game registered in this time slot', verbose_name='game')),
            ],
            options={
                'ordering': ['timeslot', 'booking_position'],
                'verbose_name': 'booking',
                'verbose_name_plural': 'bookings',
            },
        ),
        migrations.CreateModel(
            name='Timeslot',
            fields=[
                ('start_time', models.DateTimeField(help_text='The start time of the timeslot', serialize=False, verbose_name='start time', primary_key=True)),
                ('duration', models.IntegerField(default=20, help_text='The duration of the time slot in minutes', verbose_name='time slot duration')),
                ('booking_capacity', models.IntegerField(default=5, help_text='The number of bookings bookable in this time slot', verbose_name='booking capacity')),
                ('booking_availability', models.IntegerField(default=3, help_text='The number of bookings available in this time slot', verbose_name='booking availability')),
            ],
            options={
                'ordering': ['start_time'],
                'verbose_name': 'timeslot',
                'verbose_name_plural': 'timeslots',
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='timeslot',
            field=models.ForeignKey(related_name='bookings', verbose_name='time slot', to='scheduler.Timeslot', help_text='The time slot of the booking'),
        ),
    ]
