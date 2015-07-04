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


class Booking(models.Model):
    # Foreign keys
    timeslot = models.ForeignKey('Timeslot', verbose_name=_('time slot'), related_name=_('bookings'),
                                 help_text=_("The time slot of the booking"))
    game = models.OneToOneField(Game, verbose_name=_('game'), related_name=_('slot'), null=True, blank=True,
                                help_text=_("The game registered in this time slot"))
    booking_position = models.IntegerField(verbose_name=_("booking position"), default=0,
                                           help_text=_("The position of the game in the time slot"))

    def save(self, *args, **kwargs):
        try:
            max_position = Booking.objects.filter(timeslot=self.timeslot).order_by('-booking_position')[0]
            self.booking_position = max_position.booking_position + 1
        except IndexError:
            self.booking_position = 1
        super(Booking, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('booking')
        verbose_name_plural = _('bookings')
        ordering = ['timeslot', 'booking_position']

    def __unicode__(self):
        return "%s [%s] %s" % (self.timeslot.__unicode__(), self.booking_position, self.game.team)


class Timeslot(models.Model):
    start_time = models.DateTimeField(verbose_name=_("start time"), primary_key=True,
                                      help_text=_("The start time of the timeslot"))
    duration = models.IntegerField(verbose_name=_("time slot duration"), default=20,
                                   help_text=_("The duration of the time slot in minutes"))
    booking_capacity = models.IntegerField(verbose_name=_("booking capacity"), default=5,
                                           help_text=_("The number of bookings bookable in this time slot"))
    booking_availability = models.IntegerField(verbose_name=_("booking availability"), default=3,
                                               help_text=_("The number of bookings available in this time slot"))

    def _nb_bookings(self):
        nb_bookings = self.bookings.all().count()
        return nb_bookings
    nb_bookings = property(_nb_bookings)

    def _free_slots(self):
        free_slots = self.booking_availability - self.nb_bookings
        return free_slots
    free_slots = property(_free_slots)

    class Meta:
        verbose_name = _('timeslot')
        verbose_name_plural = _('timeslots')
        ordering = ['start_time']

    def __unicode__(self):
        return self.start_time.strftime("%Y-%m-%d %H:%M")
