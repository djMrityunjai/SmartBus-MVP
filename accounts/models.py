from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from common.models import AddressMixin, BaseMixin

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
    
    # Personal Information
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return (self.first_name + ' ' + self.last_name)
    
    def get_full_name(self):
        """Returns the user's full name or identifier"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.email if self.email else self.phone
    
    def get_short_name(self):
        """Returns the user's short name or identifier"""
        return self.first_name if self.first_name else self.get_full_name()
    
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

class Parent(AddressMixin, BaseMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': UserTypes.PARENT},
        related_name='parent_profile'
    )
    occupation = models.CharField(max_length=100, blank=True)
    work_address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    preferred_language = models.CharField(max_length=50, default='English')
    
    class Meta:
        ordering = ['user__email']
        
    def __str__(self):
        return f"Parent: {self.user}"

    def link_children_by_phone(self):
        """
        Links any existing students that have matching guardian phone numbers
        to this parent's profile.
        """
        from schools.models import Student
        # Find students with matching phone numbers
        potential_students = Student.objects.filter(
            models.Q(guardian_phone=self.user.phone) | 
            models.Q(guardian_alternate_phone=self.user.phone),
            parent__isnull=True  # Only unlinked students
        )
        
        for student in potential_students:
            student.link_to_parent(self)
        
        return potential_students.count()

    def verify_student_link(self, student):
        """
        Verifies if this parent should be linked to the given student
        based on phone number matching.
        """
        if not self.user.phone:
            return False
            
        return (
            student.guardian_phone == self.user.phone or 
            student.guardian_alternate_phone == self.user.phone
        )

    def link_student(self, student, force=False):
        """
        Links a student to this parent with validation.
        Set force=True to skip phone number validation.
        """
        if not force and not self.verify_student_link(student):
            raise ValueError("Phone number mismatch. Cannot link student to parent.")
            
        if student.parent and student.parent != self:
            raise ValueError("Student already linked to a different parent.")
            
        student.parent = self
        student.save()


class Driver(AddressMixin, BaseMixin):
    class Meta:
        base_manager_name = 'objects'
        related_name_prefix = 'accounts_driver'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': UserTypes.DRIVER},
        related_name='driver_profile'
    )
    # School Information
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='drivers',
        null=True,
        blank=True
    )
    
    # Personal Information
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=10)
    emergency_contact = models.CharField(max_length=17)
    
    # License Information
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=50)  # Commercial, Heavy Vehicle, etc.
    license_issue_date = models.DateField()
    license_expiry_date = models.DateField()
    license_issuing_authority = models.CharField(max_length=100)
    
    # Experience and Background
    years_of_experience = models.PositiveIntegerField()
    previous_employer = models.CharField(max_length=100, blank=True)
    
    # Documents
    license_document = models.FileField(upload_to='driver_documents/licenses/')
    police_verification = models.FileField(upload_to='driver_documents/verification/', null=True, blank=True)
    medical_certificate = models.FileField(upload_to='driver_documents/medical/', null=True, blank=True)
    
    # Status
    last_background_check = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['user__email']
        
    def __str__(self):
        return f"Driver: {self.user}"
        
    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # Validate license expiry
        if self.license_expiry_date and self.license_expiry_date < timezone.now().date():
            raise ValidationError("License has expired")
            
        # Validate date of birth (must be at least 18 years old)
        if self.date_of_birth:
            age = (timezone.now().date() - self.date_of_birth).days / 365.25
            if age < 18:
                raise ValidationError("Driver must be at least 18 years old")
