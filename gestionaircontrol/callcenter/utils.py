# -*- coding: UTF-8 -*-
# utils.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
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
import datetime
import os
import random
import pyglet
#import pygame
import subprocess
from pycall import CallFile, Call, Application, Context
import signal
import random
import ari
import time


# Core Django imports
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def get_next_start_time():
    next_start = timezone.now() + datetime.timedelta(minutes=3, seconds=33)
    return next_start