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

from gestionaircontrol.game.messaging import send_amqp_message

# Start CallCenter loop here instanitate once by django
from loop import CallCenter
CALL_CENTER = CallCenter()

# Core Django imports
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404


from questionengine import agi_question, agi_save
from gestionaircontrol.callcenter.models import Player
from gestionaircontrol.game.pdf import label, ticket
from gestionaircontrol.printing.models import Printer
from gestionaircontrol.game.models import Config


def start_game(request):
    CALL_CENTER.game_status = "TEST"
    return HttpResponse("OK")


def game_status(request):
    return HttpResponse(CALL_CENTER.game_status)

# start/init game
# stop/pause? game


def game_state(request):
    return HttpResponse("TODO send all players info")


def register_player(request):
    try:
        new_player = json.loads(request.body)
    except ValueError:
        new_player = None

    if new_player:
        player = Player()
        player.name = new_player['name']
        player.npa = new_player['npa']
        player.email = new_player['email']
        player.state = Player.REGISTERED
        player.save()

        player_json = serializers.serialize("json", player)
        message = {'player': player_json, 'type': 'PLAYER_CREATED'}
        send_amqp_message(message, "simulation")
        return JsonResponse({'id': player.id, 'code': player.code})
    else:
        return HttpResponseBadRequest('Unable to decode JSON')


def print_player(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    player.state = Player.CODEPRINTED
    player.print_time = timezone.now()
    player.save()

    #get client ip from request
    #if match in Printer.uri  print to this printer
    #else get default printer name from config
    printer = Printer
    config = Config(key='default...')
    printer.print_file( ticket( player.name, player.code, config.url . player.id ) )
    message = {'type': player.state,
                'playerId': player.id,
                'timestamp': player.print_time}
    send_amqp_message(message, "simulation")
    return HttpResponse("")


def scan_code(request):

    #eval paramerts to get player
    #FIX
    player = Player.get(id=request.body.id)

    message = {'type': 'PLAYER_SCANNED',
               'playerId': player.id,
               'state': player.state,
               'score': player.score}


    # handle player who is at rate state, for the other forwards as is to client for error display
    if(player.state == 'LIMIT_REACHED'):
        # TODO: get score limit from Config

        message['languages'] = player.languages
        player.scan_time = timezone.now()
        message['timezone'] = player.scan_time

        #print label FIX
        printer = Printer.get(name='label')
        #TOOD: fix give right params/ data
        printer.print_file( label( player ) )

        if(player.score < 3):
            # TODO: get default small price from prizes or config??
            message['prize'] = {
                    'name': 'Stylo',
                    'src': ''
                  }
            message['state'] = 'SCANNED_PEN'
            player.state = 'WON'
        else:
            message['state'] = 'SCANNED_WHEEL'
            player.state = 'SCANNED_WHEEL'
            message['prizes'] = [], # TODO get prizes and orientation for wheel from prizes?! or config
            #cache current player at wheel
            CALL_CENTER.wheel_player = player


    send_amqp_message(message, "simulation")
    return HttpResponse("")


def bumper(request):
    #FIX
     player = CALL_CENTER.wheel_player
     #TODO Handle error? or other states
     player.state = 'PRINTED'
     player.wheel_time = timezone.now()
     player.save()
    #TODO handle prize choice!
     CALL_CENTER.wheel_player = None
     message = {'type': 'WHEEL_START',
                'playerId': player.id,
                'prize': 1,  #index of prize?
                'wheel_duration': 2000, # TODO from config? + add some randomness
                'timestamp':player.wheel_time}
     send_amqp_message(message, "simulation")

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

