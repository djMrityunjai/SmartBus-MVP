from django.contrib import admin
from .models import School, SchoolAdmin, Student

# Register your models here.

@admin.register(School)
class SchoolModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'contact_number', 'email')
    list_filter = ('city', 'state')
    search_fields = ('name', 'city', 'state', 'contact_number', 'email')
    date_hierarchy = 'established_date'

@admin.register(SchoolAdmin)
class SchoolAdministratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'designation', 'is_primary_admin', 'joined_date')
    list_filter = ('school', 'is_primary_admin', 'designation')
    search_fields = ('user__email', 'user__phone', 'school__name', 'designation')
    raw_id_fields = ('user', 'school')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'school', 'grade', 'section', 'guardian_name', 'guardian_phone')
    list_filter = ('school', 'grade', 'section', 'is_active')
    search_fields = (
        'name', 'student_id', 'roll_number', 
        'guardian_name', 'guardian_phone',
        'school__name'
    )
    date_hierarchy = 'enrolled_date'
    raw_id_fields = ('school',)
