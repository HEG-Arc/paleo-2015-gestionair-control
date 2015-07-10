from django.core.management.base import CommandError
from daemon_command import DaemonCommand
import gestionaircontrol.callcenter.asterisk_ari as asterisk_ari
from gestionaircontrol.callcenter.tasks import create_call_file
import random

num_players = 6
game_running = True


class Command(DaemonCommand):
    help = 'Manages the calls'

    def loop_callback(self):
        """ When a new game starts """
        #num_players = num_players
        #game_running = True

        # get the list of endpoints in state 'online'
        online_endpoints = asterisk_ari.get_online_endpoints()
        print online_endpoints

        # get the channels; empty in the beginning
        channels = asterisk_ari.get_channels()

        #  and len(channels) < num_players and len(online_endpoints) > 0
        while game_running:
            phone = random.choice(online_endpoints)
            channels.append(phone)
            print "Online endpoints: %s" % online_endpoints
            print "Channels ringing: %s" % channels
            create_call_file(phone.json.get('resource'))
            del online_endpoints[:]
            online_endpoints = asterisk_ari.get_online_endpoints()
            online_endpoints.remove(phone)
            channels.remove(phone)

    def exit_callback(self):
        """ When a game ends """
        game_running = False

