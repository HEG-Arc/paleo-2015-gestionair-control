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
from .views import WaitingView

# Third-party app imports

# paleo-2015-gestionair-control imports
from . import views

urlpatterns = [
    url(r'^countdown/json/', views.countdown, name='countdown-json'),
    url(r'^countdown/$', TemplateView.as_view(template_name='screen/countdown.html'), name="countdown"),
    url(r'^scheduler/json/', views.scheduler, name='scheduler-json'),
    url(r'^scheduler/$', TemplateView.as_view(template_name='screen/scheduler.html'), name="scheduler"),
    url(r'^waiting/$', WaitingView.as_view(), name="waiting"),
]
