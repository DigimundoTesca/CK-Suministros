from django.contrib import admin
from django.db.models import Sum

from sales.models import TicketDetail, Ticket
from actions import export_as_excel


class TicketDetailInline(admin.TabularInline):
    model = TicketDetail
    extra = 1


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'created_at', 'ticket_details', 'payment_type', 'total',)
    list_filter = ('seller', 'created_at', 'payment_type',)
    list_display_links = ('id', 'seller',)
    list_editable = ('created_at',)
    date_hierarchy = 'created_at'
    inlines = [TicketDetailInline, ]
    actions = (export_as_excel,)


@admin.register(TicketDetail)
class TicketDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'created_at', 'cartridge', 'package_cartridge', 'quantity', 'price',)
    list_display_links = ('id', 'ticket', )
    list_filter = ('ticket',)
    search_fields = ('ticket__created_at',)
    actions = (export_as_excel,)
