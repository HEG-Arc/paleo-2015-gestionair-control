# -*- coding: UTF-8 -*-
# models.py
#
# Copyright (C) 2015 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of paleo2015.
#
# paleo2015 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paleo2015 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paleo2015. If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
import datetime
import collections

# Core Django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _
from gestionaircontrol.game.models import get_config_value
from gestionaircontrol.wheel.models import Prize
from jsonfield import JSONField


def get_player_languages(player):
    languages = []
    for answer in Answer.objects.prefetch_related('question').filter(player_id=player.id, correct=1):
        if answer.question.language.code not in languages:
            languages.append(answer.question.language.code)
    return languages


class Player(models.Model):
    REGISTERED = 'CREATED'
    CODEPRINTED = 'PRINTED'
    PLAYING = 'PLAYING'
    LIMITREACHED = 'LIMIT_REACHED'
    SCANNED = 'SCANNED'
    WON = 'WON'
    PLAYER_STATE = (
        (REGISTERED, _('Registered')),
        (CODEPRINTED, _('Code printed')),
        (PLAYING, _('Playing')),
        (LIMITREACHED, _('Limit reached')),
        (SCANNED, _('Scanned')),
        (WON, _('Won')),
    )
    number = models.IntegerField(verbose_name=_("player's number"), blank=True, null=True,
                                 help_text=_("The identification number of the player"))
    name = models.CharField(verbose_name=_("player's name"), max_length=100, blank=True, null=True,
                            help_text=_("The name of the player"))
    email = models.CharField(verbose_name=_("email address"), max_length=100, blank=True, null=True,
                             help_text=_("Depending on the configuration, we ask for the email or not"))
    zipcode = models.CharField(verbose_name=_("zip code"), max_length=10, blank=True, null=True,
                               help_text=_("Depending on the configuration, we ask for the zip or not"))
    score = models.IntegerField(verbose_name=_("player's score"), blank=True, null=True,
                                help_text=_("The final score of the player (computed at game end)"))
    state = models.CharField(verbose_name=_("player state"), max_length=20,
                             choices=PLAYER_STATE, default=REGISTERED,
                             help_text=_("The current state of the player in the game"))
    register_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    print_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    last_answer_time = models.DateTimeField(blank=True, null=True)
    limit_time = models.DateTimeField(blank=True, null=True)
    scan_time = models.DateTimeField(blank=True, null=True)
    unlock_time = models.DateTimeField(blank=True, null=True)
    wheel_time = models.DateTimeField(blank=True, null=True)
    prize = models.ForeignKey(Prize, verbose_name=_('prize'), related_name=_('players'), blank=True, null=True,
                               help_text=_("The prize won by the player"))
    languages = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, null=True)

    @property
    def code(self):
        if len(str(self.id)) > 3:
            code = int(str(self.id)[-3:])
        else:
            code = self.id
        return code

    @property
    def url(self):
        return "%s%s%s" % (get_config_value('ticket_url'), get_config_value('event_id'), self.id)

    # TODO: saves languages information? or recompute?
    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")
        ordering = ['id']

    def __unicode__(self):
        return u'%s' % self.name


