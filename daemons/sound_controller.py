# -*- coding: UTF-8 -*-
# sound_controller.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>, Boris Fritscher <boris.fritscher@he-arc.ch>
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
import logging

logging.basicConfig()

abort = {'front': False, 'center': False}


def aplayer(area, card, soundfile, loop=False, callback=None, volume=50):
    def thread():
        print "Playing: %s on %s" % (soundfile, card)
        command = ['mplayer', '-ao', 'alsa:device=hw=%s.0' % card,  '/home/gestionair/%s' % soundfile, '-volume', '%s' % volume]
        if loop:
            command.append('-loop')
            command.append('0')
        player = subprocess.Popen(command)
        while not abort[area] and player.returncode is None:
            time.sleep(0.5)
            player.poll()
        if player.returncode is None:
            player.kill()
        elif callback:
            callback()

        print "APLAYER END: %s " % player.returncode
    t = Thread(target=thread)
    t.start()


def play_sound(sound, area, volume=None):
    callback = None
    loop = None
    if volume is None:
        volume = 30
    if sound == 'ambiance':
        abort[area] = True
        time.sleep(0.6)
        abort[area] = False
        soundfile = 'ambiance.wav'
        loop = True
        if volume is None:
              volume = 30
    elif sound == 'call':
        soundfile = 'call.wav'
        abort[area] = True
        time.sleep(0.6)
        abort[area] = False
        #callback = lambda: play_sound('ambiance', area)
        if volume is None:
            volume = 100
    elif sound == 'intro':
        soundfile = 'intro.wav'
    elif sound == 'powerdown':
        soundfile = 'powerdown.wav'
    else:
        soundfile = False

    if area == 'front':
        card = '2'
    elif area == 'center':
        card = '0'
    else:
        card = False

    if soundfile and area:
        print "PLAYING %s %s" % (soundfile, area)
        aplayer(area, card, soundfile, loop=loop, callback=callback, volume=volume)


def play_sound_from_event(event):
    volume = 50
    if 'volume' in event:
        volume = event['volume']
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
        abort[event['area'] or 'center'] = True
    if event['type'] == 'PLAY_SOUND':
        abort[event['area']] = False
        play_sound(event['sound'], event['area'], volume=volume)



def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        if 'type' in message:
            print message
            play_sound_from_event(message)
    except Exception as e:
        print e
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
