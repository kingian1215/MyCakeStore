from django.contrib import admin
from.models import Cake, Order
# Register your models here.

@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user','cake','quantity','status','created_at')
    list_filter = ('status','created_at')
    search_fields = ('user__username','cake__name')