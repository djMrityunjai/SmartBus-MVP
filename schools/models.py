from django.db import models
from django.core.validators import RegexValidator
from accounts.models import User, UserTypes
from common.models import AddressMixin, BaseMixin
from vehicles.models import Bus

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


class Student(BaseMixin, AddressMixin):
    school = models.ForeignKey(
        School, 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    parent = models.ForeignKey(
        'accounts.Parent',
        on_delete=models.SET_NULL,
        related_name='children',
        null=True,
        blank=True
    )
    roll_number = models.CharField(max_length=20)
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=10) 
    section = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    
    # Guardian Information (for guardians without accounts)
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
    enrolled_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.roll_number} ({self.school})"

    class Meta:
        unique_together = ['school', 'roll_number']
        ordering = ['grade', 'section', 'roll_number']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate that we don't have conflicting parent and guardian information
        if self.parent:
            if self.parent.user.phone != self.guardian_phone and self.parent.user.phone != self.guardian_alternate_phone:
                raise ValidationError({
                    'parent': 'Parent phone number does not match guardian contact information'
                })

    def link_to_parent(self, parent, force=False):
        """
        Links this student to a parent profile with validation.
        Set force=True to skip phone number validation.
        """
        if not force:
            if not parent.verify_student_link(self):
                raise ValueError("Phone number mismatch. Cannot link student to parent.")
        
        self.parent = parent
        # Update guardian information to match parent's information
        self.guardian_name = parent.user.get_full_name() or parent.user.email or parent.user.phone
        self.guardian_phone = parent.user.phone
        self.guardian_alternate_phone = parent.emergency_contact
        self.save()

    def get_guardian_info(self):
        """Returns guardian information, prioritizing registered parent if available"""
        if self.parent:
            return {
                'name': self.parent.user.get_full_name() or self.parent.user.email or self.parent.user.phone,
                'phone': self.parent.user.phone,
                'alternate_phone': self.parent.emergency_contact,
                'relation': 'Registered Parent'
            }
        return {
            'name': self.guardian_name,
            'phone': self.guardian_phone,
            'alternate_phone': self.guardian_alternate_phone,
            'relation': self.guardian_relation
        }


class Route(BaseMixin):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, through='RouteStudent')
    default_bus = models.ForeignKey(
        Bus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ['name', 'school']

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class RouteStudent(BaseMixin):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    pickup_address = models.TextField()
    drop_address = models.TextField()
    sequence_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ['route', 'student']
        ordering = ['sequence_number']
