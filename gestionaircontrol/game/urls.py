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

# start callcenter_game_instance


# paleo-2015-gestionair-control imports
from . import views

urlpatterns = [
    url(r'^agi/(?P<player>\d+)/(?P<phone>\d+)/$', views.agi_request, name='ami-request'),
    url(r'^agi/$', views.agi_submit, name='ami-submit'),
    url(r'^start', views.start_game, name='game-start'),
    url(r'^status', views.game_state, name='game-status')
]
# start/init game
# stop/pause? game
# get status
# get scores
# register_new_player
# print_code
# playing == ami-submit && ami-request #  --- handle in ami-request limite reached [ compute_score ] ->  limitreached -- 
# scan_code == wheel[ scan_code ] --> ended (+know price)#
