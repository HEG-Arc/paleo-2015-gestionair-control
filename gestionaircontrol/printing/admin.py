from django.contrib import admin
from models import Printer


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ['name', 'exists']
    readonly_fields = ( 'exists',)
    actions = ['create_in_cups', 'delete_in_cups']

    def create_in_cups(self, request, queryset):
        for p in queryset:
            self.message_user(request, "%s" % p.create_in_cups())
    create_in_cups.short_description = "Create printer in cups"

    def delete_in_cups(self, request, queryset):
        for p in queryset:
            self.message_user(request, "%s" % p.delete_in_cups())
    delete_in_cups.short_description = "Delete printer in cups"