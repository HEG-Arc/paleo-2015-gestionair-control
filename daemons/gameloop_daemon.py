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
import logging
import requests
import os
import ari
import threading

# TODO: on STOP clear all channels, stop new calls
# TODO: on START start calling
# TODO: getConfig dynamically?
# TODO: push other events? lke demo phone
# TODO: detect off hook?
# BUG: either filter double delivery of events or make one app for endpoint and one for stasis channel

APP_NAME = "gestionair"

logging.basicConfig(level=logging.DEBUG)

client = ari.connect('http://10.0.75.2:8088', 'username', 'test')

phones = {}

last_event = {}


class Endpoint(object):
    OFFLINE = 0
    ONLINE = 1
    ANSWERING = 4
    RINGING = 2
    COOLDOWN = 3

    def __init__(self, number):
        self.state = Endpoint.ONLINE
        self.endpoint_state = Endpoint.ONLINE
        self.number = number

    # only switch if needed
    def set_online(self, online):
        if online and self.endpoint_state == Endpoint.OFFLINE:
            self.state = Endpoint.ONLINE
            self.endpoint_state = Endpoint.ONLINE
            logging.debug("setOnline online %s " % self.number)
            #TODO send event
        if not online and self.endpoint_state == Endpoint.ONLINE:
            logging.debug("setOnline offline %s " % self.number)
            self.state = Endpoint.OFFLINE
            self.endpoint_state = Endpoint.OFFLINE
            # TODO send event

    def cooldown(self):
        #TODO timer
        self.state = Endpoint.COOLDOWN

    def ringing(self):
        #TODO timer
        self.state = Endpoint.RINGING




def call(number):
    client.channels.originate(endpoint="PJSIP/%s" % number,
                                   app=APP_NAME, callerId=APP_NAME, appArgs="gestionair", timeout=20)


# wait for websocket to conect for app to exist on asterisk api before trying to subscribe
def subscribe():
    client.applications.subscribe(applicationName=APP_NAME, eventSource="endpoint:PJSIP")
    # run checkAndStartPhones

threading.Timer(1.0, subscribe).start()


def get_phone(number):
    if 1000 < number < 1100:
        if number not in phones.keys():
            logging.debug("create phone %s" % number)
            phones[number] = Endpoint(number)

        return phones[number]
    return None


# state change is also called when channel is added/removed to this endpoint
def on_endpoint_state_change(endpoint, ev):
    logging.debug(ev)
    phone = get_phone(endpoint.json["resource"])
    if phone:
        phone.set_online(endpoint.json['state'] == 'online')
        if phone.endpoint_state == Endpoint.ONLINE and len(endpoint.json['channel_ids']) == 0:
            phone.cooldown()
            # run checkAndStartPhones


def on_stasis_start(channel, ev):
    logging.debug("stasis_start %s" % ev)
    # playback getCode
    # run checkAndStartPhones


def on_channel_created(channel, ev):
    logging.debug("on_channel_created %s" % ev)


def on_channel_state_change(channel, ev):
    logging.debug("on_channel_state_change %s" % ev)
    logging.debug("%s: %s" %( channel.json['caller']['number'], channel.json['state']) )
    phone = get_phone(channel.json['caller']['number'])
    if phone and channel.json['state'] == 'Ringing':
        phone.ringing()


def on_channel_dtmf_received(channel, ev):
    # skip multiple delivery
    if channel.json['id'] in last_event and last_event[channel.json['id']] == ev['timestamp']:
        return
    last_event[channel.json['id']] = ev['timestamp']
    logging.debug("on_channel_dtmf_received %s" % ev)
    # ev['digit']
    # ev['duration_ms']
    #if state logging
        # append DTMF
        # if 3 then
            # state getQuestion
    #if answering
        # process answer


def on_playback_started(playback, ev):
    logging.debug("on_playback_started %s" % ev)
    #u'target_uri': u'channel:1473756899.17',


def on_playback_finished(channel, ev):
    logging.debug("on_playback_finished %s" % ev)
    #u'target_uri': u'channel:1473756899.17', u'state': u'done'}
    # if state answering? bad answer
    # hangup


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


client.run(apps=APP_NAME)