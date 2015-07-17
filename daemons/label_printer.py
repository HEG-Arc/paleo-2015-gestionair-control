# -*- coding: UTF-8 -*-
# sound_controller.py
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
import tempfile


import pika
import json
import subprocess

import logging
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics import barcode
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER


logging.basicConfig()


def do_print(data):
    pdf_file_name = tempfile.mktemp(".pdf")
    styles = getSampleStyleSheet()
    h1 = styles["h1"]
    h1.alignment=TA_CENTER
    h1.fontSize = 36
    h1.spaceBefore = 10
    h1.spaceAfter = 22
    normal = styles["Normal"]
    normal.alignment=TA_CENTER
    normal.fontSize = 16
    normal.spaceAfter = 18

    normal2 = styles["BodyText"]
    normal2.alignment=TA_CENTER
    normal2.fontSize = 16
    normal2.spaceAfter = 6

    doc = SimpleDocTemplate (pdf_file_name)
    doc.pagesize = (8*cm, 29*cm)
    doc.topMargin = 0
    doc.leftMargin = 0
    doc.rightMargin = 0
    parts = list()
    parts.append(Paragraph(data['name'], normal))
    languages = list()
    for lang in data['languages']:
        if lang['correct'] and lang['lang'] not in languages:
            languages.append(lang['lang'])

    parts.append(Paragraph(' '.join(languages), normal))
    #parts.append(Image(imagename, 4*cm, 4*cm))

    parts.append(Paragraph('%s' % data['score'], h1))

    d = barcode.createBarcodeDrawing("QR", width=4*cm, height=4*cm, barBorder=0, value="http://gestionair.ch/#/score/%s" % data['game'])
    d.hAlign = "CENTER"
    d.vAlign = "TOP"
    parts.append(d)

    parts.append(Paragraph('gestionair.ch', normal2))
    parts.append(Paragraph('code: %s' % data['game'], normal2))
    doc.build(parts)

    subprocess.Popen(["C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe", "", pdf_file_name])
    #TODO cups call
    #subprocess.Popen(["C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe", "", pdf_file_name])


def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        if 'type' in message and message['type']=='GAME_END' \
                and 'game' in message and 'scores' in message \
                and len(message['scores']) > 0:
            print message
            for data in message['scores']:
                data['game'] = message['game']
                do_print(data)
    except Exception as e:
        print e
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

#test
#do_print({'name': 'ASDkh ASDK ADJADDA', 'game': 345, 'score': 43, 'languages': [{'lang':'gb', 'correct': 0}, {'lang':'fr', 'correct': 1}, {'lang':'de', 'correct': 1}, {'lang':'de', 'correct': 1}]})
#exit()

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
