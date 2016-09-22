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


import pika
import os
import logging
import requests
import ari
import threading
import random
import datetime
import json

# ---- nice to have
# TODO: getConfig dynamically?
# TODO: on config event change config
# ---- need hardware test
# TODO: detect off hook?
# BUG: either filter double delivery of events or make one app for endpoint and one for stasis channel
from requests import HTTPError

APP_NAME = "gestionair"
AMQP_HOST = '127.0.0.1'
API_HOST = '127.0.0.1'

MIN_PHONE_RINGING = 1
COOLDOWN_TIME = 15
CALL_TIMEOUT = 20

game_is_running = True

logging.basicConfig(level=logging.DEBUG)

client = ari.connect('http://10.0.75.2:8088', 'username', 'test')

phones = {} # for game
phones_other = {} # for other numbers if demo calls,..

last_event = {}


# OFFLINE -> [ ONLINE -> RINGING -- timeout --> COOLDOWN ]
#                                --   Up    --> LOGIN(play) -- hangup or timeout --> COOLDOWN
#                                                     --  3 DTMF codes     --> (GAME_OVER + hangup) --> COOLDOWN
#                                                                          --> ANSWERING --> Timeout/bad(play) --> COOLDOWN
#                                                                                        --> DTMF 1 answer -> Good/Bad (play) --> COOLDOWN
class Endpoint(object):
    OFFLINE = 0
    ONLINE = 1
    RINGING = 2
    LOGIN = 3
    ANSWERING = 4
    COOLDOWN = 5

    def __init__(self, number):
        self.state = Endpoint.ONLINE
        self.endpoint_state = Endpoint.ONLINE
        self.number = int(number)
        self.player_code = ''
        self.question = {}

    # only switch if needed
    def set_online(self, online):
        if online and self.endpoint_state == Endpoint.OFFLINE:
            self.state = Endpoint.ONLINE
            self.endpoint_state = Endpoint.ONLINE
            logging.debug("setOnline online %s " % self.number)
            send_amqp_message({'type': 'PHONE_ONLINE', 'number': self.number}, "simulation")
        if not online and self.endpoint_state == Endpoint.ONLINE:
            logging.debug("setOnline offline %s " % self.number)
            self.state = Endpoint.OFFLINE
            self.endpoint_state = Endpoint.OFFLINE
            send_amqp_message({'type': 'PHONE_OFFLINE', 'number': self.number}, "simulation")


    def call(self):
        self.state = Endpoint.RINGING
        call(self.number, CALL_TIMEOUT)

    def ringing(self):
        self.player_code = ''
        self.question = {}
        self.state = Endpoint.RINGING
        send_amqp_message({'type': 'PHONE_RINGING', 'number': self.number}, "simulation")
        check_and_start_phones()

    def ask_login(self, channel):
        self.state = Endpoint.LOGIN
        self.playback = channel.playWithId(media='sound:gestionair/entercode', playbackId='%s-entercode' % self.number)
        #TODO: timeout and hangup?


    def login(self, channel, digit):
        self.player_code += digit
        if len(self.player_code) == 3:
            #TODO disable ask_login timeout
            # get player
            try:
                self.question = requests.get('http://%s/game/agi/%s/%s/' % (API_HOST, self.player_code, self.number), timeout=0.5).json()
            except:
                self.question = None
            self.stop_current_playback()
            if self.question: # ok
                if self.question['over'] == 'over':
                    self.playback = channel.playWithId(media='sound:gestionair/over',
                                                       playbackId='%s-over' % self.number)
                    self.playback.on_event('PlaybackFinished', lambda obj, ev: self.safe_hangup(channel))

                else:
                    # TODO do we want to be able to answer during question? or only after?
                    self.state = Endpoint.ANSWERING
                    #queue
                    channel.playWithId(media='sound:gestionair/speech/%s' % self.question['file'],
                                                       playbackId='%s-question' % self.number)
                    channel.playWithId(media='sound:gestionair/correspondant',
                                       playbackId='%s-correspondant' % self.number)

                    # TODO: timeout wrong and hangup
            else:
                #play wrong code gestionair / wrong - code
                self.playback = channel.playWithId(media='sound:gestionair/wrong-code', playbackId='%s-wrongcode' % self.number)
                self.playback.on_event('PlaybackFinished', lambda obj, ev: self.safe_hangup(channel))

    def answer(self, channel, digit):
        # TODO disable timeouts
        # process answer
        # TODO why do we need to send response?
        response =  int(digit) == self.question['response']
        payload = {'answer_id': self.question['answer_id'], 'answer_key': int(digit),
                   'correct': response}
        requests.post('http://%s/game/agi/' % API_HOST, data=json.dumps(payload))

        self.stop_current_playback('%s-question' % self.number)
        self.stop_current_playback('%s-correspondant' % self.number)

        if response:
            self.playback = channel.playWithId(media='sound:gestionair/thankyou',
                                               playbackId='%s-wrongcode' % self.number)
        else:
            self.playback = channel.playWithId(media='sound:gestionair/wrong',
                                               playbackId='%s-wrong' % self.number)

        if self.question['last'] == 'last':
            self.playback = channel.playWithId(media='sound:gestionair/last',
                                               playbackId='%s-last' % self.number)

        self.playback.on_event('PlaybackFinished', lambda obj, ev: self.safe_hangup(channel))

    def safe_hangup(self, channel):
        try:
            channel.hangup()
        except HTTPError as e:
            # Ignore 404's, since channels can go away before we get to them
            if e.response.status_code != requests.codes.not_found:
                raise

    def stop_current_playback(self, id=None):
        try:
            if self.playback:
                self.playback.stop()
                self.playback = None
            if id:
                client.playbacks.stop(playbackId=id)
        except:
            pass

    def cooldown(self):
        self.state = Endpoint.COOLDOWN
        self.cooldown_start = datetime.datetime.now()
        check_and_start_phones()
        send_amqp_message({'type': 'PHONE_STOPRINGING', 'number': self.number}, "simulation")

    def update_cooldown(self):
        if datetime.datetime.now() - datetime.timedelta(seconds=COOLDOWN_TIME) > self.cooldown_start:
            self.state = Endpoint.ONLINE


