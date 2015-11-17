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

from config.celery import app
from celery.contrib.abortable import AbortableTask, AbortableAsyncResult

logger = logging.getLogger(__name__)

# TODO: move to env
URL = 'http://192.168.1.1:8088'
AUTH = ('paleo', 'paleo7top')


# game loop ok
# demo loop ?
# public ?

class CallCenter:

    def __init__(self):
        self.is_running = False
        self.game_status = 'INIT'
        self.start_time = None
        self.gameloop_id = None

    def start_game(self):
        if self.is_running:
            return
        self.start_time = timezone.now()
        #create loop
        self.gameloop_id = game_loop.apply_async(self)

    def stop(self):
        self.game_status = 'STOP'
        self.clean()
        try:
            task = AbortableAsyncResult(self.gameloop_id)
            task.abort()
        except Exception as e:
            print e
        # STOP loop

    def clean(self):
        logger.debug("DELETING CALL FILES...")
        subprocess.call('/usr/bin/sudo rm /var/spool/asterisk/outgoing/*.call', shell=True)
        logger.debug("CLOSING CHANNELS...")
        open_channels = requests.get(URL + '/ari/channels', auth=AUTH).json()
        for channel in open_channels:
            if int(channel['caller']['number']) < 1100:
                requests.delete(URL + '/ari/channels/%s' % channel['id'], auth=AUTH)

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
        elif phone_type == Phone.CENTER and self.game_status == 'CALL': #TODO check
            wait = 10
            extension = 2001
            context = 'paleo-callcenter'
        else:
            context = None
        if context:
            asterisk.call_phone_number(phone_number, wait, extension, context)
        else:
            pass


class Endpoint(object):
    DISABLED = 0 #not online
    AVAILABLE = 1 #onluine available to be called
    RINGING = 2 # means ringing or play answering
    COOLDOWN = 3 #phone has been used recently
    COOLDOWN_TIME = 10

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
            if timezone.now() - datetime.timedelta(seconds=COOLDOWN_TIME) > self.cooldown_start:
                logger.debug("END cooldown %s " % self.number)
                self.state = Endpoint.AVAILABLE

    def update_ringing(self, ringing):
        if self.state == Endpoint.RINGING and not ringing:
            logger.debug("Start cooldown %s " % self.number)
            self.state = Endpoint.COOLDOWN
            self.cooldown_start = timezone.now()
            send_amqp_message({'type': 'PHONE_STOPRINGING', 'number': self.number}, "simulation")
        if ringing:
            self.state = Endpoint.RINGING
            logger.debug("Ringing phone with number %s " % self.number)

    def call(self):
        logger.debug("New phone call %s" % self.number)
        self.callcenter.call_number(self.number)



@app.task(bind=True, base=AbortableTask)
def game_loop(self, callcenter):
    min_phone_ringing = 1 # TODO move config
    phones = {}
    while not self.is_aborted():
        # check active endpoints and create or update our local phones
        endpoints = requests.get(URL + '/ari/endpoints', auth=AUTH).json()
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
        open_channels = requests.get(URL + '/ari/channels', auth=AUTH).json()
        ringing_channels = [int(channel['caller']['number']) for channel in open_channels if channel['state'] == 'Ringing']
        logger.debug("ringing channels %s " % ringing_channels)
        for number, phone in phones.iteritems():
            #trigger cooldown handling of phones
            phone.update_cooldown()
            phone.update_ringing(number in ringing_channels)

        # check if we need to call phones
        ringing_phones = [phone for phone in phones.values() if phone.state == Endpoint.RINGING]
        logger.debug("ringing_phones length %s " % len(ringing_phones))
        if len(ringing_phones) < min_phone_ringing:
            available_phones = [phone for phone in phones.values() if phone.state == Endpoint.AVAILABLE]
            logger.debug("available phones count %s " % len(available_phones))
            if len(available_phones) > 0:
                phone = random.choice(available_phones)
                phone.call()
        time.sleep(1)