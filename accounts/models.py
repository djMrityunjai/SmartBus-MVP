from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from common.models import AddressMixin

# Create your models here.

class UserTypes:
    ADMIN = 'admin'
    DRIVER = 'driver'
    PARENT = 'parent'
    SCHOOL_ADMIN = 'school_admin'
    
    CHOICES = [
        (ADMIN, 'Admin'),
        (DRIVER, 'Driver'),
        (PARENT, 'Parent'),
        (SCHOOL_ADMIN, 'School Admin'),
    ]

class CustomUserManager(BaseUserManager):
    def create_user(self, phone=None, email=None, password=None, **extra_fields):
        if not (phone or email):
            raise ValueError('Either phone number or email is required')
        
        if extra_fields.get('user_type') == UserTypes.ADMIN and not email:
            raise ValueError('Admin users must have an email address')
            
        if extra_fields.get('user_type') != UserTypes.ADMIN and not phone:
            raise ValueError('Non-admin users must have a phone number')
            
        user = self.model(
            phone=phone,
            email=self.normalize_email(email) if email else None,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', UserTypes.ADMIN)
        
        return self.create_user(email=email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=UserTypes.CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email if self.email else self.phone
    
    def clean(self):
        if self.user_type == UserTypes.ADMIN and not self.email:
            raise ValueError('Admin users must have an email address')
        if self.user_type != UserTypes.ADMIN and not self.phone:
            raise ValueError('Non-admin users must have a phone number')

class Profile(AddressMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"Profile of {self.user}"
