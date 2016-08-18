from django.contrib import admin

from gestionaircontrol.game.pdf import ticket
from models import Printer


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ['name', 'exists']
    readonly_fields = ( 'exists',)
    actions = ['test_printer', 'create_in_cups', 'delete_in_cups']

    def create_in_cups(self, request, queryset):
        for p in queryset:
            self.message_user(request, "%s" % p.create_in_cups())
    create_in_cups.short_description = "Create printer in cups"

    def delete_in_cups(self, request, queryset):
        for p in queryset:
            self.message_user(request, "%s" % p.delete_in_cups())
    delete_in_cups.short_description = "Delete printer in cups"

    def test_printer(self, request, queryset):
        for p in queryset:
            # TODO remove dependency on game
            self.message_user(request, "%s" % p.print_file(ticket(self.name, '000', 'http://test')))
    test_printer.short_description = "Test printer"
