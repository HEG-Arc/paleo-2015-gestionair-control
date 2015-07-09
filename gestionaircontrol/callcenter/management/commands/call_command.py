from django.core.management.base import CommandError
from daemon_command import DaemonCommand
import socket
from gestionaircontrol.callcenter.endpoints import get_online_endpoints, get_open_channels, return_phone

host = 'http://157.26.114.42'
port = 8088

server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_connect.connect((host, port))
num_players = 0
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

    def handle_noargs(self):
        """  """

        online_endpoints = get_online_endpoints()
        open_channels = get_open_channels()

        if game_running == True and num_players > open_channels:
