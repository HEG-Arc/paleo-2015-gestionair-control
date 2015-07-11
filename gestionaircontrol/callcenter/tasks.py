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
import time
import requests
from celery.contrib.abortable import AbortableTask, AbortableAsyncResult


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

URL = 'http://192.168.1.1:8088'
AUTH = ('paleo', 'paleo7top')


@app.task
def create_call_file(phone):
    print "PHONE %s" % phone
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
        wait = 60
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


@app.task(bind=True, base=AbortableTask)
def init_simulation(self):
    loop_task = None
    play_intro_task_id = None
    play_powerdown_task_id = None

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

    while not self.is_aborted():
        while game['game_start_time'] > timezone.now() - datetime.timedelta(seconds=settings.GAME_DURATION):
            # 00 : Intro
            if game_status == 'INIT':
                game_status = 'INTRO'
                play_intro_task_id = play_sound('intro', 'center')
                cache.set('callcenter', game_status)
                send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
            # 37 : Call center
            elif game_status == 'INTRO' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=37):
                loop_task = call_center_loop.apply_async([len(players_list)])
                game_status = 'CALL'
                cache.set('callcenter', game_status)
                send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
            # 217 : Powerdown
            elif game_status == 'CALL' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=117):
                loop_task.abort()
                play_powerdown_task_id = play_sound('powerdown', 'center')
                game_status = 'POWERDOWN'
                cache.set('callcenter', game_status)
                #TODO: compute score



                #Ordered array from 1st place to nth.
                #languages ordered by their in game appearence
                #{'name': 'a', 'score': 100, 'languages': [{'lang':'code', correct: 0}]}
                scores = []
                message = {"game": game_status, "type": "GAME_END", "scores": scores}
                send_amqp_message(message, "simulation.caller")
            # 247 : The END ;-)
            elif game_status == 'POWERDOWN' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=147):
                game_status = 'END'
                cache.set('callcenter', game_status)
                send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
                cache.delete('callcenter_loop')
        # Game is over!
        game_status = 'STOP'
        cache.set('callcenter', game_status)
        send_amqp_message('{"game": "%s"}' % game_status, "simulation.control")
        # Delete cache
        cache.delete_many(['game_start_time', 'current_game', 'callcenter_loop'])

    # Task is aborted!
    print "MAIN GAME LOOP ABORTED!!!"
    try:
        loop_task.abort()
    except:
        print "UNABLE TO ABORT MAIN LOOP"
    try:
        play_intro_task = AbortableAsyncResult(play_intro_task_id)
        play_intro_task.abort()
    except:
        print "UNABLE TO ABORT PLAY INTRO"
    try:
        play_powerdown_task = AbortableAsyncResult(play_powerdown_task_id)
        play_powerdown_task.abort()
    except:
        print "UNABLE TO ABORT PLAY POWERDOWN"

    game_status = 'STOP'
    cache.set('callcenter', game_status)
    scores = []
    message = {"game": game_status, "type": "GAME_END", "scores": scores}
    send_amqp_message(message, "simulation.caller")
    cache.delete_many(['game_start_time', 'current_game'])


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


def draw_question(player_id=None):
    if player_id:
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
    else:
        translations_list = Translation.objects.all()
        question = random.choice(translations_list)
    return question


@app.task
def agi_question(player_number, phone_number):
    print "PLAYER: %s | PHONE: %s" % (phone_number, phone_number)
    phone = Phone.objects.get(number=phone_number)
    if phone.usage == Phone.CENTER:
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
    else:
        translation = draw_question()
        response = {'question': translation.question.number, 'response': translation.question.department.number,
                    'player': 0, 'game': 0, 'phone': phone_number, 'translation': translation.id,
                    'file': "%s-%s" % (translation.question.number, translation.language.code), 'type': 'PLAYER_ANSWERING'}
    return response


@app.task
def agi_save(player_id, translation_id, answer, pickup_time, correct, phone_number):
    phone = Phone.objects.get(number=phone_number)
    if phone.usage == Phone.CENTER:
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


@app.task(bind=True, base=AbortableTask)
def aplayer(self, card, soundfile):
    while not self.is_aborted():
        subprocess.call(['aplay', '-D',  'front:CARD=%s,DEV=0' % card,  '/home/gestionair/%s' % soundfile])


