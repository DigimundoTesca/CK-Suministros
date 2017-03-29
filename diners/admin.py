from django.contrib import admin
from diners.models import Diner, AccessLog


@admin.register(Diner)
class DinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'RFID', 'employee_number', 'created_at',)    
    ordering = ('created_at', 'name') 
    list_editable = ('name', 'RFID', 'employee_number')
    search_fields = ('name', 'RFID')


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'RFID', 'diner', 'access_to_room', )
    ordering = ('access_to_room',) 
    list_filter = ('diner', 'RFID', 'access_to_room', )
    search_fields = ('RFID',)
    date_hierarchy = 'access_to_room'
