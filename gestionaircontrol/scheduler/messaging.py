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
import pika
from kombu import Producer, Queue, Exchange

# Core Django imports

# Third-party app imports
from amqp import RecoverableConnectionError

# paleo-2015-gestionair-control imports

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='simulator')
channel.close()

# connection = celery.current_app.pool.acquire()
# exchange = Exchange(name=AMPQ_EXCHANGE, type="topic", channel=connection)
# exchange.declare()
#
# queue = Queue(name="simulator", exchange=exchange, routing_key='#', channel=connection)
# queue.declare()
# queue = Queue(name="caller", exchange=exchange, routing_key='simulation.caller', channel=connection)
# queue.declare()
#
# CONNECTION = connection
# EXCHANGE = exchange
#publisher = Producer(channel=connection, exchange=exchange)


def send_amqp_message(message, routing):
    """Send a message to a specific queue on RabbitMQ."""
    new_channel = connection.channel()
    new_channel.basic_publish(exchange='', routing_key=routing, body=message)
    new_channel.close()
