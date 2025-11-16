from django.contrib import admin
from .models import Room, Booking, Service, ServiceOrder, Review

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'capacity', 'price_per_night', 'status')
    list_filter = ('status', 'capacity', 'price_per_night')
    search_fields = ('title', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'guest', 'check_in', 'check_out', 'status')
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = ('guest__username', 'room__title')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name', 'description')

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('booking', 'service', 'quantity', 'created_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'guest', 'created_at')
    search_fields = ('guest__username', 'booking__room__title', 'comment')
    readonly_fields = ('created_at',)