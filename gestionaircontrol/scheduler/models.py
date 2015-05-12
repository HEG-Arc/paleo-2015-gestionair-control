# -*- coding: UTF-8 -*-
# models.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of paleo2015.
#
# paleo2015 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paleo2015 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paleo2015. If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports

# Core Django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Third-party app imports

# paleo2015 imports
from gestionaircontrol.callcenter.models import Game


class Slot(models.Model):
    # Foreign keys
    timeslot = models.ForeignKey('Timeslot', verbose_name=_('timeslot'), related_name=_('slots'),
                                 help_text=_("The timeslot of the slot"))
    game = models.OneToOneField(Game, verbose_name=_('game'), related_name=_('slot'), null=True, blank=True,
                                help_text=_("The game registered in this slot"))


class Timeslot(models.Model):
    start_time = models.DateTimeField(verbose_name=_("start time"), primary_key=True,
                                      help_text=_("The start time of the timeslot"))
    end_time = models.DateTimeField(verbose_name=_("end time"),
                                    help_text=_("The end time of the timeslot"))