# Helpers
def call(number, timeout=20):
    client.channels.originate(endpoint="SIP/%s" % number,
                                   app=APP_NAME, callerId=APP_NAME, appArgs="gestionair", timeout=timeout)


def clear_all_channels():
    for channel in client.channels.list():
        try:
            channel.hangup()
        except:
            pass


def get_phone(number):
    number = int(number)
    if 1000 < number < 1100:
        if number not in phones.keys():
            logging.debug("create phone %s" % number)
            phones[number] = Endpoint(number)

        return phones[number]
    else:
        if number not in phones_other.keys():
            logging.debug("create other phone %s" % number)
            phones_other[number] = Endpoint(number)

        return phones_other[number]


def check_and_start_phones():
    if game_is_running:
        ringing_phones = [phone for phone in phones.values() if phone.state == Endpoint.RINGING]
        # update cooldown
        for phone in [phone for phone in phones.values() if phone.state == Endpoint.COOLDOWN]:
            phone.update_cooldown()
        logging.debug("ringing_phones: %s" % len(ringing_phones))
        if len(ringing_phones) < int(MIN_PHONE_RINGING):
            available_phones = [phone for phone in phones.values() if phone.state == Endpoint.ONLINE]
            logging.debug("available_phones: %s" % len(available_phones))
            if len(available_phones) == 0:
                cooldown_phones = [phone for phone in phones.values() if phone.state == Endpoint.COOLDOWN]
                cooldown_phones.sort(key=lambda p: p.cooldown_start)
                if len(cooldown_phones) > 0:
                    available_phones = [cooldown_phones[0]]
            if len(available_phones) > 0:
                phone = random.choice(available_phones)
                phone.call()
                # loop to handle more phones needed
                check_and_start_phones()


# event handlers

# state change is also called when channel is added/removed to this endpoint
def on_endpoint_state_change(endpoint, ev):
    logging.debug(ev)
    phone = get_phone(endpoint.json["resource"])
    phone.set_online(endpoint.json['state'] == 'online')
    if phone.endpoint_state == Endpoint.ONLINE and len(endpoint.json['channel_ids']) == 0:
        phone.cooldown()


