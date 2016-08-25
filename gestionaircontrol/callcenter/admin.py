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
from .models import Question, Translation, Language, Department, Phone, Player, Answer


class TranslationInline(admin.TabularInline):
    model = Translation


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ('department', 'translations__language__code')
    list_display = ('number', 'department', 'text_fr')
    search_fields = ['translations__text']
    inlines = [TranslationInline]

    def lookup_allowed(self, key, value):
        return True

    def text_fr(self, obj):
        fr = Translation.objects.filter(question=obj, language__code='fr').first()
        if fr :
            return fr.text
        return ''


class TranslationAdmin(admin.ModelAdmin):
    list_filter = ('question__department', 'language__code')
    list_display = ('id', 'code', 'text')

    def code(self, obj):
        return obj.language.code


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language', 'code', 'weight')


class DepartmentAdmin(admin.ModelAdmin):
    pass


class PhoneAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'dmx_channel')


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('sequence', 'code', 'correct', 'phone', 'pickup_time')
    can_delete = False
    max_num = 0
    readonly_fields = ('sequence', 'code', 'correct', 'phone', 'pickup_time')

    def code(self, obj):
        return obj.question.language.code


class PlayerAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]
    search_fields = ['id', 'name']
    ordering = ('-id',)
    list_display = ('id', 'name', 'state', 'score')
    list_filter = ('state', 'print_time', 'score')


class AnswerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Question, QuestionAdmin)
admin.site.register(Translation, TranslationAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Phone, PhoneAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Answer, AnswerAdmin)
