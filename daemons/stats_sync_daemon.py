# -*- coding: UTF-8 -*-
# simulate_players.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>, Boris Fritscher <boris.fritscher@he-arc.ch>
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
import pika
import logging
import requests
import os

logging.basicConfig(level=logging.DEBUG)

HOST = '127.0.0.1'
WEB_API = 'https://gestionair.ch/api/stats'

headers = {'Content-type': 'application/json; encoding=utf-8'}

auth = ('gestionair', 'Paleo7Top')

def on_message(channel, method_frame, header_frame, body):
    try:
        logging.debug('received: %s' % body)
        res = requests.post(WEB_API, headers=headers, data=body, auth=auth) #(os.getenv('WEB_API_USERNAME'), os.getenv('WEB_API_PASSWORD')))
        print res
        print res.text
        if res.status_code == 400 and 'code' in res.json():
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
        else:
            res.raise_for_status()
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    except Exception as e:
        logging.exception(e)
        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)


parameters = pika.URLParameters('amqp://guest:guest@%s/%%2F' % HOST)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
channel.basic_consume(on_message, queue='stats')
try:
    channel.start_consuming()
except KeyboardInterrupt, pika.exceptions.ChannelClosed:
    channel.stop_consuming()
