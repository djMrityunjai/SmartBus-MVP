from django.contrib import admin
from .models import Trip, TripStudent, TripLocation, TripEvent

# Register your models here.

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('route', 'bus', 'driver', 'trip_type', 'status', 'scheduled_start_time', 'school')
    list_filter = ('trip_type', 'status', 'school')
    search_fields = ('bus__registration_number', 'route__name', 'driver__user__first_name')
    date_hierarchy = 'scheduled_start_time'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('route', 'bus', 'driver', 'trip_type', 'status', 'school')
        }),
        ('Schedule', {
            'fields': ('scheduled_start_time', 'scheduled_end_time')
        }),
        ('Actual Times', {
            'fields': ('actual_start_time', 'actual_end_time')
        }),
    )

@admin.register(TripStudent)
class TripStudentAdmin(admin.ModelAdmin):
    list_display = ('trip', 'route_student', 'status')
    list_filter = ('status', 'trip__trip_type')
    search_fields = ('route_student__student__name', 'trip__route__name')

@admin.register(TripLocation)
class TripLocationAdmin(admin.ModelAdmin):
    list_display = ('trip', 'latitude', 'longitude', 'timestamp', 'speed')
    list_filter = ('trip__trip_type',)
    search_fields = ('trip__route__name',)
    date_hierarchy = 'timestamp'

@admin.register(TripEvent)
class TripEventAdmin(admin.ModelAdmin):
    list_display = ('trip', 'event_type', 'timestamp', 'description')
    list_filter = ('event_type',)
    search_fields = ('trip__route__name', 'description')
    date_hierarchy = 'timestamp'
