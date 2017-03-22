from django.contrib import admin
from diners.models import Diner, AccessLog


@admin.register(Diner)
class DinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'RFID', 'created_at',)    
    ordering = ('created_at', 'name') 
    list_editable = ('RFID',)


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'RFID', 'diner', 'access_to_room', )
    ordering = ('access_to_room',) 
    list_filter = ('diner', 'RFID', 'access_to_room')
    search_fields = ('diner', 'RFID')
    list_display_links = ('id', 'diner', 'RFID')


