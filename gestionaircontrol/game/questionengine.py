import random
from gestionaircontrol.callcenter.models import Player, Answer, Translation, Phone, Department, Language
from django.core.cache import cache
from django.utils import timezone
from messaging import send_amqp_message

def compute_player_score(player):
    languages_queryset = Language.objects.values('code', 'weight')
    languages = []
    languages_scores = {}
    duration = 0
    correct = 0
    for l in languages_queryset:
        languages_scores[l['code']] = {'weight': l['weight'], 'correct': 0}
    for answer in player.answers.all():
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
    player.save()
    #TODO maybe save languages string in player for easy retrieval?
    return {'name': player.name, 'score': score, 'languages': languages, 'id': player.number}


def pick_next_question(player=None):
    if player:
        # TODO if number of attempts > X compute score and other message!
        answers = Answer.objects.prefetch_related('question').filter(player_id=player.id)
        departments_list = get_departments_numbers()  # List like [1, 2, 3, 4]
        languages_list = get_languages_codes()  # List like ['fr', 'de', 'en']
        departments = []
        questions = []
        for i in range(0, len(answers)/len(departments_list)+1):
            departments += departments_list
        # We remove departments previously drawn
        for answer in answers:
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
    return question


def agi_question(player_number, phone_number):
    phone = Phone.objects.get(number=phone_number)
    if phone.usage == Phone.CENTER and len(player_number) == 3:
        #TODO more filtering in query state <> WON?
        player = Player.objects.filter(id__endswith=player_number).order_by('-id').first()
        translation = pick_next_question(player)
        message = {'playerId': player.id, 'number': phone_number, 'flag': translation.language.code,
                   'type': 'PLAYER_ANSWERING', 'timestamp': timezone.now()}
        send_amqp_message(message, "simulation")
        new_answer = Answer(player=player, question=translation, phone=phone, pickup_time=timezone.now())
        new_answer.save()
        response = {'response': translation.question.department.number, 'phone_usage': phone.usage,
                    'file': "%s-%s" % (translation.question.number, translation.language.code),
                    'type': 'PLAYER_ANSWERING', 'answer_id': new_answer.id}
    else:
        translation = pick_next_question()
        response = {'response': translation.question.department.number, 'phone_usage': phone.usage,
                    'file': "%s-%s" % (translation.question.number, translation.language.code),
                    'type': 'PLAYER_ANSWERING', 'answer_id': None}

    return response


def agi_save(answer_id, answer_key, correct):
    print "NEW ANSWER %s %s %s" % (answer_id, answer_key, correct)
    if answer_id:
        answer = Answer.objects.get(pk=answer_id)
        answer.answer = answer_key
        answer.correct = correct
        answer.hangup_time = timezone.now()
        answer.save()
        response = {'type': 'PLAYER_ANSWERED', 'playerId': answer.player.id, 'correct': int(correct),
                    'number': answer.phone.number}
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

