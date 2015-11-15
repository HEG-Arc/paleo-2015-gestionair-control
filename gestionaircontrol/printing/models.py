from django.db import models
from django.utils.translation import ugettext_lazy as _
import cups

class Printer(models.Model):
    name = models.CharField(verbose_name=_("cups printer name"), max_length=50, blank=False, null=False)
    uri = models.CharField(verbose_name=_("uri to printer"), max_length=250, blank=False, null=False)
    ppd = models.CharField(verbose_name=_("ppd file location"), max_length=250, blank=False, null=False)

    @property
    def exists(self):
        try:
            conn = cups.Connection()
            return self.name in conn.getPrinters()
        except Exception as e:
            return e

    def create_in_cups(self):
        try:
            conn = cups.Connection()
            conn.addPrinter(self.name, filename=self.ppd, device=self.uri)
            conn.acceptJobs(self.name)
            conn.enablePrinter(self.name)
        except Exception as e:
            return e

    def delete_in_cups(self):
        try:
            conn = cups.Connection()
            conn.deletePrinter(self.name)
        except Exception as e:
            return e

    def print_file(self, filename, options={}):
        try:
            conn = cups.Connection()
            return conn.printFile(self.name, filename, 'gestionair', options)
        except Exception as e:
                return e

    def __unicode__(self):
        return self.name

    @classmethod
    def list(cls):
        try:
            conn = cups.Connection()
            return conn.getPrinters()
        except Exception as e:
                return e
