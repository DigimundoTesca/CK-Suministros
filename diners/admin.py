
from django.contrib import admin
from diners.models import Diner 


@admin.register(Diner)
class DinerAdmin(admin.ModelAdmin):
    list_display = ('diner_id', 'created_at',)    
    ordering = ('created_at',) 