def on_stasis_start(channel, ev):
    logging.debug("stasis_start %s" % ev)
    phone = get_phone(ev['channel']['caller']['number'])
    phone.ask_login(channel.get('channel'))
    check_and_start_phones()


def on_channel_state_change(channel, ev):
    if channel.json['id'] in last_event and last_event[channel.json['id']] == ev['timestamp']:
        return
    last_event[channel.json['id']] = ev['timestamp']
    logging.debug("on_channel_state_change %s" % ev)
    logging.debug("%s: %s" %( channel.json['caller']['number'], channel.json['state']) )
    phone = get_phone(channel.json['caller']['number'])
    if channel.json['state'] == 'Ringing':
        phone.ringing()


def on_channel_dtmf_received(channel, ev):
    # skip multiple delivery
    if channel.json['id'] in last_event and last_event[channel.json['id']] == ev['timestamp']:
        return
    last_event[channel.json['id']] = ev['timestamp']
    logging.debug("on_channel_dtmf_received %s" % ev)
    phone = get_phone(channel.json['caller']['number'])
    # ev['digit']
    # ev['duration_ms']
    if phone.state == Endpoint.LOGIN:
        phone.login(channel, ev['digit'])
    elif phone.state == Endpoint.ANSWERING:
        phone.answer(channel, ev['digit'])


# -- debug
def on_channel_created(channel, ev):
    logging.debug("on_channel_created %s" % ev)


def on_playback_started(playback, ev):
    logging.debug("on_playback_started %s" % ev)


def on_playback_finished(playback, ev):
    logging.debug("on_playback_finished %s" % ev)


def on_channel_destroyed(channel, ev):
    logging.debug("on_channel_destroyed %s" % ev)


def on_stasis_end(channel, ev):
    logging.debug("on_stasis_end %s" % ev)


client.on_endpoint_event('EndpointStateChange', on_endpoint_state_change)
client.on_channel_event('StasisStart', on_stasis_start)
client.on_channel_event('ChannelCreated', on_channel_created)
client.on_channel_event('ChannelStateChange', on_channel_state_change)
client.on_channel_event('ChannelDtmfReceived', on_channel_dtmf_received)
client.on_playback_event('PlaybackStarted', on_playback_started)
client.on_playback_event('PlaybackFinished', on_playback_finished)
client.on_channel_event('ChannelDestroyed', on_channel_destroyed)
client.on_channel_event('StasisEnd', on_stasis_end)


# AMQP
def on_message(channel, method_frame, header_frame, body):
    global game_is_running
    try:
        message = json.loads(body)
        print message
        if 'type' in message:
            print message['type']
            if message['type'] == 'START':
                game_is_running = True
                check_and_start_phones()
            if message['type'] == 'STOP':
                game_is_running = False
                clear_all_channels()
            if message['type'] == 'CONFIG':
                pass
            if message['type'] == 'CALL':
                call(message['number'], message['timeout'])
    except Exception as e:
        logging.error(e)
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

parameters = pika.URLParameters('amqp://guest:guest@%s:5672/%%2F' % AMQP_HOST)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(queue=queue_name, exchange='gestionair', routing_key='simulation')
channel.basic_consume(on_message, queue=queue_name)

connection_send = pika.BlockingConnection(parameters=parameters)
channel_send = connection_send.channel()

def send_amqp_message(message, exchange):
    channel_send.basic_publish(exchange, 'simulation', json.dumps(message))
    logging.debug("SENT %s" % message)


def amqp_thread():
    try:
        channel.start_consuming()
    except KeyboardInterrupt, pika.exceptions.ChannelClosed:
        channel.stop_consuming()

t = threading.Thread(target=amqp_thread)
t.start()



# wait for websocket to conect for app to exist on asterisk api before trying to subscribe
def subscribe():
    client.applications.subscribe(applicationName=APP_NAME, eventSource="endpoint:SIP")
    # trigger update of endpoints
    for endpoint in client.endpoints.list():
        on_endpoint_state_change(endpoint, {})
    check_and_start_phones()

threading.Timer(1.0, subscribe).start()

client.run(apps=APP_NAME)
