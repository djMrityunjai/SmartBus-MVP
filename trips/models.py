# trips/models.py
from django.db import models
from common.models import BaseMixin, LocationMixin
from vehicles.models import Bus
from accounts.models import Driver, User
from schools.models import Route, RouteStudent, School
from django.core.exceptions import ValidationError

class Trip(BaseMixin):
    TRIP_TYPES = [
        ('PICKUP', 'Pick Up'),
        ('DROP', 'Drop Off'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips', null=True, blank=True)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPES)
    scheduled_start_time = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    scheduled_end_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    class Meta:
        ordering = ['-scheduled_start_time']

    def __str__(self):
        return f"{self.get_trip_type_display()} - {self.route.name} - {self.scheduled_start_time}"

    def clean(self):
        if self.bus.school != self.school:
            raise ValidationError("Bus must belong to the same school")
        if self.driver and self.driver.school != self.school:
            raise ValidationError("Driver must belong to the same school")
        if self.route.school != self.school:
            raise ValidationError("Route must belong to the same school")
        if self.status != 'SCHEDULED' and not self.driver:
            raise ValidationError("A driver must be assigned before the trip can be started")

class TripStudent(BaseMixin):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('PICKED_UP', 'Picked Up'),
        ('DROPPED_OFF', 'Dropped Off'),
        ('ABSENT', 'Absent'),
        ('CANCELLED', 'Cancelled'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_students')
    route_student = models.ForeignKey(RouteStudent, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    actual_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['route_student__sequence_number']

    def __str__(self):
        return f"{self.route_student.student.name} - {self.trip.get_trip_type_display()}"

    def clean(self):
        if self.route_student.route != self.trip.route:
            raise ValidationError("Student must belong to the trip's route")

class TripLocation(BaseMixin, LocationMixin):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='locations')
    timestamp = models.DateTimeField(auto_now_add=True)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in km/h
    
    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.trip} - {self.timestamp}"

class TripEvent(BaseMixin, LocationMixin):
    EVENT_TYPES = [
        ('START', 'Trip Started'),
        ('END', 'Trip Ended'),
        ('PICKUP', 'Student Pick Up'),
        ('DROP', 'Student Drop Off'),
        ('DELAY', 'Delay'),
        ('BREAKDOWN', 'Vehicle Breakdown'),
        ('ACCIDENT', 'Accident'),
        ('OTHER', 'Other'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.trip} - {self.timestamp}"