def play_sound(sound, area):
    if sound == 'ambiance':
        soundfile = 'ambiance.wav'
    elif sound == 'call':
        soundfile = 'call.wav'
    elif sound == 'intro':
        soundfile = 'intro.wav'
    elif sound == 'powerdown':
        soundfile = 'powerdown.wav'
    else:
        soundfile = False

    if area == 'front':
        card = 'DGX'
    elif area == 'center':
        card = 'system'
    else:
        card = False

    if soundfile and area:
        audio_player = aplayer.apply_async([card, soundfile])
        cache.set('player_%s' % sound, audio_player.id)
        return audio_player.id

    return False


@app.task
def clean_callcenter():
    subprocess.call('/usr/bin/sudo rm /var/spool/asterisk/outgoing/*.call', shell=True)
    open_channels = requests.get(URL + '/ari/channels', auth=AUTH).json()
    for channel in open_channels:
        if int(channel['caller']['number']) < 1100:
            requests.delete(URL + '/ari/channels/%s' % channel['id'], auth=AUTH)
    print "ALL CLEAN! BYE"


@app.task(bind=True, base=AbortableTask)
def call_center_loop(self, nb_players):
    min_phone_ringing = nb_players + 1
    disabled_phones = {}

    while not self.is_aborted():
        for phone, timestamp in disabled_phones.copy().iteritems():
            if timezone.now() - datetime.timedelta(seconds=15) > timestamp:
                del disabled_phones[phone]
        
        open_channels = requests.get(URL + '/ari/channels', auth=AUTH).json()
        ringing_channels = [channel['caller']['number'] for channel in open_channels if channel['state'] == "Ringing"]

        if len(ringing_channels) + len(disabled_phones.keys()) < min_phone_ringing:
            endpoints = requests.get(URL + '/ari/endpoints', auth=AUTH).json()
            available_phones = [endpoint['resource'] for endpoint in endpoints if endpoint['state'] == "online" and int(endpoint['resource']) > 1000 and int(endpoint['resource']) < 1100]
            for channel in ringing_channels:
                if channel in available_phones:
                    available_phones.remove(channel)
            for phone in disabled_phones.keys():
                if phone in available_phones:
                    available_phones.remove(phone)
            if len(available_phones) > 0:
                phone = random.choice(available_phones)
                create_call_file(phone)
                disabled_phones[phone] = timezone.now()
        time.sleep(1)
    print "IT'S TIME TO CLEAN-UP!"
    clean_callcenter.apply_async()


def get_gestionair_status():
    callcenter_status = False
    demo_status = False
    public_status = False
    status = cache.get_many(['callcenter', 'demo', 'public'])

    callcenter = status.get('callcenter', '')
    if callcenter and callcenter != 'STOP':
        callcenter_status = True

    demo = status.get('demo', '')
    if demo and demo != 'STOP':
            demo_status = True

    public = status.get('public', '')
    if public and public != 'STOP':
            public_status = True

    return {'callcenter': callcenter_status, 'demo': demo_status, 'public': public_status}


def callcenter_start():
    state = get_gestionair_status()
    if state['callcenter']:
        message = "Game is already running"
        success = False
        return {'success': success, 'message': message}

    start_time = timezone.now()
    # We get the current game
    try:
        current_game = Game.objects.filter(initialized=True, start_time__isnull=True)[0]
        current_game.start_time = start_time
        current_game.save()
    except IndexError:
        current_game = None

    if current_game:
        # We store the value in Redis
        cache.set_many({'game_start_time': start_time, 'current_game': current_game.id, 'callcenter': 'STARTING'})
        # We initialize the new simulation
        loop = init_simulation.apply_async()
        cache.set('callcenter_loop', loop)
        success = True
        message = "Game started"
    else:
        success = False
        message = "No initialized game found!"

    return {'success': success, 'message': message}


def demo_start():
    state = get_gestionair_status()
    if state['demo']:
        message = "Demo is already running"
        success = False
    else:
        create_call_file.apply_async(['1201'])
        cache.set('demo', True, 8)
        success = True
        message = "Demo started"
    return {'success': success, 'message': message, }


@app.task
def callcenter_stop():
    loop = cache.get('callcenter_loop', False)
    if loop:
        loop.abort()

    scores = []
    message = {"game": "STOP", "type": "GAME_END", "scores": scores}
    send_amqp_message(message, "simulation.caller")
    success = True
    message = "Game was stopped"
    return {'success': success, 'message': message, }
