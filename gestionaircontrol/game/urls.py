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
    url(r'^agi/public/$', views.agi_public_request, name='ami-public-request'),
    url(r'^agi/$', views.agi_submit, name='ami-submit'),
    url(r'^start', views.start_game, name='game-start'),
    url(r'^stop', views.stop_game, name='game-stop'),
    url(r'^api/play-sound/(?P<sound>.*)', views.play_sound, name='play-sound'),
    url(r'^api/status', views.status, name='game-status'),
    url(r'^api/register-player', views.register_player, name='register-player'),
    url(r'^api/print-player/(?P<player_id>\d+)', views.print_player, name='print-player'),
    url(r'^api/scan-code/(?P<player_id>\d+)', views.scan_player, name='scan-code'),
    url(r'^api/scan-code/[A](?P<code>\d+)', views.scan_code, name='scan-code'),
    url(r'^api/scan-code/unlock', views.unlock_previous_player, name='scan-code-unlock'),
    url(r'^api/bumper', views.bumper, name='bumper'),
    url(r'^api/load-config', views.load_config, name='load-config'),
    url(r'^api/players-list', views.players_list, name='players-list'),
    url(r'^api/call/(?P<number>\d+)', views.call_phone, name='call-phone'),
    url(r'^api/stats/save', views.stats_save, name='stats-save'),
    url(r'^api/stats', views.stats, name='stats'),
    url(r'^test_score_sync/(?P<id>\d+)', views.test_score_sync),
    url(r'^frontend', views.frontend_redirect),
]
