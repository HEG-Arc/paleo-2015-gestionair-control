# ari from the package ari-py available at https://github.com/asterisk/ari-py
# install from source using "sudo ./setup.py install"
import ari
import logging
import random

logging.basicConfig(level=logging.ERROR)

client = ari.connect('http://157.26.114.42:8088', 'paleo', 'paleo7top')

# get the channels list
current_channels = client.channels.list()
up_channels = []
ringing_channels = []
open_channels = []

num_players = 5

# For each channel, checks its state and adds it in the right list
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
        print "%s which is %s" % (channel.json.get('name'), channel.json.get('state'))

print "Up %s" % up_channels
print "Ringing %s" % ringing_channels
print "Open %s" % open_channels

# Rings random channels in the open_channels list
i = 0
while i < num_players + 1:
    channel = open_channels.pop(random.choice(open_channels))
    channel.ring()
    i += 1


def stasis_start_cb(channel_obj, ev):
    """Handler for StasisStart event"""
    current_channels.append(channel_obj)


def stasis_end_cb(channel_obj, ev):
    """Handler for StasisEnd event"""

    print "Channel %s just left our application" % channel_obj.json.get('name')


def channel_state_change_cb(channel_obj, ev):
    """Handler for changes in a channel's state"""
    print "Channel %s is now: %s" % (channel_obj.json.get('name'),
                                     channel_obj.json.get('state'))
    if channel_obj.json.get('state') == "Up":
        up_channels.append(channel_obj)

    if channel_obj.json.get('state') == "Ringing":
        ringing_channels.append(channel_obj)

    else:
        open_channels.append(channel_obj)

client.on_channel_event('StasisStart', stasis_start_cb)
client.on_channel_event('ChannelStateChange', channel_state_change_cb)
client.on_channel_event('StasisEnd', stasis_end_cb)
 
client.run(apps='channel-state')