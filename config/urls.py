# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [

    # Django Admin
    url(r'^admin/', include(admin.site.urls)),

    # Your stuff: custom urls includes go here
    url(r'^cc/', include("gestionaircontrol.callcenter.urls", namespace="cc")),

    url(r'^game/', include("gestionaircontrol.game.urls", namespace="game")),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

