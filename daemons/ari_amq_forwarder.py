import pika
import websocket
import requests

websocket.enableTrace(True)

def on_message(ws, message):
	print message



ws = websocket.WebSocketApp('ws://157.26.114.42:8088/ari/events?api_key=paleo:paleo7top&app=test', on_message=on_message, on_error=on_message, on_close=on_message)
ws.run_forever()

POST http://157.26.114.42:8088/ari/applications/test/subscription?eventSource=endpoint:SIP

def on_open(connection):
    connection.channel(on_channel_open)


def on_channel_open(channel):
    channel.basic_publish('exchange_name',
                          'routing_key',
                          'Test Message',
                          pika.BasicProperties(content_type='text/plain',
                                               type='example'))

# Step #1: Connect to RabbitMQ
parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/%2F')
connection = pika.SelectConnection(parameters=parameters,
                                   on_open_callback=on_open)

try:
    # Step #2 - Block on the IOLoop
    connection.ioloop.start()

# Catch a Keyboard Interrupt to make sure that the connection is closed cleanly
except KeyboardInterrupt:

    # Gracefully close the connection
    connection.close()

    # Start the IOLoop again so Pika can communicate, it will stop on its own when the connection is closed
    connection.ioloop.start()
