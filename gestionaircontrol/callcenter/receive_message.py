import pika
import json
import os
import glob
from threading import Thread


class Receive(Thread):

    connection = pika.BlockingConnection(pika.ConnectionParameters('157.26.114.42'))
    channel = connection.channel()

    print ' [*] Waiting for messages. To exit press CTRL+C'

    def callback(ch, method, properties, body):
        print " [x] Received %s" % body
        decoded_body = json.loads(body)
        if decoded_body['type'] == 'GAME_START':
            print decoded_body['type']
            min_phone_ringing = 2
            game_running = True
            # add business code

        if decoded_body['type'] == 'GAME_END':
            game_running = False
            print decoded_body['type']
            #remove call files
            r = glob.glob('/var/spool/asterisk/outgoing/*')
            for i in r:
                os.remove(i)

    channel.basic_consume(callback, queue='caller', no_ack=True)

    channel.start_consuming()