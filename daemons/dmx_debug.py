#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pysimpledmx
import sys

COM_PORT = '/dev/ttyUSB0'

mydmx = pysimpledmx.DMXConnection(COM_PORT)

dmx = sys.argv
scene = []

def send_dmx_scene(scene):
    if len(scene) > 0:
        for channel in scene:
            mydmx.setChannel(*channel)
        mydmx.render()


for i in range(len(dmx[2:])):
    scene.append((int(dmx[1])+i, int(dmx[2+i])))
print(scene)
send_dmx_scene(scene)
