# -*- coding: UTF-8 -*-
# views.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Benoît Vuille <benoit.vuille@he-arc.ch>
#            Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
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
import json
from loop import CallCenter
CALL_CENTER = CallCenter()

# Core Django imports

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


from questionengine import agi_question, agi_save


def start_game(request):
    CALL_CENTER.game_status = "TEST"
    return HttpResponse("OK")


def game_state(request):
    return HttpResponse(CALL_CENTER.game_status)


def agi_request(request, player, phone):
    agi = agi_question(player, phone)
    return JsonResponse(agi)


@csrf_exempt
def agi_submit(request):
    if request.method == 'POST':
            r = json.loads(request.body)
            print r
            agi_save(r['answer_id'], r['answer_key'], r['correct'])
            msg = "OK"
    else:
        msg = "GET calls are not allowed for this view!"
    return HttpResponse(msg)

