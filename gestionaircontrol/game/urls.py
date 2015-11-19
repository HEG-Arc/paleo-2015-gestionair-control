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

from . import views

urlpatterns = [
    url(r'^agi/(?P<player>\d+)/(?P<phone>\d+)/$', views.agi_request, name='ami-request'),
    url(r'^agi/$', views.agi_submit, name='ami-submit'),
    url(r'^start', views.start_game, name='game-start'),
    url(r'^status', views.game_status, name='game-status'),

    url(r'^status', views.game_state, name='game-state'),
    url(r'^api/register-player', views.register_player, name='register-player'),
    url(r'^api/print-player/(?P<player_id>\d+)', views.print_player, name='print-player'),
    url(r'^api/scan-code/(?P<player_id>\d+)', views.scan_player, name='scan-code'),
    url(r'^api/scan-code/[A](?P<code>\d+)', views.scan_code, name='scan-code'),
    url(r'^api/bumper', views.bumper, name='bumper'),
    url(r'^api/load-config', views.load_config, name='load-config'),
]
