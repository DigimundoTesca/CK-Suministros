from django.contrib import admin
from diners.models import Diner, AccessLog, ElementToEvaluate, SatisfactionRating

from actions import export_as_excel


@admin.register(Diner)
class DinerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'RFID', 'employee_number', 'created_at',)    
    ordering = ('created_at', 'name') 
    list_editable = ('name', 'RFID', 'employee_number')
    search_fields = ('name', 'RFID', 'employee_number')
    actions = (export_as_excel,)


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'RFID', 'diner', 'access_to_room', )
    ordering = ('access_to_room',) 
    list_filter = ('diner', 'RFID', 'access_to_room', )
    search_fields = ('RFID',)
    date_hierarchy = 'access_to_room'


@admin.register(ElementToEvaluate)
class ElementToEvaluateAdmin(admin.ModelAdmin):
    list_display = ('id', 'priority', 'element', 'permanent', 'publication_date')
    ordering = ('priority', 'publication_date')
    list_editable = ('priority', 'permanent', 'publication_date')


@admin.register(SatisfactionRating)
class SatisfactionRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation_date', 'satisfaction_rating', 'shortened_suggestion', 'selected_elements')
    ordering = ('-creation_date',)
    list_display_links = ('id', 'creation_date',)
    date_hierarchy = 'creation_date'

    def selected_elements(self, obj):
        return ",\n".join([p.element for p in obj.elements.all()])

