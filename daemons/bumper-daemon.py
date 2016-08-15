#!/usr/bin/python
# -*- coding: UTF-8 -*-
# bumper-reader.py
#
# Copyright (C) 2014 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of Wheel.
#
# Wheel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wheel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wheel. If not, see <http://www.gnu.org/licenses/>.

#standard python libs
import logging
import time
import requests
from evdev import InputDevice, ecodes, list_devices, categorize

logging.basicConfig()

API_URL = 'http://192.168.1.1/game/api/bumper'

while True:
    logging.info("Getting the device...")
    dev = InputDevice('/dev/input/event2')

    if dev:
        logging.info("We got the device...")
        dev.grab()
        logging.info("Starting the Bumper Reader daemon...")
        while True:
            try:
                for event in dev.read_loop():
                    if event.type == ecodes.EV_KEY:
                        data = categorize(event)
                        if data.keystate == 1:
                            # Bumper pressed
                            url = API_URL
                            r = requests.get(url)
            except IOError:
                logging.error("IOError")
                break
    time.sleep(2)

logging.info("Terminating the Bumper Reader daemon...")
