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

# Core Django imports
from django.db import models

# Third-party app imports

# Gestionair imports
from gestionaircontrol.game.models import get_config_value


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
            end_angle = (index + 1) * 360/nb_prizes
        prize = {'id': prize.id, 'name': prize.label, 'startAngle': start_angle, 'endAngle': end_angle,
                 'src': prize.picture.url}
        prizes_dict.append(prize)
    return prizes_dict


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
