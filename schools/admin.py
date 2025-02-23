from django.contrib import admin
from .models import School, SchoolAdmin, Student

# Register your models here.

@admin.register(School)
class SchoolModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'email', 'website')
    list_filter = ('created_at', 'is_active')
    search_fields = ('name', 'contact_number', 'email')
    date_hierarchy = 'established_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'website', 'established_date', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'contact_number', 'address', 'city', 'state', 'pincode')
        }),
    )

@admin.register(SchoolAdmin)
class SchoolAdministratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'designation', 'is_primary_admin', 'joined_date')
    list_filter = ('school', 'is_primary_admin')
    search_fields = ('user__email', 'user__phone', 'school__name')
    raw_id_fields = ('user', 'school')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'school', 'grade', 'section', 'guardian_name')
    list_filter = ('school', 'grade', 'section')
    search_fields = ('name', 'student_id', 'roll_number', 'guardian_name', 'guardian_phone')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'student_id', 'roll_number', 'school', 'grade', 'section', 'date_of_birth', 'gender')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_relation', 'guardian_phone', 'guardian_alternate_phone')
        }),
        ('Parent Information', {
            'fields': ('parent',)
        }),
    )
