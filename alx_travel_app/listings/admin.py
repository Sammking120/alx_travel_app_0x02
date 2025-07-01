from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'amount', 'status', 'transaction_id', 'created_at')
    search_fields = ('booking_reference', 'email')
    list_filter = ('status', 'created_at')
