from django.utils import timezone
import subprocess
import datetime
import logging
import requests
import asterisk
import random
import time
from gestionaircontrol.callcenter.models import Phone
from messaging import send_amqp_message
from threading import Thread
from gestionaircontrol.game.models import get_config_value
from config.settings import ASTERISK_URL, ASTERISK_USERNAME, ASTERISK_PASSWORD

from config.celery import app
from celery.contrib.abortable import AbortableTask, AbortableAsyncResult

logger = logging.getLogger(__name__)

AUTH = (ASTERISK_USERNAME, ASTERISK_PASSWORD)

DEMO_PHONE_NUMBER = 1201

class CallCenter:

    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.loop = Thread(target=game_loop, args=(self,))
        self.loop.start()
        self.start_game()
        self.open_channels = []

    def start_game(self):
        if self.is_running:
            return
        self.start_time = timezone.now()
        self.is_running = True

    def stop_game(self):
        self.is_running = False
        self.clean()
        send_amqp_message({'type': 'STOP'}, 'simulation')

    def demo_state(self):
        state = [channel['state'].upper() for channel in self.open_channels if int(channel['caller']['number']) == DEMO_PHONE_NUMBER]
        if len(state) > 0:
            return state[0]
        return 'FREE'


    def clean(self):
        logger.debug("DELETING CALL FILES...")
        subprocess.call('/usr/bin/sudo rm /var/spool/asterisk/outgoing/*.call', shell=True)
        logger.debug("CLOSING CHANNELS...")
        open_channels = requests.get(ASTERISK_URL + '/ari/channels', auth=AUTH).json()
        for channel in open_channels:
            if int(channel['caller']['number']) < 1100:
                requests.delete(ASTERISK_URL + '/ari/channels/%s' % channel['id'], auth=AUTH)
        #TODO: dynamic all phones
        for number in range(1001, 1011):
            send_amqp_message({'type': 'PHONE_STOPRINGING', 'number': number}, "simulation")

    def call_number(self, phone_number):
        logger.debug("Call phone number:  %s" % phone_number)
        phone_type = Phone.objects.get(number=phone_number).usage
        if phone_type == Phone.PUBLIC:
            wait = 20
            extension = 6666
            context = 'paleo-jukebox'
        elif phone_type == Phone.DEMO:
            wait = 10
            extension = 2001
            context = 'paleo-callcenter'
        elif phone_type == Phone.CENTER:
            wait = 10
            extension = 2001
            context = 'paleo-callcenter'
        else:
            context = None
        if context:
            logger.debug('call_asterisk')
            asterisk.call_phone_number(phone_number, wait, extension, context)
        else:
            pass


class Endpoint(object):
    DISABLED = 0 #not online
    AVAILABLE = 1 #onluine available to be called
    UP = 4 # phone channel up
    RINGING = 2 # means ringing or play answering
    COOLDOWN = 3 #phone has been used recently
    COOLDOWN_TIME = 10
    stop_ringing_sent = False
    count = 0
    last_ringing = False

    def __init__(self, number, callcenter):
        self.state = Endpoint.AVAILABLE
        self.number = number
        self.callcenter = callcenter

    def set_online(self, online):
        if online and self.state == Endpoint.DISABLED:
            self.state = Endpoint.AVAILABLE
            logger.debug("setOnline available %s " % self.number)
        if not online:
            logger.debug("setOnline disabled %s " % self.number)
            self.state = Endpoint.DISABLED

    def update_cooldown(self):
        if self.state == Endpoint.COOLDOWN:
            if timezone.now() - datetime.timedelta(seconds = Endpoint.COOLDOWN_TIME) > self.cooldown_start:
                logger.debug("END cooldown %s " % self.number)
                self.state = Endpoint.AVAILABLE

    def update_ringing(self, ringing):
        # check that we received twice to update
        if self.count < 2:
            if self.last_ringing == ringing:
                self.count += 1
            else:
                self.count = 0
            self.last_ringing = ringing
            return
        self.count = 0
        if self.state == Endpoint.RINGING and not ringing:
            self.cooldown()
        if ringing and not self.state == Endpoint.RINGING:
            logger.debug("Ringing phone with number %s state: %s" % (self.number, self.state))
            self.state = Endpoint.RINGING
            self.stop_ringing_sent = False

    def update_up(self, up):
        if up and not self.state == Endpoint.UP:
            logger.debug("Start up %s " % self.number)
            self.state = Endpoint.UP
        if self.state == Endpoint.UP and not up:
            self.cooldown()

    def cooldown(self):
        logger.debug("Start cooldown %s " % self.number)
        self.state = Endpoint.COOLDOWN
        self.cooldown_start = timezone.now()
        if not self.stop_ringing_sent:
            send_amqp_message({'type': 'PHONE_STOPRINGING', 'number': self.number}, "simulation")
        self.stop_ringing_sent = True


    def call(self):
        logger.debug("New phone call %s" % self.number)
        self.callcenter.call_number(self.number)


def game_loop(callcenter):
    logger.debug('game loop started')
    phones = {}
    while True:
        # check active endpoints and create or update our local phones
        try:
            open_channels = requests.get(ASTERISK_URL + '/ari/channels', auth=AUTH).json()
            # export channel for callcenter status api
            callcenter.open_channels = open_channels
            if callcenter.is_running:
                endpoints = requests.get(ASTERISK_URL + '/ari/endpoints', auth=AUTH).json()
                for endpoint in endpoints:
                    endpoint_number = int(endpoint['resource'])
                    # only callcenter numbers
                    # TODO: Do it from the database
                    if 1000 < endpoint_number < 1100:
                        if endpoint_number not in phones.keys():
                            logger.debug("create phone %s" % endpoint_number)
                            phones[endpoint_number] = Endpoint(endpoint_number, callcenter)
                        phones[endpoint_number].set_online(endpoint['state'] == 'online')

                # update phone states
                ringing_channels = [int(channel['caller']['number']) for channel in open_channels if channel['state'] == 'Ringing']
                logger.debug("ringing channels %s " % ringing_channels)
                for number, phone in phones.iteritems():
                    # trigger cooldown handling of phones
                    phone.update_up( number in [int(channel['caller']['number']) for channel in open_channels if channel['state'] == 'Up'])
                    phone.update_ringing(number in ringing_channels)
                    phone.update_cooldown()

                # check if we need to call phones
                ringing_phones = [phone for phone in phones.values() if phone.state == Endpoint.RINGING]
                logger.debug("ringing_phones length %s " % len(ringing_phones))
                if len(ringing_phones) < get_config_value('min_phone_ringing'):
                    available_phones = [phone for phone in phones.values() if phone.state == Endpoint.AVAILABLE]
                    logger.debug("available phones count %s " % len(available_phones))
                    if len(available_phones) > 0:
                        phone = random.choice(available_phones)
                        phone.call()
            time.sleep(1)
        except Exception as e:
            logger.error(e)
