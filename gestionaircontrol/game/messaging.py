# -*- coding: UTF-8 -*-
# messaging.py
#
# Copyright (C) 2014 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of paleo-2015-gestionair-control.
#
# paleo-2015-gestionair-control is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paleo-2015-gestionair-control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paleo-2015-gestionair-control. If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
import celery
from kombu import Producer, Exchange
from kombu import Connection
from kombu.pools import connections
from threading import Thread
import time


# Core Django imports
from django.conf import settings

# Third-party app imports

# paleo-2015-gestionair-control imports

AMPQ_EXCHANGE = 'gestionair'

connection_broker = Connection(settings.BROKER_URL)


def send_amqp_message(message, routing):
    def thread():
        print "New message: %s" % message

        def send(count):
            try:
                with connections[connection_broker].acquire(block=True) as connection:
                    exchange = Exchange(name=AMPQ_EXCHANGE, type="topic", channel=connection)
                    exchange.declare()
                    publisher = Producer(channel=connection, exchange=exchange)
                    publisher.publish(message, routing_key=routing)
                    publisher.close()
                    print "Sent..."
            except Exception as e:
                if count < 10000:
                    print e
                    time.sleep(0.1)
                    send(count + 1)
                else:
                    print "FAILED"
        send(0)

    t = Thread(target=thread)
    t.start()