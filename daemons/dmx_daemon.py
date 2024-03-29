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
import threading
import serial.tools.list_ports

logging.basicConfig()

COM_PORT = '/dev/ttyUSB0'

TEUF_STOP = threading.Event()

ports = serial.tools.list_ports.comports()

for (i, (path, name, _)) in enumerate(ports):
        if "ENR2OIBB" in _:
            print "Current port: %s" % path
            COM_PORT = path
        else:
            print "ENTTEC not found, using default port: %s" % COM_PORT

mydmx = pysimpledmx.DMXConnection(COM_PORT)

EFFECTS = {'bumper': 300, 'wheel': 310, 'borne': 320}
PHONES = {'1001': 1, '1002': 5, '1003': 9, '1004': 13, '1005': 17, '1006': 21, '1007': 25, '1008': 29, '1009': 33, '1010': 37}

print "DMX Controller Starting..."

def send_dmx_scene(scene):
    if len(scene) > 0:
        for channel in scene:
            mydmx.setChannel(*channel)
        mydmx.render()

def set_effect_color(scene, channel, d1, d2, d3, d4, d5, d6, d7):
    scene.append((channel + 0, d1))
    scene.append((channel + 1, d2))
    scene.append((channel + 2, d3))
    scene.append((channel + 3, d4))
    scene.append((channel + 4, d5))
    scene.append((channel + 5, d6))
    scene.append((channel + 6, d7))

def set_phone_color(scene, channel, r, g, b, w):
    scene.append((channel + 1, r))
    scene.append((channel + 0, g))
    scene.append((channel + 2, b))
    scene.append((channel + 3, w))

def lateuf():
    duration = 82
    while not TEUF_STOP.is_set() and duration > 0:
        scene = []
        set_effect_color(scene, EFFECTS['borne'], 255, 0, 0, 255, 0, 0, 0)
        set_effect_color(scene, EFFECTS['wheel'], 255, 0, 0, 0, 0, 0, 100)
        set_phone_color(scene, EFFECTS['bumper'], 255, 0, 0, 0)
        send_dmx_scene(scene)
	time.sleep(0.4)
        if TEUF_STOP.is_set():
            return
        scene = []
        set_effect_color(scene, EFFECTS['borne'], 255, 255, 0, 255, 0, 0, 0)
        set_effect_color(scene, EFFECTS['wheel'], 255, 255, 0, 0, 0, 0, 100)
        set_phone_color(scene, EFFECTS['bumper'], 255, 255, 0, 0)
        send_dmx_scene(scene)
        time.sleep(0.4)
        if TEUF_STOP.is_set():
            return
        scene = []
        set_effect_color(scene, EFFECTS['borne'], 0, 255, 0, 255, 0, 0, 0)
        set_effect_color(scene, EFFECTS['wheel'], 0, 255, 0, 0, 0, 0, 100)
        set_phone_color(scene, EFFECTS['bumper'], 0, 255, 0, 0)
        send_dmx_scene(scene)
        time.sleep(0.4)
        if TEUF_STOP.is_set():
            return
        scene = []
        set_effect_color(scene, EFFECTS['borne'], 0, 255, 255, 255, 0, 0, 0)
        set_effect_color(scene, EFFECTS['wheel'], 0, 255, 255, 0, 0, 0, 100)
        set_phone_color(scene, EFFECTS['bumper'], 0, 255, 255, 0)
        send_dmx_scene(scene)
        time.sleep(0.4)
        if TEUF_STOP.is_set():
            return
        scene = []
        set_effect_color(scene, EFFECTS['borne'], 0, 0, 255, 255, 0, 0, 0)
        set_effect_color(scene, EFFECTS['wheel'], 0, 0, 255, 0, 0, 0, 100)
        set_phone_color(scene, EFFECTS['bumper'], 0, 0, 255, 0)
        send_dmx_scene(scene)
        time.sleep(0.4)
        if TEUF_STOP.is_set():
            return
        scene = []
        set_effect_color(scene, EFFECTS['borne'], 255, 0, 255, 255, 0, 0, 0)
        set_effect_color(scene, EFFECTS['wheel'], 255, 0, 255, 0, 0, 0, 100)
        set_phone_color(scene, EFFECTS['bumper'], 255, 0, 255, 0)
        send_dmx_scene(scene)
        time.sleep(0.4)
        if TEUF_STOP.is_set():
            return
        duration -= 2.4
    default_scene()

def default_scene():
    scene = []
    set_effect_color(scene, EFFECTS['wheel'], 0, 138, 201, 0, 0, 0, 100)
    set_effect_color(scene, EFFECTS['borne'], 0, 138, 201, 255, 0, 0, 0)
    set_phone_color(scene, EFFECTS['bumper'], 0, 138, 221, 0)
    send_dmx_scene(scene)

