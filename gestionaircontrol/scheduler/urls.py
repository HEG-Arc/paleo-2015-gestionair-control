# -*- coding: UTF-8 -*-
# urls.py
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

# Core Django imports
from django.conf.urls import *
from django.views.generic import TemplateView

# Third-party app imports

# paleo-2015-gestionair-control imports
from . import views

urlpatterns = [
    url(r'^start/', views.start, name='start'),
    url(r'^status/', views.status, name='status'),
    url(r'^stop/sound/', views.sound_stop, name='sound-stop'),
    url(r'^stop/', views.stop, name='stop'),
    url(r'^demo/', views.demo, name='demo'),
    url(r'^call/', views.call, name='call'),
    url(r'^ring/(?P<number>\d+)/', views.ring, name='ring'),
    url(r'^ambiance/', views.ambiance, name='ambiance'),
    url(r'^timeslots/create/$', views.TimeslotCreateView.as_view(), name="timeslots-create"),
    url(r'^timeslots/all/$', views.TimeslotListView.as_view(), {'filter': 'all'}, name="timeslots-full-list"),
    url(r'^timeslots/free/$', views.TimeslotListView.as_view(), {'filter': 'free'}, name="timeslots-free-list"),
    url(r'^timeslots/$', views.TimeslotListView.as_view(), {'filter': 'current'}, name="timeslots-list"),
    url(r'^timeslot/(?P<pk>\d{4}-\d{2}-\d{2} \d{2}:\d{2})/$', views.TimeslotDetailView.as_view(), name='timeslot-detail-view'),
    url(r'^game/new/(?P<timeslot>\d{4}-\d{2}-\d{2} \d{2}:\d{2})/$', views.CreateGame.as_view(), name='game-create'),
]
