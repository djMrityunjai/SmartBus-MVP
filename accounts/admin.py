from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Parent, Driver

# Register your models here.

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone', 'user_type', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('email', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'user_type'),
        }),
    )

    inlines = [ProfileInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_type')
    list_filter = ('user__user_type',)
    search_fields = ('user__email', 'user__phone')
    
    def get_user_type(self, obj):
        return obj.user.get_user_type_display()
    get_user_type.short_description = 'User Type'

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_parent_name', 'get_phone', 'occupation', 'get_children_count')
    list_filter = ('user__user_type', 'preferred_language')
    search_fields = ('user__email', 'user__phone', 'user__first_name', 'user__last_name', 'occupation')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('occupation', 'work_address')
        }),
        ('Contact Information', {
            'fields': ('emergency_contact', 'preferred_language')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'latitude', 'longitude')
        }),
    )
    
    def get_parent_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_parent_name.short_description = 'Name'
    
    def get_phone(self, obj):
        return obj.user.phone
    get_phone.short_description = 'Phone'
    
    def get_children_count(self, obj):
        return obj.children.count()
    get_children_count.short_description = 'Number of Children'

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'license_number', 'license_expiry_date', 'years_of_experience')
    list_filter = ('school', 'license_type')
    search_fields = ('user__email', 'user__phone', 'license_number', 'user__first_name', 'user__last_name')
    date_hierarchy = 'license_expiry_date'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'school', 'date_of_birth', 'blood_group', 'emergency_contact')
        }),
        ('License Information', {
            'fields': ('license_number', 'license_type', 'license_issue_date', 
                      'license_expiry_date', 'license_issuing_authority')
        }),
        ('Experience', {
            'fields': ('years_of_experience', 'previous_employer')
        }),
        ('Documents', {
            'fields': ('license_document', 'police_verification', 'medical_certificate')
        }),
        ('Status', {
            'fields': ('last_background_check',)
        }),
    )
