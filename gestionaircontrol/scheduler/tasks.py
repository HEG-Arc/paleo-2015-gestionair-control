# -*- coding: UTF-8 -*-
# tasks.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of paleo-2015-gestionair-control.
#
# paleo-2015-gestionair-control is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paleo-2015-gestionair-control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paleo-2015-gestionair-control. If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
import datetime

# Core Django imports
#from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# Third-party app imports

# paleo-2015-gestionair-control imports
from config.celery import app
from gestionaircontrol.scheduler.models import Timeslot


@app.task
def schedule_availability():
    available_slots = Timeslot.objects.filter(start_time__lte=datetime.datetime.now()+datetime.timedelta(minutes=20))
    updated = False
    for slot in available_slots:
        slot.booking_availability = slot.booking_capacity
        slot.save()
        updated = True
    if updated:
        return _('New slots available!')
