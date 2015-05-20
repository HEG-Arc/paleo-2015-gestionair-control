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
import collections

# Core Django imports
from django.shortcuts import render
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, JsonResponse
from django.conf import settings

# Third-party app imports

# paleo2015 imports


def start(request):
    # Is it already working?
    start_time = cache.get('start_time')
    if start_time:
        if datetime.datetime.now() < start_time + datetime.timedelta(seconds=settings.GAME_DURATION):
            # The game is not yet finished
            pass
        else:
            # We can start a new counter
            start_time = datetime.datetime.now()
            # We store the value in Redis
            cache.set_many({'start_time': start_time, 'current_game': 999})
            # We initialize the new simulation
    else:
        # We can start a new counter
        start_time = datetime.datetime.now()
        # We store the value in Redis
        cache.set_many({'start_time': start_time, 'current_game': 999})
        # We initialize the new simulation
    game = cache.get_many(['start_time', 'current_game'])
    return HttpResponse("Game %s started at: %s." % (game['current_game'], game['start_time']),
                        content_type="text/plain")


def status(request):
    game = cache.get_many(['start_time', 'current_game'])
    if game.get('start_time'):
        if datetime.datetime.now() < game['start_time'] + datetime.timedelta(seconds=settings.GAME_DURATION):
            current_status = "RUNNING"
        else:
            current_status = "PAUSED"
    else:
        current_status = "PAUSED"
    return HttpResponse("Current status: %s (Game %s started at: %s)." % (current_status, game.get('current_game'), game.get('start_time')),
                        content_type="text/plain")


def stop(request):
    game = cache.get_many(['start_time', 'current_game'])
    cache.delete_many(['start_time', 'current_game'])
    return HttpResponse("Game %s was stopped." % game['current_game'],
                        content_type="text/plain")


def countdown(request):
    game = cache.get_many(['start_time', 'current_game'])
    if game.get('start_time'):
        if datetime.datetime.now() < game['start_time'] + datetime.timedelta(seconds=settings.GAME_DURATION):
            time_left = datetime.timedelta(seconds=settings.GAME_DURATION) - (datetime.datetime.now() - game.get('start_time'))
            game['time_left'] = time_left.seconds
        else:
            game['time_left'] = "GAME OVER!"
    else:
        game['time_left'] = "GAME OVER!"
    return JsonResponse(game)