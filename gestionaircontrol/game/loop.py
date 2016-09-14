from django.utils import timezone

import logging
import requests

from messaging import send_amqp_message

from config.settings import ASTERISK_URL, ASTERISK_USERNAME, ASTERISK_PASSWORD


logger = logging.getLogger(__name__)

AUTH = (ASTERISK_USERNAME, ASTERISK_PASSWORD)

DEMO_PHONE_NUMBER = 1201

class CallCenter:

    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.start_game()

    def start_game(self):
        if self.is_running:
            return
        self.start_time = timezone.now()
        self.is_running = True
        send_amqp_message({'type': 'START'}, 'simulation')

    def stop_game(self):
        self.is_running = False
        send_amqp_message({'type': 'STOP'}, 'simulation')

    def demo_state(self):
        # TODO change to read phone events?
        open_channels = requests.get(ASTERISK_URL + '/ari/channels', auth=AUTH).json()
        state = [channel['state'].upper() for channel in open_channels if int(channel['caller']['number']) == DEMO_PHONE_NUMBER]
        if len(state) > 0:
            return state[0]
        return 'FREE'

    def call_number(self, phone_number):
        logger.debug("Call phone number:  %s" % phone_number)
        send_amqp_message({'type': 'CALL', 'number': phone_number, 'timeout': 20}, 'simulation')
