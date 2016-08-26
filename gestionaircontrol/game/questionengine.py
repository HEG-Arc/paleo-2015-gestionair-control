import random
import json
import logging
from gestionaircontrol.callcenter.models import Player, Answer, Translation, Phone, Department, Language
from django.core.cache import cache
from django.utils import timezone

from gestionaircontrol.game.serializers import GamePlayerSerializer
from messaging import send_amqp_message
from gestionaircontrol.game.models import get_config_value

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def compute_player_score(player):
    languages_queryset = Language.objects.values('code', 'weight')
    languages = []
    languages_scores = {}
    duration = 0
    correct = 0
    for l in languages_queryset:
        languages_scores[l['code']] = {'weight': l['weight'], 'correct': 0}
    for answer in Answer.objects.prefetch_related('question').filter(player_id=player.id):
        correct_answer = False
        if answer.pickup_time and answer.hangup_time:
            if answer.correct:
                languages_scores[answer.question.language.code]['correct'] += 1
                correct += 1
                correct_answer = True
            duration += (answer.hangup_time - answer.pickup_time).seconds
        languages.append({'lang': answer.question.language.code, 'correct': int(correct_answer)})

    score_languages = 0
    for score in languages_scores:
        score_languages += languages_scores[score]['correct'] * 50 + languages_scores[score]['correct']/languages_scores[score]['weight'] * 30
    try:
        score_duration = correct / (duration*60)
    except ZeroDivisionError:
        score_duration = 0
    try:
        score_correct = correct / player.answers.count()
    except ZeroDivisionError:
        score_correct = 0
    score = int(score_languages + score_duration*5 + score_correct*5)
    player.score = score
    player.languages = languages
    player.save()
    return {'name': player.name, 'score': score, 'languages': languages, 'id': player.number}


def pick_next_question(player=None):
    last = "not"

    if player:
        answers = Answer.objects.prefetch_related('question').filter(player_id=player.id)

        if len(answers) == int(get_config_value('max_answers')) - 1:
            last = "last"

        departments_list = get_departments_numbers()  # List like [1, 2, 3, 4]
        languages_list = get_languages_codes()  # List like ['fr', 'de', 'en']
        departments = []
        questions = []
        for i in range(0, len(answers)/len(departments_list)+1):
            departments += departments_list
        # We remove departments previously drawn
        for answer in answers:
            if answer.question.question.department.number in departments:
                departments.remove(answer.question.question.department.number)
            questions.append(answer.question.question.number)
        # We draw a department and a language
        language = random.choice(languages_list)
        department = random.choice(departments)
        translations_list = Translation.objects.exclude(question__in=questions).filter(question__department__number=department, language__code=language)
        try:
            question = random.choice(translations_list)
        except IndexError:
            translations_list = Translation.objects.all()
            question = random.choice(translations_list)
    else:
        translations_list = Translation.objects.all()
        question = random.choice(translations_list)
    return question, last


def agi_question(player_number, phone_number):
    phone = Phone.objects.get(number=phone_number)
    if phone.usage == Phone.CENTER and len(player_number) == 3:
        player = Player.objects.filter(id__endswith=str(player_number)).order_by('-id').first()
        over = "not"
        last = "not"
        if player.state == Player.LIMITREACHED:
            response_code = None
            response_file = get_config_value('agi_over_file')
            answer_id = None
            over = "over"
        else:
            translation, last = pick_next_question(player)
            message = {'playerId': player.id, 'number': phone_number, 'flag': translation.language.code,
                       'type': 'PLAYER_ANSWERING', 'timestamp': timezone.now().isoformat()}
            send_amqp_message(message, "simulation")
            new_answer = Answer(player=player, question=translation, phone=phone, pickup_time=timezone.now())
            new_answer.save()
            response_code = translation.question.department.number
            response_file = "%s-%s" % (translation.question.number, translation.language.code)
            answer_id = new_answer.id
        response = {'response': response_code, 'phone_usage': phone.usage,
                    'file': response_file,
                    'type': 'PLAYER_ANSWERING', 'answer_id': answer_id, 'last': last, 'over': over}
    else:
        translation, last = pick_next_question()
        response = {'response': translation.question.department.number, 'phone_usage': phone.usage,
                    'file': "%s-%s" % (translation.question.number, translation.language.code),
                    'type': 'PLAYER_ANSWERING', 'answer_id': None, 'last': None, 'over': None}

    return response


def agi_save(answer_id, answer_key, correct):
    if answer_id:
        answer = Answer.objects.get(pk=answer_id)
        answer.answer = answer_key
        answer.correct = correct
        answer.hangup_time = timezone.now()
        answer.save()
        player = Player.objects.get(pk=answer.player.id)
        response = {'type': 'PLAYER_ANSWERED', 'playerId': player.id, 'correct': int(correct),
                    'number': answer.phone.number}
        send_amqp_message(response, "simulation")

        answers = Answer.objects.filter(player_id=player.id)
        if len(answers) >= int(get_config_value('max_answers')):
            player.state = Player.LIMITREACHED
            player.limit_time = timezone.now()
            player.save()

            # TODO: move in a celery task
            player_score = compute_player_score(player)
            # send score and player data to sync queue
            send_amqp_message({
                'code': '%s%s' % (get_config_value('event_id'), player.id),
                'json': GamePlayerSerializer(player).data
            }, 'sync')
            response = {'playerId': player.id, 'languages': player_score['languages'], 'score': player_score['score'],
                        'type': 'PLAYER_LIMIT_REACHED', 'timestamp': player.limit_time.isoformat()}
            send_amqp_message(response, "simulation")


def get_departments_numbers():
    cached = cache.get('departments_numbers', '')
    if cached:
        return cached
    else:
        departments = Department.objects.all()
        departments_numbers = []
        for department in departments:
            departments_numbers.append(department.number)
        # Expires after 300 seconds
        cache.set('departments_numbers', departments_numbers, 300)
        return departments_numbers


def get_languages_codes():
    cached = cache.get('languages_codes', '')
    if cached:
        return cached
    else:
        languages = Language.objects.all()
        weighted_languages_codes = []
        for language in languages:
            weighted_languages_codes.append((language.code, language.weight))
        # Expires after 300 seconds
        languages_codes = [val for val, cnt in weighted_languages_codes for i in range(cnt)]
        cache.set('languages_codes', languages_codes, 300)
        return languages_codes

