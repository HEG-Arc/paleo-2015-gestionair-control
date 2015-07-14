# -*- coding: UTF-8 -*-
# sound_controller.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
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

from django.conf import settings
import pika
import json
import subprocess
import time
from threading import Thread

abort = {'front': False, 'center': False}


def aplayer(card, soundfile):
    def thread():
        print "Playing: %s on %s" % (soundfile, card)
        player = subprocess.Popen(['aplay', '-D',  'front:CARD=%s,DEV=0' % card,  '/home/gestionair/%s' % soundfile])
        while not abort[card] and player.returncode is None:
            time.sleep(0.5)
            player.poll()
        if player.returncode is None:
            player.kill()
        print "APLAYER END: %s " % player.returncode
    t = Thread(target=thread)
    t.start()


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
        aplayer(card, soundfile)

def play_sound_from_event(event):
    global abort
    if event['type']=='GAME_START':
        abort['center'] = False
        play_sound('intro', 'center')
    elif event['type']=='PHONE_RINGING':
        pass
    elif event['type']=='PHONE_STOPRINGING':
        pass
    elif event['type']=='PLAYER_ANSWERING':
        pass
    elif event['type']=='PLAYER_ANSWERED':
        pass
    elif event['type']=='GAME_END':
        play_sound('powerdown', 'center')
    elif event['type'] == 'STOP':
        abort['center'] = True
    if event['type'] == 'PLAY_SOUND':
        play_sound(event.sound, event.area)


def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        if 'type' in message:
            play_sound_from_event(message)
    except:
        pass
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

parameters = pika.URLParameters('amqp://guest:guest@192.168.1.1:5672/%2F')
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(queue=queue_name, exchange='gestionair', routing_key='simulation')
channel.basic_consume(on_message, queue=queue_name)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
