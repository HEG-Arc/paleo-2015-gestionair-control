from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from jsonfield import JSONField

CACHE_CONFIG_KEY = 'current_config'


def get_config():
    cached = cache.get(CACHE_CONFIG_KEY)
    if not cached:
        cached = dict(Config.objects.values_list('key', 'value'))
        cache.set(CACHE_CONFIG_KEY, cached, 300)
    return cached


def get_config_value(key):
    cached = get_config()
    if key in cached:
        return cached[key]
    return None


# TODO create a migration which loads inital data
class Config(models.Model):
    key = models.CharField(verbose_name=_("Config key"), max_length=250, blank=False, null=False, primary_key=True)
    value = models.TextField(verbose_name=_("value of this option"), blank=True, null=True)
    description = models.TextField(verbose_name=_("description of the key"), blank=True, null=True)

    def __unicode__(self):
        return str(self.key)

    # ticket_url = https://gestionair.ch/
    # minimum_score = 50
    # number_wheel_prizes
    # wheel_duration = 11000
    # max_answers = 5
    # default_ticket_printer = 'print-ticket'
    # label_printer = 'label'
    # min_phone_ringing = 1 # used in loop to determine if need to call a phone
    # agi_over_file
    # event_id = 'a' # identifier used in code exchange with web
    # default_frontend_url
    # %ip%


@receiver(post_save, sender=Config)
def delete_cache(sender, instance, **kwargs):
    cache.delete(CACHE_CONFIG_KEY)


class Statistics(models.Model):
    event_code = models.CharField(verbose_name=_("Event code"), max_length=10)
    event_name = models.CharField(verbose_name=_("Name of the event"), max_length=250, blank=True, null=True)
    stats_date = models.DateField(verbose_name=_("Date of the statistics"))
    creation = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    stats = JSONField()

