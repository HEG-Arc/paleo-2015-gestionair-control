from django.contrib import admin
from models import Prize


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    pass