def purple_bumper():
    scene = []
    set_phone_color(scene, EFFECTS['bumper'], 202, 10, 244, 0)
    send_dmx_scene(scene)
    time.sleep(5)
    scene = []
    set_phone_color(scene, EFFECTS['bumper'], 0, 138, 221, 0)
    send_dmx_scene(scene)

def red_bumper():
    scene = []
    set_phone_color(scene, EFFECTS['bumper'], 255, 0, 0, 0)
    send_dmx_scene(scene)
    time.sleep(5)
    scene = []
    set_phone_color(scene, EFFECTS['bumper'], 0, 138, 221, 0)
    send_dmx_scene(scene)

def wheel_small(scene):
    set_effect_color(scene, EFFECTS['wheel'], 0, 0, 0, 0, 240, 180, 255)
    send_dmx_scene(scene)
    time.sleep(1)
    default_scene()

def wheel_big(scene):
    set_effect_color(scene, EFFECTS['wheel'], 0, 0, 0, 0, 240, 180, 255)
    send_dmx_scene(scene)
    time.sleep(9)
    default_scene()

def start_wheel(size):
    scene = []
    scene.append((EFFECTS['wheel'] + 0,   0))  # CH1
    scene.append((EFFECTS['wheel'] + 1, 138))  # CH2
    scene.append((EFFECTS['wheel'] + 2, 201))  # CH3
    scene.append((EFFECTS['wheel'] + 3,   0))  # CH4
    scene.append((EFFECTS['wheel'] + 4, 220))  # CH5
    scene.append((EFFECTS['wheel'] + 5,   0))  # CH6
    scene.append((EFFECTS['wheel'] + 6, 255))  # CH7
    send_dmx_scene(scene)
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 210)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 200)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 190)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 180)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 170)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 160)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 140)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 120)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 100)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 70)])
    time.sleep(1)
    send_dmx_scene([(EFFECTS['wheel'] + 4, 30)])
    time.sleep(0.5)
    send_dmx_scene(scene)
    if size == 'big':
       wheel_big(scene)
    elif size == 'small':
       wheel_small(scene)
    return

def stop_scene(scene):
    for number, channel in PHONES.iteritems():
        set_phone_color(scene, channel, 0, 0, 0, 0)
    for number, channel in EFFECTS.iteritems():
        set_effect_color(scene, channel, 0, 0, 0, 0, 0, 0, 0)

#anim = [
#[(channel, color), (channel, color)],
#3 //sleep
#]

def play_remote_anim(anim):
   for instruction in anim:
       if type(instruction) is list:
           send_dmx_scene(instruction)
       elif type(instruction) is int or type(instruction) is float:
           time.sleep(instruction)


def play_dmx_from_event(event):
    scene = []
    if event['type'] == 'DMX_ANIM':
        t = threading.Thread(target=play_remote_anim, args=(event['anim'],))
        t.start()

    if event['type'] == 'START':
        default_scene()
    if event['type'] == 'GAME_START':
        default_scene()
        for number, channel in PHONES.iteritems():
            set_phone_color(scene, channel, 0, 138, 221, 0)
    if event['type'] == 'GAME_START_PLAYING':
        for number, channel in PHONES.iteritems():
            set_phone_color(scene, channel, 0, 0, 0, 0)
    elif event['type'] == 'PHONE_RINGING':
        number = event['number']
        channel = PHONES['%s' % number]
        set_phone_color(scene, channel, 0, 138, 221, 0)
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
        powerdown_scene()
    elif event['type'] == 'WHEEL_START':
        t = threading.Thread(target=start_wheel, args=(event['size'],))
        t.start()
    elif event['type'] == 'PLAYER_SCANNED':
        TEUF_STOP.set()
        default_scene()
        if event['state'] == 'SCANNED_WHEEL':
            set_phone_color(scene, EFFECTS['bumper'], 15, 255, 0, 0)
        elif event['state'] == 'SCANNED_PEN':
            t = threading.Thread(target=purple_bumper)
            t.start()
        else:
            t = threading.Thread(target=red_bumper)
            t.start()
    elif event['type'] == 'PLAY_SOUND' and event['sound'] == 'call':
        TEUF_STOP.clear()
        threading.Thread(target=lateuf).start()
    elif event['type'] == 'STOP':
        stop_scene(scene)
        TEUF_STOP.set()

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
except KeyboardInterrupt, pika.exceptions.ChannelClosed:
    channel.stop_consuming()
