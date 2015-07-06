# -*- coding: UTF-8 -*-
# admin.py
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
from django.contrib import admin

# Third-party app imports

# paleo-2015-gestionair-control imports
from .models import Question, Translation, Language, Department, Phone, Game, Player, Answer


class QuestionAdmin(admin.ModelAdmin):
    pass


class TranslationAdmin(admin.ModelAdmin):
    pass


class LanguageAdmin(admin.ModelAdmin):
    pass


class DepartmentAdmin(admin.ModelAdmin):
    pass


class PhoneAdmin(admin.ModelAdmin):
    pass


class GameAdmin(admin.ModelAdmin):
    pass

class PlayerAdmin(admin.ModelAdmin):
    pass

class AnswerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Question, QuestionAdmin)
admin.site.register(Translation, TranslationAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Phone, PhoneAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Answer, AnswerAdmin)
