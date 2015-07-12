# -*- coding: UTF-8 -*-
# views.py
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
import datetime

# Core Django imports
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from gestionaircontrol.scheduler.models import Timeslot, Game
from django.views.generic import TemplateView
from django.db.models import F, Count
from django.core import serializers


# Third-party app imports

# paleo2015 imports
from gestionaircontrol.callcenter.utils import get_next_start_time

def countdown(request):
    game = cache.get_many(['game_start_time', 'callcenter'])
    try:
        game_start_time = game.get('game_start_time').isoformat()
    except:
        game_start_time = ''

    response = {'game_start_time': game_start_time, 'game_status': game.get('callcenter', 'STOP'),
                'intro_duration': settings.GAME_PHASE_INTRO, 'game_duration': settings.GAME_PHASE_CALL}
    return JsonResponse(response)


def scheduler(request):
    next_start_time = get_next_start_time()
    next_free_slots = Timeslot.objects.prefetch_related('bookings').annotate(Count('bookings')).filter(bookings__count__lt=F('booking_capacity')).filter(start_time__gte=timezone.now()-datetime.timedelta(minutes=settings.SLOT_DURATION))
    if len(next_free_slots) >= 1:
        next_free_slot = next_free_slots[0]
        next_free_slot_start_time = next_free_slot.start_time + datetime.timedelta(seconds=(settings.GAME_LENGTH * next_free_slot.nb_bookings))
        if next_free_slot_start_time < timezone.now():
            next_free_slot_start_time = timezone.now()
    else:
        next_free_slot_start_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    next_slots = Timeslot.objects.prefetch_related('bookings').filter(start_time__gt=timezone.now()-datetime.timedelta(minutes=2*settings.SLOT_DURATION), start_time__lt=timezone.now()+datetime.timedelta(minutes=settings.SLOT_DURATION))
    next_slots_list = []
    for slot in next_slots:
        next_teams_list = []
        for booking in slot.bookings.all():
            if not booking.game.canceled:
                display_team = {'team': booking.game.team, 'position': booking.booking_position, 'players': booking.game.nb_players}
                next_teams_list.append(display_team)
        display_slot = {'slot': slot.start_time, 'teams': next_teams_list}
        next_slots_list.append(display_slot)

    response = {'next_start_time': next_start_time, 'next_free_slot_start_time': next_free_slot_start_time,
                'next_slots': next_slots_list}
    return JsonResponse(response, safe=False)
