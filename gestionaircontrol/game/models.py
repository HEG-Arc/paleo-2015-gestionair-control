from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _


def get_config_value(key):
    cached = cache.get('current_config')
    if not cached:
        cached = dict(Config.objects.values_list('key', 'value'))
        cache.set('current_config', cached, 300)
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

    # default_printer_ticket
    # ticket_url
    # minimum_score
    # number_wheel_prizes
    # wheel_duration
    # max_answers

