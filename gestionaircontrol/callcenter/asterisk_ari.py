# ari from the package ari-py available at https://github.com/asterisk/ari-py
# install from source using "sudo ./setup.py install"
import ari
import random

client = ari.connect('http://157.26.114.42:8088', 'paleo', 'paleo7top')

# get the endpoints list
current_endpoints = client.endpoints.list()

# list of online endpoints
online_endpoints = []

# get the channels list
current_channels = client.channels.list()

# lists of different channels state
up_channels = []
ringing_channels = []
channels = []

num_players = 5


def get_online_endpoints():
    """For each endpoint, checks its state and adds it to the online list"""
    if len(current_endpoints) == 0:
        print "No endpoints currently"
    else:
        for endpoint in current_endpoints:
            if endpoint.json.get('state') == 'online':
                online_endpoints.append(endpoint)
    return online_endpoints


def get_channels():
    """For each channel, checks its state and adds it to the appropriate list"""
    if len(current_channels) == 0:
        print "No channels currently"
    else:
        for channel in current_channels:
            if channel.json.get('state') == "Up":
                up_channels.append(channel)
            elif channel.json.get('state') == "Ringing":
                ringing_channels.append(channel)
            else:
                channels.append(channel)
    return channels