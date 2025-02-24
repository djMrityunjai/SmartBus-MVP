from django.contrib import admin
from django import forms
from .models import School, SchoolAdmin, Student, User, UserTypes, Route, RouteStudent

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
            'fields': ('email', 'contact_number', 'address', 'city', 'state', 'zip_code')
        }),
    )

@admin.register(SchoolAdmin)
class SchoolAdministratorAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'get_admin_name', 'get_email', 'school', 'designation', 'is_primary_admin', 'joined_date')
    list_display_links = ('get_display_name',)
    list_filter = ('school', 'is_primary_admin', 'designation')
    search_fields = ('user__email', 'user__phone', 'user__first_name', 'user__last_name', 'school__name')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'school')
        }),
        ('Role Information', {
            'fields': ('designation', 'is_primary_admin')
        }),
    )
    
    def get_display_name(self, obj):
        return str(obj)
    get_display_name.short_description = 'School Admin'
    
    def get_admin_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_admin_name.short_description = 'Admin Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(user_type=UserTypes.SCHOOL_ADMIN)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class RouteStudentForm(forms.ModelForm):
    pickup_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 30}))
    drop_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 30}))
    
    class Meta:
        model = RouteStudent
        fields = ('student', 'pickup_address', 'drop_address', 'sequence_number')

class RouteStudentInline(admin.TabularInline):
    model = RouteStudent
    form = RouteStudentForm
    extra = 1
    fields = ('sequence_number', 'student', 'pickup_address', 'drop_address')
    ordering = ('sequence_number',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'get_bus_info', 'get_students_count')
    list_filter = ('school', 'default_bus__status')
    search_fields = ('name', 'school__name', 'default_bus__registration_number')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'school', 'default_bus')
        }),
    )
    
    inlines = [RouteStudentInline]
    
    def get_bus_info(self, obj):
        if obj.default_bus:
            return f"{obj.default_bus.registration_number} ({obj.default_bus.get_status_display()})"
        return "No bus assigned"
    get_bus_info.short_description = 'Bus'
    
    def get_students_count(self, obj):
        return obj.students.count()
    get_students_count.short_description = 'Students'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('school', 'default_bus')

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
