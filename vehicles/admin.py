from django.contrib import admin
from .models import Bus, BusDocument

# Register your models here.

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'school', 'capacity', 'status')
    list_filter = ('school', 'status', 'fuel_type')
    search_fields = ('registration_number', 'make', 'model')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('registration_number', 'school', 'capacity', 'status')
        }),
        ('Vehicle Details', {
            'fields': ('make', 'model', 'year', 'fuel_type')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance_date', 'next_maintenance_due')
        }),
        ('Documents', {
            'fields': ('insurance_expiry', 'fitness_certificate_expiry')
        }),
    )

@admin.register(BusDocument)
class BusDocumentAdmin(admin.ModelAdmin):
    list_display = ('bus', 'document_type', 'document_number', 'issue_date')
    list_filter = ('document_type',)
    search_fields = ('bus__registration_number', 'document_number')

# @admin.register(BusStop)
# class BusStopAdmin(admin.ModelAdmin):
#     list_display = ('name', 'latitude', 'longitude', 'address')
#     search_fields = ('name', 'address')
#     list_filter = ('created_at',)
