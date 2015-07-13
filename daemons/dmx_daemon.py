from django.conf import settings
import pysimpledmx
import pika
import json
from gestionaircontrol.callcenter.models import Phone


COM_PORT = '/dev/ttyUSB0'

mydmx = pysimpledmx.DMXConnection(COM_PORT)




def send_dmx_scene(scene):
    for channel in scene:
        mydmx.setChannel(*channel)
        print "Channel (%s, %s)" % channel
    mydmx.render()

def set_dmx_color(scene, channel, r, g, b, w):
    if r:
        scene.append((1, 222))
        scene.append((2, 12))
    elif g:
        scene.append((1, 222))
        scene.append((2, 17))
    elif b:
        scene.append((1, 222))
        scene.append((2, 22))
    elif w:
        scene.append((1, 222))
        scene.append((2, 32))
    # scene.append((channel + 0, r))
    # scene.append((channel + 1, g))
    # scene.append((channel + 2, b))
    # scene.append((channel + 3, w))


def play_dmx_from_event(event):
    scene = []
    phones = {}
    phones_list = Phone.objects.filter(usage=Phone.CENTER).values('number', 'dmx_channel')
    for phone in phones_list:
        phones[phone.number] = phone.dmx_channel

    if event['type']=='GAME_START':
        for number, channel in phones.iteritems():
            set_dmx_color(scene, channel, 0, 0, 0, 100)
    elif event['type']=='PHONE_RINGING':
        number = event['number']
        channel = phones[number]
        set_dmx_color(scene, channel, 0, 0, 200, 0)
    elif event['type']=='PHONE_STOPRINGING':
        number = event['number']
        channel = phones[number]
        set_dmx_color(scene, channel, 0, 0, 0, 0)
    elif event['type']=='PLAYER_ANSWERING':
        number = event['number']
        channel = phones[number]
        set_dmx_color(scene, channel, 0, 0, 100, 0)
    elif event['type']=='PLAYER_ANSWERED':
        number = event['number']
        channel = phones[number]
        correct = event['correct']
        if correct:
            set_dmx_color(scene, channel, 0, 200, 0, 0)
        else:
            set_dmx_color(scene, channel, 200, 0, 0, 0)
    elif event['type']=='GAME_END':
        for number, channel in phones.iteritems():
            set_dmx_color(scene, channel, 0, 0, 0, 0)



def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        if 'type' in message:
            play_dmx_from_event(message)
    except:
        pass
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

parameters = pika.URLParameters('amqp://guest:guest@192.168.1.1:5672/%2F')
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(queue=queue_name, exchange='gestionair', routing_key='simulation')
channel.basic_consume(on_message, queue=queue_name)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