class Answer(models.Model):
    sequence = models.IntegerField(verbose_name=_("question sequence"), blank=True, null=True,
                                   help_text=_("The sequence of the questions for a player"))
    answer = models.IntegerField(verbose_name=_("answer given"), blank=True, null=True,
                                 help_text=_("The answer key that was pressed during the game"))
    pickup_time = models.DateTimeField(verbose_name=_("pick up time"),
                                       help_text=_("The pick up time of the call"))
    hangup_time = models.DateTimeField(verbose_name=_("hang up time"), blank=True, null=True,
                                       help_text=_("The hang up time of the call"))
    correct = models.IntegerField(verbose_name=_("correct answer"), null=True, blank=True,
                                  help_text=_("This indicates if the answer is correct (1), false (0) or if there is no answer (NULL)"))
    # Foreign keys
    player = models.ForeignKey('Player', verbose_name=_('player'), related_name=_('answers'),
                               help_text=_("The player who answered the question"))
    question = models.ForeignKey('Translation', verbose_name=_('question'), related_name=_('answers'),
                                 help_text=_("The question/language which was answered"))
    phone = models.ForeignKey('Phone', verbose_name=_("phone"), related_name=_('answers'),
                              help_text=_("The identifier of the phone used for this answer"))

    class Meta:
        ordering = ['sequence']

    def save(self, *args, **kwargs):
        if not self.sequence:
            self.sequence = Answer.objects.filter(player=self.player).count() + 1
        super(Answer, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s %s %s" % (self.player, self.question, 'correct' if self.correct else 'wrong')


class Question(models.Model):
    number = models.IntegerField(verbose_name=_("question number"), unique=True, primary_key=True,
                                 help_text=_("The number of the question"))
    # Foreign keys
    department = models.ForeignKey('Department', verbose_name=_('department'), related_name=_('questions'),
                                   help_text=_("The department concerned by the question (aka right answer)"))

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ['number']

    def __unicode__(self):
        return str(self.number)


class Translation(models.Model):
    text = models.TextField(verbose_name=_("translated question"), null=True, blank=True,
                            help_text=_("The translated text of the question"))
    audio_file = models.FileField(verbose_name=_("audio file"), upload_to='questions',
                                  help_text=_("The MP3 file of the question"))
    # Foreign keys
    question = models.ForeignKey('Question', verbose_name=_('question'), related_name=_('translations'),
                                 help_text=_("The translated question"))
    language = models.ForeignKey('Language', verbose_name=_('language'), related_name=_('questions'),
                                 help_text=_("The language of the translation"))

    class Meta:
        verbose_name = _("translation")
        verbose_name_plural = _("translations")
        ordering = ['question', 'language']

    def __unicode__(self):
        return u"%s (%s)" % (self.question, self.language.code)


class Language(models.Model):
    # TODO: Should we translate the names of the languages in DE and EN?
    code = models.CharField(verbose_name=_("language code"), max_length=2, unique=True, primary_key=True,
                            help_text=_("The ISO 3166-1 code of the language"))
    language = models.CharField(verbose_name=_("language name"), max_length=100,
                                help_text=_("The french name of the language"))
    flag = models.ImageField(verbose_name=_("flag file"), upload_to='flags',
                             help_text=_("The flag file of the language"))
    weight = models.IntegerField(verbose_name=_("language weight"), default=1,
                                 help_text=_("The weight of the language in the random draw"))

    class Meta:
        verbose_name = _("language")
        verbose_name_plural = _("languages")
        ordering = ['language']

    def __unicode__(self):
        return self.language


class Department(models.Model):
    # TODO: We also have the description in DE and EN!
    number = models.IntegerField(verbose_name=_("department number"), unique=True, primary_key=True,
                                 help_text=_("The number of the department"))
    name = models.CharField(verbose_name=_("department"), max_length=50,
                            help_text=_("The name of the department"))
    description = models.TextField(verbose_name=_("description"), blank=True, null=True,
                                   help_text=_("The description of the department"))
    audio_file = models.FileField(verbose_name=_("audio file"), upload_to='departments', blank=True, null=True,
                                  help_text=_("The MP3 file of the department's description"))

    class Meta:
        verbose_name = _("department")
        verbose_name_plural = _("departments")
        ordering = ['number']

    def __unicode__(self):
        return self.name


class Phone(models.Model):
    CENTER = 10
    PUBLIC = 11
    DEMO = 12
    TEST = 60
    PHONE_USAGE = (
        (CENTER, _('Call Center Phone')),
        (PUBLIC, _('Public Phone')),
        (DEMO, _('Demo Phone')),
        (TEST, _('Test Phone')),
    )
    number = models.IntegerField(verbose_name=_("phone number"), primary_key=True,
                                 help_text=_("The call number of the phone"))
    position_x = models.FloatField(verbose_name=_("x position"), null=True, blank=True,
                                   help_text=_("The position on the horizontal axis"))
    position_y = models.FloatField(verbose_name=_("y position"), null=True, blank=True,
                                   help_text=_("The position on the vertical axis"))
    orientation = models.IntegerField(verbose_name=_("orientation"), default=0, blank=True,
                                      help_text=_("The orientation of the phone in degrees"))
    usage = models.IntegerField(verbose_name=_("phone usage"),
                                choices=PHONE_USAGE, default=TEST,
                                help_text=_("The main use of this phone"))
    dmx_channel = models.IntegerField(verbose_name=_("DMX channel"), default=1,
                                      help_text=_("The DMX channel of the LED strip decoder"))

    class Meta:
        verbose_name = _("phone")
        verbose_name_plural = _("phones")
        ordering = ['number']

    def __unicode__(self):
        return u"%s (%s)" % (self.number, self.get_usage_display())

