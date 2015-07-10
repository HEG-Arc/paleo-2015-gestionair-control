from django.core.management.base import CommandError
from daemon_command import DaemonCommand
from gestionaircontrol.callcenter.tasks import create_call_file
import random
import ari
import datetime
from django.utils import timezone


class Command(DaemonCommand):
    help = 'Manages the calls'

    disabled_phones = {}
    min_phone_ringing = 2
    game_running = True

    def loop_callback(self):
        """ When a new game starts """

        client = ari.connect('http://157.26.114.42:8088', 'paleo', 'paleo7top')

        while self.game_running:
            open_channels = client.channels.list()
            ringing_channels = [channel.json.get('name') for channel in open_channels if channel.json.get('state') == "Ringing"]

            if len(ringing_channels) < self.min_phone_ringing:
                for phone, timestamp in self.disabled_phones.copy().iteritems():
                    if timezone.now() - datetime.timedelta(seconds=10) > timestamp:
                        del self.disabled_phones[phone]
                available_phones = [endpoint.json.get('resource') for endpoint in client.endpoints.list() if endpoint.json.get('state') == "online"]
                for channel in ringing_channels:
                    if channel in available_phones:
                        available_phones.remove(channel)
                for phone in self.disabled_phones.keys():
                    if phone in available_phones:
                        available_phones.remove(phone)
                if len(available_phones) > 0:
                    phone = random.choice(available_phones)
                    create_call_file(phone)
                    self.disabled_phones[phone] = timezone.now()

    def exit_callback(self):
        """ When a game ends """
        self.game_running = False