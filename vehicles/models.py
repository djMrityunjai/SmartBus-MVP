from django.db import models
from common.models import BaseMixin
from django.apps import apps

class Bus(BaseMixin):
    FUEL_TYPES = [
        ('DIESEL', 'Diesel'),
        ('CNG', 'CNG'),
        ('ELECTRIC', 'Electric'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('INACTIVE', 'Inactive'),
    ]

    registration_number = models.CharField(max_length=20, unique=True)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='buses')
    capacity = models.PositiveIntegerField()
    make = models.CharField(max_length=50)  # e.g., Tata, Ashok Leyland
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_due = models.DateField(null=True, blank=True)
    insurance_expiry = models.DateField()
    fitness_certificate_expiry = models.DateField()
    
    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'
        ordering = ['school', 'registration_number']

    def __str__(self):
        return f"{self.registration_number} - {self.school.name}"

class BusDocument(BaseMixin):
    DOCUMENT_TYPES = [
        ('INSURANCE', 'Insurance'),
        ('FITNESS', 'Fitness Certificate'),
        ('PERMIT', 'Permit'),
        ('TAX', 'Road Tax'),
        ('OTHER', 'Other')
    ]

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    document_file = models.FileField(upload_to='bus_documents/')
    
    class Meta:
        unique_together = ['bus', 'document_type']
        ordering = ['bus', 'document_type']

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.bus.registration_number}"

class SafetyCheckItem(BaseMixin):
    name = models.CharField(max_length=100)
    description = models.TextField()