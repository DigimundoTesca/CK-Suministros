from django.contrib import admin
from diners.models import Diner, AccessLog


@admin.register(Diner)
class DinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'RFID',)    
    ordering = ('created_at', 'name') 


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'diner', 'access_to_room',)    
    ordering = ('access_to_room',) 

