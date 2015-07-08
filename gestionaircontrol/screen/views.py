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

# Third-party app imports

# paleo2015 imports


def get_game_status(game_start_time):
    if game_start_time:
        if timezone.now() < game_start_time + datetime.timedelta(seconds=settings.GAME_DURATION):
            current_status = "RUNNING"
        else:
            current_status = "FINISHED"
    else:
        current_status = "FINISHED"
    return current_status


def countdown(request):
    game = cache.get_many(['game_start_time', 'current_game', 'game_status'])
    if 'game_start_time' in game:
        current_status = get_game_status(game['game_start_time'])
    else:
        current_status = "FINISHED"
    if current_status == "RUNNING":
        time_left = datetime.timedelta(seconds=settings.GAME_DURATION) - (timezone.now() - game['game_start_time'])
        game['time_left'] = time_left.seconds
    elif current_status == "FINISHED":
        game['time_left'] = "GAME OVER!"
    return JsonResponse(game)


def scheduler(request):
    game = cache.get_many(['game_start_time', 'current_game', 'game_status'])
    if 'game_start_time' in game:
        current_status = get_game_status(game['game_start_time'])
    else:
        current_status = "FINISHED"
    if current_status == "RUNNING":
        time_left = datetime.timedelta(seconds=settings.GAME_DURATION) - (timezone.now() - game['game_start_time'])
        game['time_left'] = time_left.seconds
    elif current_status == "FINISHED":
        game['time_left'] = "GAME OVER!"
    return JsonResponse(game)
