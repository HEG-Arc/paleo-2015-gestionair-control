from django.db import models
from django.utils.translation import ugettext_lazy as _

# TODO create a migration which loads inital data
class Config(models.Model):
    key = models.CharField(verbose_name=_("Config key"), max_length=250, blank=False, null=False, primary_key=True)
    value = models.TextField(verbose_name=_("value of this option"), blank=True, null=True)

    def __unicode__(self):
        return str(self.key)