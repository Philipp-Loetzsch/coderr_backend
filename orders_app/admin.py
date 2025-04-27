from django.contrib import admin
from .models import Order, Review

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer', 'offer_detail', 'buyer', 'seller', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('offer__title', 'buyer__username', 'seller__username')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'reviewer', 'reviewee', 'rating', 'created_at')
    search_fields = ('order__id', 'reviewer__username', 'reviewee__username', 'comment')

admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)