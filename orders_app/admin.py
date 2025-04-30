from django.contrib import admin
from .models import Order
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Order) 
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_offer_title', 
        'customer',       
        'get_seller_username', 
        'status',
        'created_at',
        'updated_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'id',
        'customer__username',
        'offer_detail__title',
        'offer_detail__offer__user__username'
    ]
    readonly_fields = ['created_at', 'updated_at']

    @admin.display(description='Offer Title')
    def get_offer_title(self, obj):
        if obj.offer_detail:
            return obj.offer_detail.title
        return None

    @admin.display(description='Seller')
    def get_seller_username(self, obj):
        if obj.offer_detail and obj.offer_detail.offer and obj.offer_detail.offer.user:
            seller = obj.offer_detail.offer.user
            return seller.username 
        return None