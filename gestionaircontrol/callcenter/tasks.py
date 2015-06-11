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
import time
import os
import pyglet
import pygame
from pycall import CallFile, Call, Application, Context

# Core Django imports
from django.conf import settings

# Third-party app imports

# paleo-2015-gestionair-control imports
from config.celery import app
from gestionaircontrol.scheduler.messaging import send_amqp_message


funky = os.path.join(settings.STATIC_ROOT, 'sounds', 'game music FUNK.mp3')

@app.task
def play_call():
    send_amqp_message("{'play': 'funky'}", "player.start")
    # call = pyglet.media.load(funky, streaming=False)
    # player = call.play()
    pygame.mixer.init()
    pygame.mixer.music.load(funky)
    pygame.mixer.music.play(0)
    time.sleep(10)
    pygame.mixer.music.stop()


@app.task
def sound_control(sound):
    if sound == 'call':
        play_call.apply_async()


@app.task
def create_call_file(phone, context):
    asterisk_context = {'demo': 'paleo-call'}
    if context in asterisk_context:
        c = Call('SIP/%s' % phone)
        c.wait_time = 30
        c.retry_time = 60
        c.max_retries = 2
        x = Context(asterisk_context[context])
        cf = CallFile(c, x)
        cf.spool()
    else:
        pass
