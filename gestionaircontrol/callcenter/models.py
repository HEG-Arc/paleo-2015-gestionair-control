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

# Core Django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Third-party app imports

# paleo2015 imports


# TODO: Should we internationalize the models?

class Game(models.Model):
    code = models.CharField(verbose_name=_("code"), max_length=15, unique=True, primary_key=True,
                            help_text=_("The identification code of the game"))
    team = models.CharField(verbose_name=_("team"), max_length=100,
                            help_text=_("The name of the team (this field is not unique!)"))
    start_time = models.DateTimeField(verbose_name=_("start time"), blank=True, null=True,
                                      help_text=_("The start time of the game"))
    end_time = models.DateTimeField(verbose_name=_("end time"), blank=True, null=True,
                                    help_text=_("The end time of the game"))
    canceled = models.BooleanField(verbose_name=_("canceled"), default=False, blank=True,
                                   help_text=_("A game is canceled in the case of a no-show (time slot + grace period"))
    initialized = models.BooleanField(verbose_name=_("initialized"), default=False, blank=True,
                                      help_text=_("A game is initialized when the team is ready to play"))


class Player(models.Model):
    number = models.IntegerField(verbose_name=_("player's number"), blank=True, null=True,
                                 help_text=_("The identification number of the player"))
    name = models.CharField(verbose_name=_("player's name"), max_length=100, blank=True, null=True,
                            help_text=_("The name of the player"))
    # Foreign keys
    game = models.ForeignKey('Game', verbose_name=_('game'), related_name=_('players'),
                             help_text=_("The game in which the player takes part"))


class Answer(models.Model):
    sequence = models.IntegerField(verbose_name=_("question sequence"),
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


class Question(models.Model):
    number = models.IntegerField(verbose_name=_("question number"), unique=True, primary_key=True,
                                 help_text=_("The number of the question"))
    # Foreign keys
    department = models.ForeignKey('Department', verbose_name=_('department'), related_name=_('questions'),
                                   help_text=_("The department concerned by the question (aka right answer)"))


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


class Language(models.Model):
    # TODO: Should we translate the names of the languages in DE and EN?
    code = models.CharField(verbose_name=_("language code"), max_length=2, unique=True, primary_key=True,
                            help_text=_("The ISO 3166-1 code of the language"))
    language = models.CharField(verbose_name=_("language name"), max_length=100,
                                help_text=_("The french name of the language"))
    flag = models.ImageField(verbose_name=_("flag file"), upload_to='flags',
                             help_text=_("The flag file of the language"))


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


class Phone(models.Model):
    number = models.IntegerField(verbose_name=_("phone number"), primary_key=True,
                                 help_text=_("The call number of the phone"))
    position_x = models.FloatField(verbose_name=_("x position"), null=True, blank=True,
                                   help_text=_("The position on the horizontal axis"))
    position_y = models.FloatField(verbose_name=_("y position"), null=True, blank=True,
                                   help_text=_("The position on the vertical axis"))
    orientation = models.IntegerField(verbose_name=_("orientation"), default=0, blank=True,
                                      help_text=_("The orientation of the phone in degrees"))


class Phonelog(models.Model):
    AVAILABLE = 0
    RESERVED = 1
    OFF_HOOK = 2
    DIALED = 3
    RINGING = 4
    REMOTE = 5
    UP = 6
    BUSY = 7
    CHANNEL_STATUS = (
        (AVAILABLE, _('Channel is down and available')),
        (RESERVED, _('Channel is down, but reserved')),
        (OFF_HOOK, _('Channel is off hook')),
        (DIALED, _('Digits (or equivalent) have been dialed')),
        (RINGING, _('Line is ringing')),
        (REMOTE, _('Remote end is ringing')),
        (UP, _('Line is up')),
        (BUSY, _('Line is busy')),
    )

    status = models.IntegerField(verbose_name=_("status of the channel"),
                                 choices=CHANNEL_STATUS, default=0,
                                 help_text=_("The current status of this channel"))
    timestamp = models.DateTimeField(verbose_name=_("timestamp"), auto_now_add=True,
                                     help_text=_("The timestamp of the log entry"))
    # Foreign keys
    phone = models.ForeignKey('Phone', verbose_name=_('phone'), related_name=_('logs'),
                              help_text=_("The related phone"))