# -*- coding: UTF-8 -*-
# simulate_players.py
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
import BaseHTTPServer

from django.conf import settings
import pika
import json
import logging
import random
import requests
import math
import time
from threading import Thread, Timer

logging.basicConfig(level=logging.DEBUG)

HOST = '127.0.0.1'
MIN_PLAYERS = 4
PHONE_NUMBERS = [1001 + i for i in range(10)]

# FROM https://github.com/Marak/faker.js/blob/master/lib/locales/fr/name/first_name.js
NAMES = [
      'Enzo',
      'Lucas',
      'Mathis',
      'Nathan',
      'Thomas',
      'Hugo',
      'Théo',
      'Tom',
      'Louis',
      'Raphaël',
      'Clément',
      'Léo',
      'Mathéo',
      'Maxime',
      'Alexandre',
      'Antoine',
      'Yanis',
      'Paul',
      'Baptiste',
      'Alexis',
      'Gabriel',
      'Arthur',
      'Jules',
      'Ethan',
      'Noah',
      'Quentin',
      'Axel',
      'Evan',
      'Mattéo',
      'Romain',
      'Valentin',
      'Maxence',
      'Noa',
      'Adam',
      'Nicolas',
      'Julien',
      'Mael',
      'Pierre',
      'Rayan',
      'Victor',
      'Mohamed',
      'Adrien',
      'Kylian',
      'Sacha',
      'Benjamin',
      'Léa',
      'Clara',
      'Manon',
      'Chloé',
      'Camille',
      'Ines',
      'Sarah',
      'Jade',
      'Lola',
      'Anaïs',
      'Lucie',
      'Océane',
      'Lilou',
      'Marie',
      'Eva',
      'Romane',
      'Lisa',
      'Zoe',
      'Julie',
      'Mathilde',
      'Louise',
      'Juliette',
      'Clémence',
      'Célia',
      'Laura',
      'Lena',
      'Maëlys',
      'Charlotte',
      'Ambre',
      'Maeva',
      'Pauline',
      'Lina',
      'Jeanne',
      'Lou',
      'Noémie',
      'Justine',
      'Louna',
      'Elisa',
      'Alice',
      'Emilie',
      'Carla',
      'Maëlle',
      'Alicia',
      'Mélissa'
    ]

active_players = []
phones_ringing = {}


def thread():
    time.sleep(5)
    while True:
        if len(active_players) < MIN_PLAYERS:
            create_player()
        time.sleep(20)

t = Thread(target=thread)
t.start()


class ari_handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        if self.path == '/ari/endpoints':
            self.wfile.write(json.dumps(
                [{
                    'resource': phone_number,
                    'state': 'online'
                } for phone_number in PHONE_NUMBERS]
            ))
        if self.path == '/ari/channels':
            self.wfile.write(json.dumps(
                [{
                    'caller': {'number': phone_number},
                    'state': 'Ringing'
                } for phone_number in phones_ringing.keys() if phones_ringing[phone_number]]
            ))
        self.wfile.close()

    def log_message(self, format, *args):
        return


def web():
    server_address = ('', 8088)
    httpd = BaseHTTPServer.HTTPServer(server_address, ari_handler)
    httpd.serve_forever()

t2 = Thread(target=web)
t2.start()


# SIMULATE Player Inputs
def create_player():
    payload = {
        'name': random.choice(NAMES),
        'npa': int(math.floor(random.random() * 100) + 2000),
        'email': 'nospam@example.com'
    }
    res = requests.post('http://%s/game/api/register-player' % HOST, json=payload)
    player = res.json()
    requests.get('http://%s/game/api/print-player/%d' % (HOST, player['id']))
    logging.debug('player %d created' % player['id'])


def answer_question(payload):
    logging.debug('answered question %s' % json.dumps(payload))
    requests.post('http://%s/game/agi/' % HOST, json=payload)


def answer_phone(phone_number):
    logging.debug('answered phone %d' % phone_number)
    if len(active_players) == 0:
        return
    player_id = random.choice(active_players)
    res = requests.get('http://%s/game/agi/%d/%d' % (HOST, player_id, phone_number))
    question = res.json()
    if random.random() > 0.5:
        pressed_key = question['response']
    else:
        pressed_key = random.randint(1, 7)
    payload = {
        'answer_id': question['answer_id'],
        'answer_key': pressed_key,
        'correct': int(pressed_key == question['response'])

    }
    Timer(2.0, answer_question, [payload]).start()


def scan_code(player_id):
    requests.get('http://%s/game/api/scan-code/%d' % (HOST, player_id))
    logging.debug('scanned player %d' % player_id)


def push_bumper():
    requests.get('http://%s/game/api/bumper' % HOST)
    logging.debug('bumper')


def stop_phone_ringing(phone_number):
    phones_ringing[phone_number] = False


def start_phone_ringing(phone_number):
    phones_ringing[phone_number] = True
    Timer(5.0, stop_phone_ringing, [phone_number]).start()


def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        if message['type'] == 'PLAYER_PRINTED':
            active_players.append(message['playerId'])

        if message['type'] == 'PHONE_RINGING':
            missed_call = random.random() < 0.15
            start_phone_ringing(message['number'])
            if not missed_call:
                answer_phone(message['number'])

        if message['type'] == 'PLAYER_LIMIT_REACHED':
            continue_playing = random.random() < 0.05
            if not continue_playing:
                active_players.remove(message['playerId'])
                # TODO: queue?
                scan_code(message['playerId'])

        if message['type'] == 'PLAYER_SCANNED':
            if message['state'] == 'SCANNED_WHEEL':
                push_bumper()

    except Exception as e:
        logging.exception(e)
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


parameters = pika.URLParameters('amqp://guest:guest@%s/%%2F' % HOST)
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
