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

from django.core.files import File

from gestionaircontrol.game.messaging import send_amqp_message

# Start CallCenter loop here instanitate once by django
from loop import CallCenter
CALL_CENTER = CallCenter()

# Core Django imports
from django.shortcuts import redirect
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist


from questionengine import agi_question, agi_save
from gestionaircontrol.callcenter.models import Player
from gestionaircontrol.game.pdf import label, ticket
from gestionaircontrol.printing.models import Printer
from gestionaircontrol.game.models import get_config_value, get_config
from gestionaircontrol.wheel.models import Prize, get_current_wheel, get_random_prize

def start_game(request):
    CALL_CENTER.start_game()
    return HttpResponse("OK")

def stop_game(request):
    CALL_CENTER.stop_game()
    return HttpResponse("OK")

# call 1201 for demo
def call_phone(request, number):
    CALL_CENTER.call_number(number)
    return HttpResponse("OK")

def status(requests):
    status = {
        'isRunning': CALL_CENTER.is_running,
        'startTime': CALL_CENTER.start_time,
        'demoState': CALL_CENTER.demo_state()
    }
    return JsonResponse(status)


# sound can be call or ambiance
def play_sound(requests, sound):
    send_amqp_message({'type': 'PLAY_SOUND', 'sound': sound, 'area': 'center'}, "simulation")
    return HttpResponse("OK")


@csrf_exempt
def register_player(request):
    try:
        new_player = json.loads(request.body)
    except ValueError:
        new_player = None

    if new_player:
        player = Player()
        player.name = new_player['name']
        player.zipcode = new_player['npa']
        player.email = new_player['email']
        player.state = Player.REGISTERED
        player.save()

        player_dict = model_to_dict(player)
        message = {'player': player_dict, 'type': 'PLAYER_CREATED'}
        send_amqp_message(message, "simulation")
        return JsonResponse({'id': player.id, 'code': player.code})
    else:
        return HttpResponseBadRequest('Unable to decode JSON')


def print_player(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    player.state = Player.CODEPRINTED
    player.print_time = timezone.now()
    player.save()

    ip = request.META.get('HTTP_X_REAL_IP')

    try:
        printer = Printer.objects.get(uri__contains=str(ip))
    except ObjectDoesNotExist:
        default_printer = get_config_value('default_ticket_printer')
        if default_printer:
            printer = Printer.objects.get(name=default_printer)
        else:
            printer = None

    if printer:
        printer.print_file(ticket(player.name, player.code, player.url))
        message = {'type': 'PLAYER_PRINTED',
                   'playerId': player.id,
                   'timestamp': player.print_time.isoformat()}
        send_amqp_message(message, "simulation")
        return HttpResponse("OK - Printed on %s" % printer.name)
    else:
        return HttpResponseBadRequest('Unable to find a printer')


def scan_code(request, code):
    player = Player.objects.get(pk=1)
    message = {'type': 'PLAYER_SCANNED',
               'playerId': -1,
               'state': 'SCANNED_WHEEL',
               'score': 999,
               'prizes': get_current_wheel()}
    CALL_CENTER.wheel_player = player.id
    player.score += 1
    player.save()
    send_amqp_message(message, "simulation")
    return HttpResponse("")


def scan_player(request, player_id):
    player = get_object_or_404(Player, pk=player_id)

    message = {'type': 'PLAYER_SCANNED',
               'playerId': player.id,
               'state': player.state,
               'score': player.score}

    # handle player who is at rate state, for the other forwards as is to client for error display
    if player.state == Player.LIMITREACHED or (player.state == Player.SCANNED and player.wheel_time is None):
        languages = []
        for answer in player.answers.all():
            if answer.pickup_time and answer.hangup_time:
                languages.append({'lang': answer.question.language.code, 'correct': int(answer.correct)})
        player.languages = languages
        message['languages'] = languages
        player.scan_time = timezone.now()
        message['timezone'] = player.scan_time.isoformat()

        label_printer = get_config_value('label_printer')
        if label_printer:
            printer = Printer.objects.get(name=label_printer)
        else:
            printer = None

        if printer:
            printer.print_file(label(player))

        if player.score < int(get_config_value('minimum_score')):
            prize = Prize.objects.filter(free=True).first()
            if prize:
                message['prize'] = {
                    'name': prize.label,
                    'src': prize.picture.url
                }
            message['state'] = 'SCANNED_PEN'
            player.state = Player.WON
        else:
            message['state'] = 'SCANNED_WHEEL'
            player.state = Player.SCANNED
            message['prizes'] = get_current_wheel()
            # cache current player at wheel
            CALL_CENTER.wheel_player = player.id

        player.save()

    send_amqp_message(message, "simulation")
    return HttpResponse("")


def bumper(request):
    player_id = CALL_CENTER.wheel_player
    player = Player.objects.get(pk=player_id)

    # TODO Handle error? or other states
    player.state = Player.WON
    player.wheel_time = timezone.now()
    player.save()

    CALL_CENTER.wheel_player = None
    prize_id, prize_big = get_random_prize()
    if prize_big:
        prize_size = 'big'
    else:
        prize_size = 'small'
    message = {'type': 'WHEEL_START',
               'playerId': player.id,
               'prize': prize_id,
               'size': prize_size,
               'wheel_duration': int(get_config_value('wheel_duration')),
               'timestamp': player.wheel_time.isoformat()}
    send_amqp_message(message, "simulation")


def load_config(request):
    return JsonResponse(get_config())


def players_list(request):
    # TODO: Filter e-mail and zip if not requested by an admin
    players = serializers.serialize('json', Player.objects.all())
    return JsonResponse(dict([(p['pk'], dict(p['fields'], id=p['pk'])) for p in json.loads(players)]), safe=False)


def agi_request(request, player, phone):
    agi = agi_question(player, phone)
    return JsonResponse(agi)


def agi_public_request(request):
    agi = agi_question(None, None)
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


def frontend_redirect(request):
    ip = request.META.get('HTTP_X_REAL_IP')
    if not ip:
        ip = request.META.get('REMOTE_ADDR')
    url = get_config_value(ip)
    if not url:
        url = get_config_value('default_frontend_url')
    return redirect(url)



from gestionaircontrol.game.serializers import GamePlayerSerializer
def test_score_sync(request, id):
    player = Player.objects.get(pk=id)
    send_amqp_message({
        'code': '%s%s' % (get_config_value('event_id'), player.id),
        'json': GamePlayerSerializer(player).data
    }, 'sync')
    return HttpResponse('created')
