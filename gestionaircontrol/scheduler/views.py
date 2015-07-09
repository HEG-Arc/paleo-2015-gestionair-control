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
#import pyglet
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
from gestionaircontrol.callcenter.tasks import sound_control, create_call_file, init_simulation, play_teuf
from .messaging import send_amqp_message
from .models import Timeslot, Booking, Game
from .forms import TimeslotCreationForm, GameForm, PlayerFormSet


def get_game_status(game_start_time):
    if game_start_time:
        if timezone.now() < game_start_time + datetime.timedelta(seconds=settings.GAME_DURATION):
            current_status = "RUNNING"
        else:
            current_status = "FINISHED"
    else:
        current_status = "FINISHED"
    return current_status


def get_demo_status():
    demo_status = cache.get('demo_status')
    if not demo_status:
        demo_status = "FINISHED"
    return demo_status


@login_required()
def start(request):
    # Is it already working?
    game_start_time = cache.get('game_start_time', '')
    if game_start_time:
        current_status = get_game_status(game_start_time)
    else:
        current_status = "FINISHED"

    if current_status == "RUNNING":
        success = False
        message = "Game is already running"
    elif current_status == "FINISHED":
        # We can start a new counter
        start_time = timezone.now()
        # We get the current game
        try:
            current_game = Game.objects.filter(initialized=True, start_time__isnull=True)[0]
            current_game.start_time = start_time
            current_game.save()
        except IndexError:
            current_game = False
        if current_game:
            # We store the value in Redis
            cache.set_many({'game_start_time': start_time, 'current_game': current_game.id})
            # We initialize the new simulation
            init_simulation.apply_async()
            success = True
            message = "Game started"
            send_amqp_message("Simulation started", "simulator.start")
        else:
            success = False
            message = "No initialized game found!"

    game = cache.get_many(['game_start_time', 'current_game'])
    if 'game_start_time' not in game:
        game['start_time'] = None
    else:
        game['start_time'] = game['game_start_time'].isoformat()
    if 'current_game' not in game:
        game['current_game'] = None

    result = {'success': success, 'message': message, 'game': game['current_game'],
              'game_start_time': game['start_time']}
    return JsonResponse(result)


@login_required()
def stop(request):
    game = cache.get_many(['game_start_time', 'current_game'])
    game_start_time = game.get('game_start_time')
    current_status = get_game_status(game_start_time)

    if current_status == "RUNNING":
        # Game is running, we stop it
        cache.delete_many(['game_start_time', 'current_game'])
        success = True
        message = "Game was stopped"
    elif current_status == "FINISHED":
        # Game is paused, no need to stop it
        success = False
        message = "Game is already finished"

    cache.delete_many(['game_start_time', 'current_game'])
    result = {'success': success, 'message': message}
    return JsonResponse(result)


@login_required()
def demo(request):
    # Is it already working?
    demo_status = cache.get('demo_status')
    if not demo_status:
        demo_status = "FINISHED"

    if demo_status == "RUNNING":
        success = False
        message = "Demo is already running"
    elif demo_status == "FINISHED":
        # We can start a new demo
        # TODO: Start the demo ;-)
        create_call_file.apply_async(args=['6001', 'demo'])
        # We store the value in Redis (expiration is only for tests!)
        cache.set('demo_status', 'RUNNING', 8)
        success = True
        message = "Demo started"

    result = {'success': success, 'message': message, }
    return JsonResponse(result)


@login_required()
def call(request):
    # TODO: Do something here....
    # For tests only...
    play_teuf.apply_async()
    success = True
    message = "Call was started"
    result = {'success': success, 'message': message}
    return JsonResponse(result)


def countdown(request):
    game = cache.get_many(['game_start_time', 'current_game', 'game_status'])
    if 'game_start_time' in game:
        current_status = get_game_status(game['game_start_time'])
    else:
        current_status = "FINISHED"
    if current_status == "RUNNING":
        time_left = datetime.timedelta(seconds=settings.GAME_DURATION) - (timezone.now() - game['game_start_time'])
        game['time_left'] = time_left.seconds
    elif current_status == "FINISHED":
        game['time_left'] = "GAME OVER!"
    return JsonResponse(game)


def status(request):
    status = cache.get_many(['game_start_time', 'current_game'])
    status['game'] = get_game_status(status.get('game_start_time'))
    status['demo'] = get_demo_status()
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
