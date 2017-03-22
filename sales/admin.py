from django.contrib import admin
from django.db.models import Sum

from sales.models import TicketDetail, Ticket, TicketExtraIngredient
from actions import export_as_excel


class TicketDetailInline(admin.TabularInline):
    model = TicketDetail
    extra = 1


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number','seller', 'created_at', 'ticket_details', 'payment_type', 'total',)
    list_filter = ('seller', 'created_at', 'payment_type',)
    list_display_links = ('id', 'seller',)
    list_editable = ('created_at',)
    ordering = ('-created_at', )
    date_hierarchy = 'created_at'
    inlines = [TicketDetailInline, ]
    actions = (export_as_excel,)


class TicketExtraIngredientInline(admin.TabularInline):
    model = TicketExtraIngredient
    extra = 0


@admin.register(TicketDetail)
class TicketDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'created_at', 'cartridge', \
        'package_cartridge', 'extra_ingredients', 'quantity', 'price',)
    list_display_links = ('id', 'ticket', 'created_at')
    list_filter = ('ticket',)
    ordering = ('-ticket__created_at', )
    search_fields = ('ticket__created_at',)
    actions = (export_as_excel,)
    inlines = [TicketExtraIngredientInline, ]

