from django.contrib import admin
from models import Config, Statistics


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'stats_date', 'creation')
