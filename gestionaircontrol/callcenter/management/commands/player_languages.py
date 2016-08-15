from django.core.management.base import BaseCommand, CommandError
from gestionaircontrol.callcenter.models import Player


class Command(BaseCommand):
    help = 'Recompute languages player field'

    def handle(self, *args, **options):
        count = 0
        for player in Player.objects.all():
            languages = []
            try:
                for answer in player.answers.all():
                    if answer.pickup_time and answer.hangup_time:
                        languages.append({'lang': answer.question.language.code, 'correct': int(answer.correct)})
                player.languages = languages
                player.save()
                count +=1
            except Exception as e:
                print e
        self.stdout.write('Successfully update %s players' % count)
