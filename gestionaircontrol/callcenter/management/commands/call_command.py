from django.core.management.base import CommandError
from daemon_command import DaemonCommand
import gestionaircontrol.callcenter.endpoints as endpoints
from gestionaircontrol.callcenter.tasks import create_call_file

host = 'http://157.26.114.42'
port = 8088

#server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_connect.connect((host, port))
num_players = 5
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

        open_endpoints = endpoints.get_online_endpoints()

        if game_running is False and num_players > len(open_endpoints):
            phone = endpoints.return_phone()
            create_call_file(phone, type)
            print phone