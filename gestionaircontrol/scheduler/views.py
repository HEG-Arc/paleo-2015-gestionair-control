# -*- coding: UTF-8 -*-
# views.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of paleo2015.
#
# paleo2015 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paleo2015 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paleo2015. If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
import datetime
import collections
import json
import os

# Core Django imports
from django.utils import timezone
from django.core.cache import cache
from django.template.context import RequestContext
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, FormView, CreateView
from django.views.generic.detail import DetailView
from django.shortcuts import render_to_response, get_object_or_404, render
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.db.models import F, Count

# Third-party app imports

# paleo2015 imports
from gestionaircontrol.callcenter.tasks import create_call_file, callcenter_start, get_gestionair_status, demo_start, callcenter_stop
from gestionaircontrol.scheduler.messaging import send_amqp_message
from .models import Timeslot, Booking, Game
from .forms import TimeslotCreationForm, GameForm, PlayerFormSet


@login_required()
def start(request):
    result = callcenter_start()
    return JsonResponse(result)


@login_required()
def stop(request):
    result = callcenter_stop()
    return JsonResponse(result)


@login_required()
def demo(request):
    result = demo_start()
    return JsonResponse(result)


@login_required()
def ring(request, number):
    create_call_file.apply_async([number, ])
    success = True
    message = "Call was started"
    result = {'success': success, 'message': message}
    return JsonResponse(result)


@login_required()
def call(request):
    send_amqp_message({'type': 'PLAY_SOUND', 'sound': 'call', 'area': 'front'}, "simulation")
    success = True
    message = "Call was started"
    result = {'success': success, 'message': message}
    return JsonResponse(result)


@login_required()
def ambiance(request):
    send_amqp_message({'type': 'PLAY_SOUND', 'sound': 'ambiance', 'area': 'front'}, "simulation")
    success = True
    message = "Ambiance was started"
    result = {'success': success, 'message': message}
    return JsonResponse(result)


def status(request):
    status = get_gestionair_status()
    return JsonResponse(status)


class TimeslotListView(ListView):

    model = Timeslot

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TimeslotListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TimeslotListView, self).get_context_data(**kwargs)
        context['filter'] = self.kwargs['filter']
        return context

    def get_queryset(self):
        if self.kwargs['filter'] == 'all':
            time_slots = Timeslot.objects.prefetch_related('bookings').all()
        elif self.kwargs['filter'] == 'free':
            time_slots = Timeslot.objects.prefetch_related('bookings').annotate(Count('bookings')).filter(bookings__count__lt=F('booking_availability')).filter(start_time__gte=timezone.now()-datetime.timedelta(hours=1))
        else:
            time_slots = Timeslot.objects.prefetch_related('bookings').filter(start_time__gte=timezone.now()-datetime.timedelta(hours=1))
        return time_slots


class TimeslotDetailView(DetailView):

    model = Timeslot

    def get_context_data(self, **kwargs):
        context = super(TimeslotDetailView, self).get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        timeslot = get_object_or_404(Timeslot.objects.prefetch_related('bookings'), pk=self.kwargs['pk'])
        return timeslot


class TimeslotCreateView(FormView):
    template_name = 'scheduler/timeslot_creation_form.html'
    form_class = TimeslotCreationForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.create_timeslots()
        return super(TimeslotCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('scheduler:timeslots-list')


class CreateGame(CreateView):
    template_name = 'scheduler/game_create_form.html'
    model = Game
    form_class = GameForm

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        player_form = PlayerFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  player_form=player_form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        player_form = PlayerFormSet(self.request.POST)
        if form.is_valid() and player_form.is_valid():
            return self.form_valid(form, player_form)
        else:
            return self.form_invalid(form, player_form)

    def form_valid(self, form, player_form):
        self.object = form.save()
        player_form.instance = self.object
        player_form.save()
        timeslot = get_object_or_404(Timeslot, pk=self.kwargs['timeslot'])
        game = get_object_or_404(Game, pk=self.object.id)
        booking = Booking(timeslot=timeslot, game=game)
        booking.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, player_form):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  player_form=player_form))

    def get_success_url(self):
        return reverse('scheduler:timeslots-list')
