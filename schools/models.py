from django.db import models
from django.core.validators import RegexValidator
from accounts.models import User, UserTypes
from common.models import AddressMixin, BaseMixin

class School(AddressMixin, BaseMixin):
    name = models.CharField(max_length=255)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    contact_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    established_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class SchoolAdmin(BaseMixin):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': UserTypes.SCHOOL_ADMIN}
    )
    school = models.ForeignKey(
        School, 
        on_delete=models.CASCADE, 
        related_name='administrators'
    )
    designation = models.CharField(max_length=100)
    is_primary_admin = models.BooleanField(default=False)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.school}"

    def save(self, *args, **kwargs):
        if not self.user.user_type == UserTypes.SCHOOL_ADMIN:
            raise ValueError("User must be a school admin")
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['user', 'school']

class Student(BaseMixin):
    school = models.ForeignKey(
        School, 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    roll_number = models.CharField(max_length=20)
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=10) 
    section = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    
    # Guardian Information
    guardian_name = models.CharField(max_length=255)
    guardian_relation = models.CharField(max_length=50)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    guardian_phone = models.CharField(validators=[phone_regex], max_length=17)
    guardian_alternate_phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True
    )
    
    # Additional Information
    address = models.TextField()
    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.roll_number} ({self.school})"

    class Meta:
        unique_together = ['school', 'roll_number']
        ordering = ['grade', 'section', 'roll_number']
