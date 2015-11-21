# -*- coding: UTF-8 -*-
# models.py
#
# Copyright (C) 2013 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of appagoo.
#
# appagoo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# appagoo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with appagoo.  If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
from random import randrange

# Core Django imports
from django.db import models
from django.core.cache import cache

# Third-party app imports

# Gestionair imports
# from gestionaircontrol.game.models import get_config_value


def get_current_wheel():
    prizes_dict = []
    # min_number_wheel_prizes = get_config_value('min_number_wheel_prizes')
    prizes = Prize.objects.filter(free=False)
    nb_prizes = len(prizes)
    for index, prize in enumerate(Prize.objects.filter(free=False)):
        start_angle = index * 360/nb_prizes
        if index + 1 == nb_prizes:
            end_angle = 360
        else:
            end_angle = ((index + 1) * 360/nb_prizes) - 1
        prize = {'id': prize.id, 'name': prize.label, 'startAngle': start_angle, 'endAngle': end_angle,
                 'src': prize.picture.url}
        prizes_dict.append(prize)
    return prizes_dict


def get_random_prize():
    last_prize_id = cache.get('last_prize_id')

    if last_prize_id:
        prizes_list = Prize.objects.filter(stock__gt=0).exclude(pk=last_prize_id)
    else:
        prizes_list = Prize.objects.filter(stock__gt=0)

    # We build a dict with all available prizes
    prizes_dict = {}
    total_weight = 0
    fill_prizes = 0
    for prize in prizes_list:
        prizes_dict[prize.id] = prize.percentage
        if prize.percentage != 100:
            total_weight += prize.percentage
        else:
            fill_prizes += 1

    # We build a list with all prizes
    weighted_prizes_list = []
    for p in prizes_dict:
        if prizes_dict[p] != 100:
            for i in range(0, prizes_dict[p]):
                weighted_prizes_list.append(p)
        else:
            for i in range(0, (100-total_weight)/fill_prizes):
                weighted_prizes_list.append(p)

    # We randomly choose one prize in the list
    prize_id = weighted_prizes_list[randrange(len(weighted_prizes_list))]
    prize = Prize.objects.get(pk=prize_id)
    cache.set('last_prize_id', prize.id)
    prize.stock -= 1
    prize.save()
    return prize.id, prize.big


class Prize(models.Model):
    name = models.CharField(max_length=250, help_text='Name used for inventory purpose')
    label = models.CharField(max_length=250, help_text='This is the name displayed on the screen, with the article')
    percentage = models.IntegerField(max_length=2)
    stock = models.IntegerField(max_length=5)
    big = models.BooleanField(default=False)
    free = models.BooleanField(default=False)
    picture = models.ImageField(blank=True, null=True)

    class Meta:
        verbose_name = 'prize'
        verbose_name_plural = 'prizes'
        ordering = ['name']

    def __unicode__(self):
        return self.name
