# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.IntegerField(help_text='The sequence of the questions for a player', null=True, verbose_name='question sequence', blank=True)),
                ('answer', models.IntegerField(help_text='The answer key that was pressed during the game', null=True, verbose_name='answer given', blank=True)),
                ('pickup_time', models.DateTimeField(help_text='The pick up time of the call', verbose_name='pick up time')),
                ('hangup_time', models.DateTimeField(help_text='The hang up time of the call', null=True, verbose_name='hang up time', blank=True)),
                ('correct', models.IntegerField(help_text='This indicates if the answer is correct (1), false (0) or if there is no answer (NULL)', null=True, verbose_name='correct answer', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('number', models.IntegerField(help_text='The number of the department', unique=True, serialize=False, verbose_name='department number', primary_key=True)),
                ('name', models.CharField(help_text='The name of the department', max_length=50, verbose_name='department')),
                ('description', models.TextField(help_text='The description of the department', null=True, verbose_name='description', blank=True)),
                ('audio_file', models.FileField(help_text="The MP3 file of the department's description", upload_to=b'departments', null=True, verbose_name='audio file', blank=True)),
            ],
            options={
                'ordering': ['number'],
                'verbose_name': 'department',
                'verbose_name_plural': 'departments',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(primary_key=True, serialize=False, max_length=2, help_text='The ISO 3166-1 code of the language', unique=True, verbose_name='language code')),
                ('language', models.CharField(help_text='The french name of the language', max_length=100, verbose_name='language name')),
                ('flag', models.ImageField(help_text='The flag file of the language', upload_to=b'flags', verbose_name='flag file')),
                ('weight', models.IntegerField(default=1, help_text='The weight of the language in the random draw', verbose_name='language weight')),
            ],
            options={
                'ordering': ['language'],
                'verbose_name': 'language',
                'verbose_name_plural': 'languages',
            },
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('number', models.IntegerField(help_text='The call number of the phone', serialize=False, verbose_name='phone number', primary_key=True)),
                ('position_x', models.FloatField(help_text='The position on the horizontal axis', null=True, verbose_name='x position', blank=True)),
                ('position_y', models.FloatField(help_text='The position on the vertical axis', null=True, verbose_name='y position', blank=True)),
                ('orientation', models.IntegerField(default=0, help_text='The orientation of the phone in degrees', verbose_name='orientation', blank=True)),
                ('usage', models.IntegerField(default=60, help_text='The main use of this phone', verbose_name='phone usage', choices=[(10, 'Call Center Phone'), (11, 'Public Phone'), (12, 'Demo Phone'), (60, 'Test Phone')])),
                ('dmx_channel', models.IntegerField(default=1, help_text='The DMX channel of the LED strip decoder', verbose_name='DMX channel')),
            ],
            options={
                'ordering': ['number'],
                'verbose_name': 'phone',
                'verbose_name_plural': 'phones',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(help_text='The identification number of the player', null=True, verbose_name="player's number", blank=True)),
                ('name', models.CharField(help_text='The name of the player', max_length=100, null=True, verbose_name="player's name", blank=True)),
                ('email', models.CharField(help_text='Depending on the configuration, we ask for the email or not', max_length=100, null=True, verbose_name='email address', blank=True)),
                ('zipcode', models.CharField(help_text='Depending on the configuration, we ask for the zip or not', max_length=10, null=True, verbose_name='zip code', blank=True)),
                ('score', models.IntegerField(help_text='The final score of the player (computed at game end)', null=True, verbose_name="player's score", blank=True)),
                ('state', models.CharField(default=b'REGISTERED', help_text='The current state of the player in the game', max_length=20, verbose_name='player state', choices=[(b'REGISTERED', 'Registered'), (b'CODEPRINTED', 'Code printed'), (b'PLAYING', 'Playing'), (b'LIMITREACHED', 'Limit reached'), (b'SCANNED', 'Scanned'), (b'WON', 'Won')])),
                ('register_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('print_time', models.DateTimeField(null=True, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('last_answer_time', models.DateTimeField(null=True, blank=True)),
                ('limit_time', models.DateTimeField(null=True, blank=True)),
                ('scan_time', models.DateTimeField(null=True, blank=True)),
                ('wheel_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'player',
                'verbose_name_plural': 'players',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('number', models.IntegerField(help_text='The number of the question', unique=True, serialize=False, verbose_name='question number', primary_key=True)),
                ('department', models.ForeignKey(related_name='questions', verbose_name='department', to='callcenter.Department', help_text='The department concerned by the question (aka right answer)')),
            ],
            options={
                'ordering': ['number'],
                'verbose_name': 'question',
                'verbose_name_plural': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(help_text='The translated text of the question', null=True, verbose_name='translated question', blank=True)),
                ('audio_file', models.FileField(help_text='The MP3 file of the question', upload_to=b'questions', verbose_name='audio file')),
                ('language', models.ForeignKey(related_name='questions', verbose_name='language', to='callcenter.Language', help_text='The language of the translation')),
                ('question', models.ForeignKey(related_name='translations', verbose_name='question', to='callcenter.Question', help_text='The translated question')),
            ],
            options={
                'ordering': ['question', 'language'],
                'verbose_name': 'translation',
                'verbose_name_plural': 'translations',
            },
        ),
        migrations.AddField(
            model_name='answer',
            name='phone',
            field=models.ForeignKey(related_name='answers', verbose_name='phone', to='callcenter.Phone', help_text='The identifier of the phone used for this answer'),
        ),
        migrations.AddField(
            model_name='answer',
            name='player',
            field=models.ForeignKey(related_name='answers', verbose_name='player', to='callcenter.Player', help_text='The player who answered the question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(related_name='answers', verbose_name='question', to='callcenter.Translation', help_text='The question/language which was answered'),
        ),
    ]
