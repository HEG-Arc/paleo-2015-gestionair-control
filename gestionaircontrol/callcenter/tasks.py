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
def create_call_file(phone, type):
    if type == 'public':
        wait = 20
        extension = 2003
        context = 'paleo-public'
    elif type == 'demo':
        wait = 10
        extension = 2001
        context = 'paleo-call'
    elif type == 'call':
        wait = 5
        extension = 2001
        context = 'paleo-call'
    else:
        context = None

    if context:
        c = Call('SIP/%s' % phone, wait_time=wait, retry_time=1, max_retries=1)
        x = Context(context, str(extension), '1')
        cf = CallFile(c, x)
        cf.spool()
        subprocess.call('/usr/bin/sudo chmod 660 /var/spool/asterisk/outgoing/*.call && /usr/bin/sudo chown asterisk:asterisk /var/spool/asterisk/outgoing/*.call', shell=True)
        send_amqp_message("{'call': context, 'phone': phone}", "asterisk.call")
    else:
        pass


@app.task
def init_simulation():
    game = cache.get_many(['game_start_time', 'current_game'])
    game_status = 'INIT'
    send_amqp_message("{'game': %s}" % game_status, "simulation.control")
    while game['game_start_time'] > timezone.now() - datetime.timedelta(seconds=settings.GAME_DURATION):
        # 00 : Intro
        if game_status == 'INIT':
            game_status = 'INTRO'
            cache.set('game_status', game_status)
            send_amqp_message("{'game': %s}" % game_status, "simulation.control")
        # 37 : Call center
        elif game_status == 'INTRO' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=37):
            game_status = 'CALL'
            cache.set('game_status', game_status)
            send_amqp_message("{'game': %s}" % game_status, "simulation.control")
        # 217 : Powerdown
        elif game_status == 'CALL' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=217):
            game_status = 'POWERDOWN'
            cache.set('game_status', game_status)
            send_amqp_message("{'game': %s}" % game_status, "simulation.control")
        # 247 : The END ;-)
        elif game_status == 'POWERDOWN' and game['game_start_time'] < timezone.now() - datetime.timedelta(seconds=247):
            game_status = 'END'
            cache.set('game_status', game_status)
            send_amqp_message("{'game': %s}" % game_status, "simulation.control")
    # Game is over!
    game_status = 'OVER'
    cache.set('game_status', game_status)
    send_amqp_message("{'game': %s}" % game_status, "simulation.control")
    # Delete cache
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
    return question.id


@app.task
def ami_interface(player_number, phone_number):
    current_game_id = get_current_game()
    game = Game.objects.get(pk=current_game_id)
    player = Player.objects.get(game=game, number=player_number)
    translation = draw_question(player.id)
    response = {'translation': translation.id, 'response': translation.question.department.number,
                'player': player.id, 'game': game.id, 'phone': phone_number}
    send_amqp_message(response, "simulation.control")
    return response


@app.task
def answer_to_db(player_id, translation_id, answer, pickup_time, hangup_time, correct, phone_number):
    player = Player.objects.get(pk=player_id)
    translation = Translation.objects.get(pk=translation_id)
    phone = Phone.objects.get(number=phone_number)
    new_answer = Answer(player=player, question=translation, phone=phone, answer=answer, pickup_time=pickup_time,
                        hangup_time=hangup_time, correct=correct)
    new_answer.save()
    response = {'answer': answer, 'phone': phone.number}
    send_amqp_message(response, "simulation.control")
    return True

"""
@app.task
def call_center(game_id):
    current_game_id = Game.objects.get(pk=game_id)
    list_players = current_game_id.player_set.all()
    list_phones = Phone.objects.all().filter(state="CENTER")
    num_players = len(list_players)
"""


@app.task
def generate_call():
    phone = Phone.objects.get(number=1102)
    type = phone.type
    create_call_file(phone, type)
