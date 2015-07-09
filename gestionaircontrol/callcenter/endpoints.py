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
open_channels = []

num_players = 5


def get_online_endpoints():
    """For each endpoint, checks its state and adds it to the online list"""
    if len(current_endpoints) == 0:
        print "No endpoints currently"
    else:
        print "Current endpoints:"
        for endpoint in current_endpoints:
            if endpoint.json.get('state') == 'online':
                online_endpoints.append(endpoint)
                print "Endpoint: %s | State: %s" % (endpoint.json.get('resource'), endpoint.json.get('state'))
    return online_endpoints


def get_open_channels():
    """For each channel, checks its state and adds it to the appropriate list"""
    if len(current_channels) == 0:
        print "No channels currently"
    else:
        print "Current channels:"
        for channel in current_channels:
            if channel.json.get('state') == "Up":
                up_channels.append(channel)
            elif channel.json.get('state') == "Ringing":
                ringing_channels.append(channel)
            else:
                open_channels.append(channel)
            print "Channel: %s | State: %s" % (channel.json.get('name'), channel.json.get('state'))
    return open_channels


def return_phone():
    """Selects a random endpoint in the open_endpoints list"""
    phone = random.choice(online_endpoints)
    print "Phone selected: %s" % phone.json.get('resource')
    return phone.json.get('resource')