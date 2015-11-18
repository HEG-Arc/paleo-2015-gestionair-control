# -*- coding: UTF-8 -*-
# views.py
#
# Copyright (C) 2013 HES-SO//HEG Arc
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wheel.  If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
import string
import logging
import time
import datetime
from random import randrange
import pysimpledmx
from threading import Thread

# Core Django imports
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.conf import settings


# Third-party app imports

# Wheel imports
from .models import Prize


SCORECODES = {
    'A': 0, 'B': 25, 'C': 50, 'D': 100, 'E': 200, 'F': 500
}

FREECODES = ['1A1', '2A2', '3A3']

ADMINCODES = {
    101: 'booth-admin-kids', 102: 'booth-admin-stats', 104: 'booth-admin-refresh', 105: 'booth-admin-light-off', 106: 'booth-admin-shutdown'
}

COM_PORT = '/dev/ttyUSB0'


def validate_code(code):
    # The code is in the form '32X242C3'
    code = code.lower()
    checksum = 0
    for char in code[:-1]:
        if char.isdigit():
            checksum += int(char)
        else:
            checksum += int(string.lowercase.index(char))
    if checksum % 10 == int(code[-1]):
        return True
    return False


def scan(request, code):
    if validate_code(code):
        logging.info("Valid code received: %s" % code)
        # We test the code
        try:
            if code[-2] == 'Z' and int(code[:3]) in ADMINCODES:
                logging.debug("Admin code %s - %s" % (code[:3], ADMINCODES[int(code[:3])]))
                return HttpResponseRedirect(reverse(ADMINCODES[int(code[:3])]))
            elif code[-2] in SCORECODES:
                # We check if the code is already in the database
                try:
                    quiz = Quiz.objects.get(code=code)
                    if quiz.prize:
                        # This is a cheater ;-)
                        return HttpResponseRedirect(reverse('booth-cheater', args=(quiz.id,)))
                    else:
                        # Display the score
                        return HttpResponseRedirect(reverse('booth-score', args=(quiz.id,)))
                except Quiz.DoesNotExist:
                    quiz = Quiz(code=code, score=SCORECODES[code[-2]], terminal=code[0])
                    quiz.save()
                    return HttpResponseRedirect(reverse('booth-score', args=(quiz.id,)))
            else:
                # The code is invalid, sorry
                logging.warning("Code format not recognized: %s" % code)
                return HttpResponseRedirect(reverse('wrong-code', args=(code,)))
        except IndexError:
            return HttpResponseRedirect(reverse('wrong-code', args=('WRONG',)))
    else:
        logging.warning("Code is not valid: %s" % code)
        return HttpResponseRedirect(reverse('wrong-code', args=(code,)))


def prize(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    past_prize = int(request.session.get('prize', 12))
    logging.info("Past_prize: %s" % past_prize)
    random_prize = get_random_prize(past_prize)
    quiz.prize = random_prize
    quiz.save()
    random_prize.stock -= 1
    random_prize.save()
    request.session['prize'] = random_prize.id
    return render_to_response('booth/prize.html', {
        'quiz': quiz,
        'prize': random_prize,
    }, context_instance=RequestContext(request))


def prize_kids(request):
    past_prize = int(request.session.get('prize', 12))
    logging.info("Past_prize: %s" % past_prize)
    random_prize = get_random_prize(past_prize)
    random_prize.stock -= 1
    random_prize.save()
    request.session['prize'] = random_prize.id
    return render_to_response('booth/prize.html', {
        'prize': random_prize,
    }, context_instance=RequestContext(request))


def get_random_prize(past_prize):
    prizes_list = Prize.objects.all().filter(stock__gt=0)
    # We build a dict with all available prizes
    prizes_dict = {}
    total_percent = 0
    for prize in prizes_list:
        prizes_dict[prize.id] = prize.percentage
        if prize.percentage != 100:
            total_percent += prize.percentage
    # We build a list with all prizes
    weighted_prizes_list = []
    for p in prizes_dict:
        if prizes_dict[p] != 100:
            for i in range(0, prizes_dict[p]):
                weighted_prizes_list.append(p)
        else:
            for i in range(0, 100-total_percent):
                weighted_prizes_list.append(p)
    # We randomly choose one prize in the list
    prize = past_prize
    # while prize == past_prize:
    prize = weighted_prizes_list[randrange(len(weighted_prizes_list))]
    logging.info("Random prize: %s" % prize)
    random_prize = get_object_or_404(Prize, pk=prize)
    return random_prize



