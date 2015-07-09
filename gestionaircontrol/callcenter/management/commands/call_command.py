from django.core.management.base import CommandError
from daemon_command import DaemonCommand
import gestionaircontrol.callcenter.asterisk_ari as asterisk_ari
from gestionaircontrol.callcenter.tasks import create_call_file

num_players = 6
game_running = False


class Command(DaemonCommand):
    help = 'Manages the calls'

    def loop_callback(self, num_players):
        """ When a new game starts """
        num_players = num_players
        game_running = True

    def exit_callback(self):
        """ When a game ends """
        game_running = False

    def handle_noargs(self, **options):
        """ Make calls on the open channels """

        # get the list of endpoints in state 'online'
        online_endpoints = asterisk_ari.get_online_endpoints()
        print online_endpoints

        # get the channels
        channels = asterisk_ari.get_channels()

        while game_running is False and len(channels) < num_players and len(online_endpoints) > 0:
            phone = asterisk_ari.return_phone(online_endpoints)
            online_endpoints.remove(phone)
            channels.append(phone)
            print "Online endpoints: %s" % online_endpoints
            print "Open channels: %s" % channels
            type = 'public'
            create_call_file(phone.json.get('resource'), type)
            online_endpoints.append(phone)