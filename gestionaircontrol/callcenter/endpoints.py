# ari from the package ari-py available at https://github.com/asterisk/ari-py
# install from source using "sudo ./setup.py install"
import ari
import random

client = ari.connect('http://157.26.114.42:8088', 'paleo', 'paleo7top')

# get the endpoints list
current_endpoints = client.endpoints.list()
online_endpoints = []

num_players = 5


def start():
    """For each endpoint, checks its state and adds it to the online list"""
    if len(current_endpoints) == 0:
        print "No channels currently"
    else:
        print "Current channels:"
        for endpoint in current_endpoints:
            if endpoint.json.get('state') == 'online':
                online_endpoints.append(endpoint)
                print "Endpoint: %s | State: %s" % (endpoint.json.get('resource'), endpoint.json.get('state'))


def return_phone():
    """Selects a random endpoint in the open_endpoints list"""
    phone = random.choice(online_endpoints)
    print phone.json.get('resource')
    return phone.json.get('resource')


def stop():
    pass

client.run(apps="endpoints")