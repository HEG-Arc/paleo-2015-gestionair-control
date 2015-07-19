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

import json
import pika
import pysimpledmx
import logging
import time

logging.basicConfig()

COM_PORT = '/dev/ttyUSB0'

mydmx = pysimpledmx.DMXConnection(COM_PORT)

EFFECTS = {'strobe': 101}
PHONES = {'1001': 1, '1002': 5, '1003': 9, '1004': 13, '1005': 17, '1006': 21, '1007': 25, '1008': 29, '1009': 33, '1010': 37}

print "DMX Controller Starting..."

def send_dmx_scene(scene):
    if len(scene) > 0:
        for channel in scene:
            mydmx.setChannel(*channel)
        mydmx.render()

def set_phone_color(scene, channel, r, g, b, w):
    scene.append((channel + 1, r))
    scene.append((channel + 0, g))
    scene.append((channel + 2, b))
    scene.append((channel + 3, w))

def powerdown_scene():
    scene = []
    # Strobe
    scene.append((EFFECTS['strobe'], 255))  # CH1 intensité
    scene.append((EFFECTS['strobe'] + 1, 255))  # CH2 vitesse
    scene.append((EFFECTS['strobe'] + 6, 40))  # CH7 mode (35-69 zone 1-3)
    # Tous téléphones bleu
    for number, channel in PHONES.iteritems():
        set_phone_color(scene, channel, 0, 0, 255, 0)
    send_dmx_scene(scene)
    scene = []
    # Attendre 2 secondes
    time.sleep(2)
    # Stop le strobo
    scene.append((EFFECTS['strobe'], 0))  # CH1 intensité
    scene.append((EFFECTS['strobe'] + 6, 40))  # CH7 mode (35-69 zone 1-3)
    send_dmx_scene(scene)
    scene = []
    # Fade out
    for i in range(1, 5):
        for number, channel in PHONES.iteritems():
            set_phone_color(scene, channel, 0, 0, 250 - i * 50, 0)
        send_dmx_scene(scene)
        scene = []
        time.sleep(1)
    # Black
    for number, channel in PHONES.iteritems():
        set_phone_color(scene, channel, 0, 0, 0, 0)
    send_dmx_scene(scene)


def stop_scene(scene):
    for number, channel in PHONES.iteritems():
        set_phone_color(scene, channel, 0, 0, 0, 0)


def play_dmx_from_event(event):
    scene = []

    if event['type'] == 'GAME_START':
        for number, channel in PHONES.iteritems():
            set_phone_color(scene, channel, 0, 0, 255, 0)
    if event['type'] == 'GAME_START_PLAYING':
        for number, channel in PHONES.iteritems():
            set_phone_color(scene, channel, 0, 0, 0, 0)
    elif event['type'] == 'PHONE_RINGING':
        number = event['number']
        channel = PHONES['%s' % number]
        set_phone_color(scene, channel, 0, 0, 255, 0)
    elif event['type'] == 'PHONE_STOPRINGING':
        number = event['number']
        channel = PHONES['%s' % number]
        set_phone_color(scene, channel, 0, 0, 0, 0)
    elif event['type'] == 'PLAYER_ANSWERING':
        number = event['number']
        channel = PHONES['%s' % number]
        set_phone_color(scene, channel, 100, 0, 100, 0)
    elif event['type'] == 'PLAYER_ANSWERED':
        number = event['number']
        channel = PHONES['%s' % number]
        correct = event['correct']
        if correct:
            set_phone_color(scene, channel, 0, 255, 0, 0)
        else:
            set_phone_color(scene, channel, 255, 0, 0, 0)
    elif event['type'] == 'GAME_END':
        # TODO: Détacher le proc
        powerdown_scene()
    elif event['type'] == 'STOP':
        stop_scene(scene)

    send_dmx_scene(scene)


def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        print message
        if 'type' in message:
            print message['type']
            play_dmx_from_event(message)
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
