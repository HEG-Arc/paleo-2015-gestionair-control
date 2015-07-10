# -*- coding: UTF-8 -*-
# tasks.py
#
# Copyright (C) 2014 HES-SO//HEG Arc
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
import os
import random
import pyglet
#import pygame
import subprocess
from pycall import CallFile, Call, Application, Context
import signal
import random
import ari


# Core Django imports
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

# Third-party app imports

# paleo-2015-gestionair-control imports
from config.celery import app
from gestionaircontrol.scheduler.messaging import send_amqp_message
from gestionaircontrol.callcenter.models import Game, Player, Answer, Department, Language, Question, Translation, Phone


funky = os.path.join(settings.STATIC_ROOT, 'sounds', 'game music FUNK.mp3')


@app.task
def play_call():
    send_amqp_message("{'play': 'funky'}", "player.start")
    # call = pyglet.media.load(funky, streaming=False)
    # player = call.play()
    # pygame.mixer.init()
    # pygame.mixer.music.load(funky)
    # pygame.mixer.music.play(0)
    # time.sleep(10)
    # pygame.mixer.music.stop()


@app.task
def sound_control(sound):
    if sound == 'call':
        play_call.apply_async()


@app.task
def create_call_file(phone):
    type = Phone.objects.get(number=phone).usage
    if type == Phone.PUBLIC:
        wait = 20
        extension = 6666
        context = 'paleo-jukebox'
    elif type == Phone.DEMO:
        wait = 10
        extension = 2001
        context = 'paleo-callcenter'
    elif type == Phone.CENTER:
        wait = 15
        extension = 2001
        context = 'paleo-callcenter'
    else:
        context = None
    print type
    print context
    if context:
        c = Call('SIP/%s' % phone, wait_time=wait, retry_time=1, max_retries=1)
        x = Context(context, str(extension), '1')
        cf = CallFile(c, x)
        cf.spool()
        subprocess.call('/usr/bin/sudo chmod 660 /var/spool/asterisk/outgoing/*.call && /usr/bin/sudo chown asterisk:asterisk /var/spool/asterisk/outgoing/*.call', shell=True)
        send_amqp_message({'type': 'PHONE_RINGING', 'number': int(phone)}, "asterisk.call")
    else:
        pass


@app.task
def init_simulation():
    loop = None
    game = cache.get_many(['game_start_time', 'current_game'])
    game_status = 'INIT'
    players = Player.objects.filter(game_id=game['current_game'])
    players_list = []
    for player in players:
        players_list.append({'id': player.number, 'name': player.name})
    phones = Phone.objects.filter(usage=Phone.CENTER)
    phones_list = [{'number': phone.number, 'x': phone.position_x, 'y': phone.position_y,
                    'orientation': phone.orientation} for phone in phones]
    message = {'type': 'GAME_START', 'endTime': (game['game_start_time'] + datetime.timedelta(seconds=settings.GAME_DURATION)).isoformat(),
               'players': players_list, 'phones': phones_list}
    send_amqp_message(message, "simulation.caller")
    while game['game_start_time'] > timezone.now() - datetime.timedelta(seconds=settings.GAME_DURATION):
        # 00 : Intro
        if game_status == 'INIT':
            game_status = 'INTRO'
            cache.set('game_status', game_status)
            send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
        # 37 : Call center
        elif game_status == 'INTRO' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=37):
            loop = call_center_loop.apply_async([len(players_list)])
            game_status = 'CALL'
            cache.set('game_status', game_status)
            send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
        # 217 : Powerdown
        elif game_status == 'CALL' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=117):
            loop.revoke()
            game_status = 'POWERDOWN'
            cache.set('game_status', game_status)
            send_amqp_message('{"game": "%s", "type": "GAME_END"}' % game_status, "simulation.caller")
        # 247 : The END ;-)
        elif game_status == 'POWERDOWN' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=247):
            game_status = 'END'
            cache.set('game_status', game_status)
            send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
    # Game is over!
    game_status = 'OVER'
    cache.set('game_status', game_status)
    send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
    # Delete cache
    cache.delete_many(['game_start_time', 'current_game'])


@app.task
def stop_simulation():
    #send_amqp_message('{"game": "%s", "type": "GAME_END"}' % game_status, "simulation.caller")
    pass



def get_departments_numbers():
    cached = cache.get('departments_numbers', '')
    if cached:
        return cached
    else:
        # TODO: Add logging
        departments = Department.objects.all()
        departments_numbers = []
        for department in departments:
            departments_numbers.append(department.number)
        # Expires after 300 seconds
        cache.set('departments_numbers', departments_numbers, 300)
        return departments_numbers


def get_languages_codes():
    cached = cache.get('languages_codes', '')
    if cached:
        return cached
    else:
        # TODO: Add logging
        languages = Language.objects.all()
        weighted_languages_codes = []
        for language in languages:
            weighted_languages_codes.append((language.code, language.weight))
        # Expires after 300 seconds
        languages_codes = [val for val, cnt in weighted_languages_codes for i in range(cnt)]
        cache.set('languages_codes', languages_codes, 300)
        return languages_codes


