# -*- coding: UTF-8 -*-
# forms.py
#
# Copyright (C) 2014 HES-SO//HEG Arc
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

# Core Django imports
from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

# Third-party app imports
from bootstrap3_datetime.widgets import DateTimePicker

# paleo-2015-gestionair-control imports
from .models import Timeslot
from gestionaircontrol.callcenter.models import Game, Player

class TimeslotCreationForm(forms.Form):
    start_time = forms.DateTimeField(widget=DateTimePicker(options={"format": "YYYY-MM-DD"}))
    end_time = forms.DateTimeField(widget=DateTimePicker(options={"format": "YYYY-MM-DD"}))
    duration = forms.IntegerField()
    booking_capacity = forms.IntegerField()
    booking_availability = forms.IntegerField()

    def create_timeslots(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        duration = self.cleaned_data['duration']
        booking_capacity = self.cleaned_data['booking_capacity']
        booking_availability = self.cleaned_data['booking_availability']
        while start_time + datetime.timedelta(minutes=duration) <= end_time:
            timeslot = Timeslot(start_time=start_time, duration=duration, booking_capacity=booking_capacity, booking_availability=booking_availability)
            timeslot.save()
            start_time = start_time + datetime.timedelta(minutes=duration)


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ['team']


class PlayerForm(ModelForm):

    class Meta:
        model = Player
        fields = ['name']


PlayerFormSet = inlineformset_factory(Game, Player, form=PlayerForm, extra=2)