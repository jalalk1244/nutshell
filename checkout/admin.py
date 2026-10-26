from django.contrib import admin
from .models import Order, OrderLineItem, PaymentEvent

class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('product', 'quantity', 'unit_price', 'lineitem_total')
    extra = 0
    can_delete = False
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)
    readonly_fields = tuple(f.name for f in Order._meta.fields)
    list_display = ('order_number', 'date', 'payment_status', 'grand_total')
    ordering = ('-date',)
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    readonly_fields = tuple(f.name for f in PaymentEvent._meta.fields)
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
