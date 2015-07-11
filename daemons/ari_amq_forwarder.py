import pika
import websocket
import requests
import json
from time import sleep

class ARIListener:
    app_name = 'ari_proxy'
    username = 'paleo'
    password = 'paleo7top'
    callback = None
    
    def __init__(self, callback):
        self.callback = callback
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://192.168.1.1:8088/ari/events?api_key=%s:%s&app=%s" % (self.username,
                                                                                               self.password,
                                                                                               self.app_name),
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()

    def on_message(self, ws, message):
        if self.callback:
            self.callback(message)
        

    def on_error(self, ws, error):
        print "### error :", error

    def on_close(self, ws):
        print "### closed ###"
        sleep(10)
        ari = ARIListener(self.callback)

    def on_open(self, ws):
        requests.post('http://192.168.1.1:8088/ari/applications/%s/subscription?eventSource=endpoint:SIP' % self.app_name,
                      auth=(self.username, self.password))


#TODO cleanup code and reconnect rabbit
send_channel = None

def on_message_listener(message):
    if send_channel:
        m = json.loads(message)
        if m['type'] == 'ChannelDestroyed':
            send_channel.basic_publish('gestionair',
                          'simulator.phone',
                           '{"type":"PHONE_STOPRINGING", "number": %s}' % m['channel']['caller']['number'] ,
                           pika.BasicProperties(content_type='application/json'))
                
##        send_channel.basic_publish('gestionair',
##                          'simulator.phone',
##                           message,
##                           pika.BasicProperties(content_type='application/json'))


def on_amq_open(connection):
    connection.channel(on_amq_channel_open)


def on_amq_channel_open(channel):
    global send_channel
    send_channel = channel
    ari = ARIListener(on_message_listener)


# Step #1: Connect to RabbitMQ
parameters = pika.URLParameters('amqp://guest:guest@192.168.1.1:5672/%2F')
connection = pika.SelectConnection(parameters=parameters,
                                   on_open_callback=on_amq_open)

try:
    # Step #2 - Block on the IOLoop
    connection.ioloop.start()

# Catch a Keyboard Interrupt to make sure that the connection is closed cleanly
except KeyboardInterrupt:

    # Gracefully close the connection
    connection.close()

    # Start the IOLoop again so Pika can communicate, it will stop on its own when the connection is closed
    connection.ioloop.start()
