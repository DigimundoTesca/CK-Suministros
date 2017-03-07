from django.contrib import admin

from orders.models import SupplierOrderDetail, SupplierOrder, CustomerOrderDetail, CustomerOrder


class SupplierOrderDetailInline(admin.TabularInline):
    model = SupplierOrderDetail
    extra = 1


@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'status', 'assigned_dealer',)
    inlines = [SupplierOrderDetailInline, ]


class CustomerOrderDetailInline(admin.TabularInline):
    model = CustomerOrderDetail
    extra = 1


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ('customer_user', 'created_at', 'delivery_date', 'price', 'status')
    inlines = [CustomerOrderDetailInline, ]
