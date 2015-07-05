# -*- coding: UTF-8 -*-
# views.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Benoît Vuille <benoit.vuille@he-arc.ch>
#            Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
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
import time
from threading import Thread
from datetime import datetime

# Core Django imports
from django.utils import timezone
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Count

# Third-party app imports
from extra_views import InlineFormSet, UpdateWithInlinesView

# paleo-2015-gestionair-control imports
from gestionaircontrol.callcenter.models import Game, Player
from gestionaircontrol.scheduler.forms import PlayerFormSet, GameForm


def home(request):
    """ Accueil du Call Center """
    text = """<h1>Bienvenue sur le Call Center</h1>
              <p>Application pour le Paléo !</p>"""
    return HttpResponse(text)


def beat():
    """ Declenche le timer """
    timer = 240
    while timer > 0:
        print(timer)
        timer = timer-1
        time.sleep()


def print_test(request):
    return HttpResponse(beat())


class TimeThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.seconds = 0

    def run(self):
        cpt = 240
        while cpt > 0:
            self.seconds = cpt
            cpt -= 1

            time.sleep(1)

    def get_seconds(self):
        return self.seconds


def start(request):

    print("Lancement thread")
    mon_thread = TimeThread()
    mon_thread.start()

    print("Affichage du temps")
    while True:
        sleep()
        print(mon_thread.get_seconds())

    text = """test"""
    return HttpResponse(text)


def sleep():
    time.sleep(1)


def date1(request):
    return render(request, 'date.html', {'date': timezone.now()})


def index(request):
    return render(request, 'web/index.html')


def addGroup(request):
    return render(request, 'web/ajouterGroupe.html')

def listGroup(request):
    #games = Game.find(limit=10)
    games = Game()

    print (games.team)
    return render(request, 'web/listeGroupe.html', {
        'games': games,
    })


class GameDetailView(DetailView):

    model = Game

    def get_context_data(self, **kwargs):
        context = super(GameDetailView, self).get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        game = get_object_or_404(Game.objects.prefetch_related('players'), pk=self.kwargs['pk'])
        return game


class PlayerDeleteView(DeleteView):

    model = Player

    def get_success_url(self):
        return reverse('cc:game-detail-view', kwargs={'pk': self.kwargs['game']})


class PlayerInline(InlineFormSet):
    model = Player
    fields = ['name',]
    max_num = 6
    extra = 6


class GameUpdateView(UpdateWithInlinesView):
    template_name = 'callcenter/game_update.html'
    model = Game
    form_class = GameForm
    inlines = [PlayerInline]

    def get_success_url(self):
        return reverse('cc:game-detail-view', kwargs={'pk': self.kwargs['pk']})


class GameInitializeRedirectView(RedirectView):
    permanent = False
    pattern_name = 'cc:game-detail-view'

    def get_redirect_url(self, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'])
        game.initialize_game()
        return super(GameInitializeRedirectView, self).get_redirect_url(*args, **kwargs)


class GameCancelRedirectView(RedirectView):
    permanent = False
    pattern_name = 'cc:game-detail-view'

    def get_redirect_url(self, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'])
        game.cancel_game()
        return super(GameCancelRedirectView, self).get_redirect_url(*args, **kwargs)


class GameQueueListView(ListView):
    model = Game
    template_name = 'callcenter/game_queue.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GameQueueListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GameQueueListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        games = Game.objects.prefetch_related('slot', 'players').annotate(nb_players=Count('players')).filter(canceled=False, slot__isnull=False, nb_players__gt=0).order_by('slot__timeslot__start_time')
        return games
