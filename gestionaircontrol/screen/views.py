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
    next_free_slots = Timeslot.objects.prefetch_related('bookings').annotate(Count('bookings')).filter(bookings__count__lt=F('booking_availability')).filter(start_time__gte=timezone.now()-datetime.timedelta(minutes=20))
    if len(next_free_slots) >= 1:
        next_free_slot = next_free_slots[0]
        next_free_slot_start_time = next_free_slot.start_time + datetime.timedelta(seconds=(settings.GAME_LENGTH * next_free_slot.nb_bookings))
        if next_free_slot_start_time < timezone.now():
            next_free_slot_start_time = timezone.now()
    else:
        next_free_slot_start_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    next_teams = Game.objects.prefetch_related('slot', 'players').annotate(nb_players=Count('players')).filter(canceled=False, slot__isnull=False, nb_players__gt=0, start_time__isnull=True).order_by('slot__timeslot__start_time', 'slot__booking_position')[:4]
    next_teams_list = []
    for game in next_teams:
        display_team = {'team': game.team, 'position': game.slot.booking_position, 'players': game.nb_players}
        next_teams_list.append(display_team)
    response = {'next_start_time': next_start_time, 'next_free_slot_start_time': next_free_slot_start_time,
                'next_teams': next_teams_list}
    return JsonResponse(response, safe=False)


class WaitingView(TemplateView):
    template_name = "screen/waiting.html"

    def get_context_data(self, **kwargs):
        context = super(WaitingView, self).get_context_data(**kwargs)
        context['free_time_slots'] = Timeslot.objects.prefetch_related('bookings').annotate(Count('bookings')).filter(bookings__count__lt=F('booking_availability')).filter(start_time__gte=timezone.now()-datetime.timedelta(hours=1))[0]
        context['next_games'] = Game.objects.prefetch_related('slot', 'players').annotate(nb_players=Count('players')).filter(canceled=False, slot__isnull=False, nb_players__gt=0, start_time__isnull=True).order_by('slot__timeslot__start_time', 'slot__booking_position')[:4]
        #context['waiting_time'] = to be implemented
        return context