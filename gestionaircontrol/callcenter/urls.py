# -*- coding: UTF-8 -*-
# urls.py
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

# Core Django imports
from django.conf.urls import *
from django.views.generic import TemplateView

# Third-party app imports

# paleo-2015-gestionair-control imports
from . import views

urlpatterns = [
    url(r'^game/queue/$', views.GameQueueListView.as_view(), name='game-queue-view'),
    url(r'^game/(?P<pk>\d+)/$', views.GameDetailView.as_view(), name='game-detail-view'),
    url(r'^game/(?P<pk>\d+)/edit/$', views.GameUpdateView.as_view(), name='game-update-view'),
    url(r'^game/(?P<pk>\d+)/initialize/$', views.GameInitializeRedirectView.as_view(), name='game-initialize-redirectview'),
    url(r'^game/(?P<pk>\d+)/cancel/$', views.GameCancelRedirectView.as_view(), name='game-cancel-redirectview'),
    url(r'^game/(?P<pk>\d+)/rebook/(?P<timeslot>\d{4}-\d{2}-\d{2} \d{2}:\d{2})/$', views.GameRebookRedirectView.as_view(), name='game-rebook-redirectview'),
    url(r'^game/(?P<pk>\d+)/rebook/$', views.GameRebookListView.as_view(), name='game-rebook-view'),
    url(r'^game/(?P<game>\d+)/delete/(?P<pk>\d+)/$', views.PlayerDeleteView.as_view(), name='player-delete-view'),
    url(r'^search/$', views.GameSearchView.as_view(), name='game-search-view'),
]
