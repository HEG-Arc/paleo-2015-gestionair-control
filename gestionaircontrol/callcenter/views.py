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
import datetime
import json

# Core Django imports
from django.utils import timezone
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F
from django.views.decorators.csrf import csrf_exempt

# Third-party app imports
from extra_views import InlineFormSet, UpdateWithInlinesView

# paleo-2015-gestionair-control imports
from gestionaircontrol.callcenter.models import Game, Player
from gestionaircontrol.scheduler.forms import PlayerFormSet, GameForm
from gestionaircontrol.scheduler.models import Timeslot, Booking
from gestionaircontrol.callcenter.tasks import agi_question, agi_save


def agi_request(request, player, phone):
    agi = agi_question(player, phone)
    return JsonResponse(agi)

@csrf_exempt
def agi_submit(request):
    #if request.is_ajax():
    if request.method == 'POST':
            r = json.loads(request.body)
            print r
            print "player : %s" % r['player_id']
            agi_save.apply_async([r['player_id'], r['translation_id'], r['answer'], r['pickup_time'], r['correct'], r['phone_number']])
            msg = "OK"
    else:
        msg = "GET calls are not allowed for this view!"
    return HttpResponse(msg)

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
        games = Game.objects.prefetch_related('slot', 'players').annotate(nb_players=Count('players')).filter(canceled=False, slot__isnull=False, nb_players__gt=0, start_time__isnull=True).order_by('slot__timeslot__start_time', 'slot__booking_position')
        return games


class GameRebookListView(ListView):
    model = Timeslot
    template_name = 'callcenter/game_rebook.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GameRebookListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GameRebookListView, self).get_context_data(**kwargs)
        context['game'] = get_object_or_404(Game, pk=self.kwargs['pk'])
        return context

    def get_queryset(self):
        timeslots = Timeslot.objects.prefetch_related('bookings').annotate(num_bookings=Count('bookings')).filter(start_time__gte=timezone.now()-datetime.timedelta(minutes=20), num_bookings__lt=F('booking_availability'))
        return timeslots


class GameRebookRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'])
        timeslot = get_object_or_404(Timeslot, start_time=kwargs['timeslot'])
        booking = get_object_or_404(Booking, game=game)
        booking.timeslot = timeslot
        booking.save()
        return reverse('cc:game-detail-view', kwargs={'pk': kwargs['pk']})


class GameSearchView(ListView):
    template_name = 'callcenter/games_list.html'

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        if q:
            return Game.objects.filter(team__icontains=q)
        else:
            return Game.objects.filter()