def get_current_game():
    cached = cache.get('current_game', '')
    if cached:
        return cached
    else:
        # TODO: Add logging
        game = Game.objects.filter(initialized=True, start_time__isnull=False, end_time__isnull=True).order_by('-start_time')[0]
        cache.set('current_game', game.id)
        return game.id


def draw_question(player_id):
    player = Player.objects.get(pk=player_id)
    answers = Answer.objects.prefetch_related('question').filter(player_id=player.id)
    departments_list = get_departments_numbers()  # List like [1, 2, 3, 4]
    languages_list = get_languages_codes()  # List like ['fr', 'de', 'en']
    departments = []
    questions = []
    for i in range(0, len(answers)/len(departments_list)+1):
        departments += departments_list
    # We remove departments previously drawn
    for answer in answers:
        departments.remove(answer.question.question.department.number)
        questions.append(answer.question.question.number)
    # We draw a department and a language
    language = random.choice(languages_list)
    department = random.choice(departments)
    translations_list = Translation.objects.exclude(question__in=questions).filter(question__department__number=department, language__code=language)
    try:
        question = random.choice(translations_list)
    except IndexError:
        # TODO: Add logging
        translations_list = Translation.objects.all()
        question = random.choice(translations_list)
    return question


@app.task
def agi_question(player_number, phone_number):
    print "PLAYER: %s | PHONE: %s" % (phone_number, phone_number)
    current_game_id = get_current_game()
    game = Game.objects.get(pk=current_game_id)
    player = Player.objects.get(game=game, number=player_number)
    translation = draw_question(player.id)
    response = {'question': translation.question.number, 'response': translation.question.department.number,
                'player': player.id, 'game': game.id, 'phone': phone_number, 'translation': translation.id,
                'file': "%s-%s" % (translation.question.number, translation.language.code), 'type': 'PLAYER_ANSWERING'}
    message = {'playerId': player.number, 'number': phone_number, 'flag': translation.language.code,
               'type': 'PLAYER_ANSWERING'}
    send_amqp_message(message, "simulation.control")
    return response


@app.task
def agi_save(player_id, translation_id, answer, pickup_time, correct, phone_number):
    player = Player.objects.get(pk=player_id)
    translation = Translation.objects.get(pk=translation_id)
    phone = Phone.objects.get(number=phone_number)
    new_answer = Answer(player=player, question=translation, phone=phone, answer=answer, pickup_time=pickup_time,
                        hangup_time=timezone.now(), correct=correct)
    new_answer.save()
    #dmx_phone_answer_scene.apply_async(phone.number, correct)
    response = {'type': 'PLAYER_ANSWERED', 'playerId': player.number, 'correct': int(correct), 'number': phone.number}
    send_amqp_message(response, "simulation.control")


@app.task
def dmx_phone_answer_scene(phone_number, correct):
    phone = Phone.objects.get(number=phone_number)
    if correct:
        scene = "GREEN"
    else:
        scene = "RED"


@app.task
def play_end(result, area):
    cache.delete(area)


@app.task
def play_teuf():
    play_sound.apply_async(['call', 'front'])  #, link=play_end.s('front'))


@app.task
def play_ambiance():
    play_sound.apply_async(['ambiance', 'center'])  #, link=play_end.s('front'))


@app.task
def play_stop(pid):
    os.kill(pid, signal.SIGQUIT)
    # process = cache.get('front')
    # process.terminate()


@app.task
def play_sound(sound, area):
    if sound == 'ambiance':
        file = 'ambiance.wav'
    elif sound == 'call':
        file = 'call.wav'
    elif sound == 'intro':
        file = 'intro.wav'
    elif sound == 'powerdown':
        file = 'powerdown.wav'
    else:
        file = False

    if area == 'front':
        card = 'DGX'
    elif area == 'center':
        card = 'system'
    else:
        card = False

    if file and card:
        process = subprocess.Popen(['aplay', '-D',  'front:CARD=%s,DEV=0' % card,  '/home/gestionair/%s' % file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cache.set('front', process)
        print "PID: %s" % process.pid


@app.task
def call_center_loop(nb_players):
    min_phone_ringing = nb_players + 1
    disabled_phones = {}

    client = ari.connect('http://157.26.114.42:8088', 'paleo', 'paleo7top')

    while True:
        open_channels = client.channels.list()
        ringing_channels = [channel.json.get('name') for channel in open_channels if channel.json.get('state') == "Ringing"]

        if len(ringing_channels) < min_phone_ringing:
            for phone, timestamp in disabled_phones.copy().iteritems():
                if timezone.now() - datetime.timedelta(seconds=10) > timestamp:
                    del disabled_phones[phone]
            available_phones = [endpoint.json.get('resource') for endpoint in client.endpoints.list() if endpoint.json.get('state') == "online"]
            for channel in ringing_channels:
                if channel in available_phones:
                    available_phones.remove(channel)
            for phone in disabled_phones.keys():
                if phone in available_phones:
                    available_phones.remove(phone)
            if len(available_phones) > 0:
                phone = random.choice(available_phones)
                create_call_file('phone')
                disabled_phones[phone] = timezone.now()
