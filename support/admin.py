from django.contrib import admin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'amount',
        'user',
        'payment_status',
        'created_at',
    )
    list_filter = (
        'payment_status',
        'created_at',
    )
    search_fields = (
        'stripe_session_id',
        'user__username',
        'user__email',
    )