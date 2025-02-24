from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from trips.models import Trip, TripStudent, TripLocation, TripEvent
from schools.models import School, Route, RouteStudent
from vehicles.models import Bus
from accounts.models import Driver
from datetime import timedelta, datetime
import random
import pytz

class Command(BaseCommand):
    help = 'Generate sample trip data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to generate trips for'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Indian timezone
        tz = pytz.timezone('Asia/Kolkata')
        
        # Typical school timings in India
        SCHOOL_TIMINGS = {
            'PICKUP': {
                'start_range': ('06:30', '07:30'),  # Pickup starts between 6:30-7:30 AM
                'duration': timedelta(minutes=45)    # Average pickup route duration
            },
            'DROP': {
                'start_range': ('14:00', '15:30'),  # Drop starts between 2:00-3:30 PM
                'duration': timedelta(minutes=45)    # Average drop route duration
            }
        }

        try:
            schools = School.objects.all()
            if not schools:
                self.stdout.write(self.style.ERROR('No schools found. Please run generate_sample_schools first.'))
                return

            total_trips_created = 0
            today = timezone.now().date()

            with transaction.atomic():
                # Generate trips for each day
                for day_offset in range(days):
                    current_date = today - timedelta(days=day_offset)
                    
                    for school in schools:
                        self.stdout.write(f'Creating trips for school: {school.name} on {current_date}')
                        
                        routes = Route.objects.filter(school=school)
                        buses = Bus.objects.filter(school=school, status='ACTIVE')
                        drivers = Driver.objects.filter(school=school)

                        if not (routes and buses and drivers):
                            continue

                        # Create pickup and drop trips for each route
                        for route in routes:
                            for trip_type, timing in SCHOOL_TIMINGS.items():
                                # Generate start time
                                start_hour, start_minute = map(int, timing['start_range'][0].split(':'))
                                start_minute += random.randint(0, 60)  # Random minutes
                                if start_minute >= 60:
                                    start_hour += 1
                                    start_minute -= 60
                                
                                scheduled_start = tz.localize(datetime.combine(
                                    current_date,
                                    datetime.min.time().replace(hour=start_hour, minute=start_minute)
                                ))
                                
                                scheduled_end = scheduled_start + timing['duration']
                                is_completed = current_date < today

                                # Create trip
                                trip = Trip.objects.create(
                                    school=school,
                                    route=route,
                                    bus=random.choice(buses),
                                    driver=random.choice(drivers),
                                    trip_type=trip_type,
                                    scheduled_start_time=scheduled_start,
                                    scheduled_end_time=scheduled_end,
                                    status='COMPLETED' if is_completed else 'SCHEDULED'
                                )

                                # Add actual times for completed trips
                                if is_completed:
                                    delay = random.randint(-5, 15)  # Random delay between -5 to +15 minutes
                                    trip.actual_start_time = scheduled_start + timedelta(minutes=delay)
                                    trip.actual_end_time = scheduled_end + timedelta(minutes=delay)
                                    trip.save()

                                # Create trip students
                                route_students = RouteStudent.objects.filter(route=route)
                                for route_student in route_students:
                                    # Calculate scheduled time based on sequence number
                                    time_offset = (route_student.sequence_number - 1) * 2  # 2 minutes between stops
                                    scheduled_time = scheduled_start + timedelta(minutes=time_offset)

                                    trip_student = TripStudent.objects.create(
                                        trip=trip,
                                        route_student=route_student,
                                        scheduled_time=scheduled_time,
                                        status='DROPPED_OFF' if is_completed else 'SCHEDULED'
                                    )

                                    # Add actual time for completed trips
                                    if is_completed:
                                        actual_delay = random.randint(-2, 5)  # Random delay between -2 to +5 minutes
                                        trip_student.actual_time = scheduled_time + timedelta(minutes=actual_delay)
                                        trip_student.save()

                                # Generate trip locations for completed trips
                                if is_completed:
                                    self.generate_trip_locations(trip)

                                # Generate trip events
                                self.generate_trip_events(trip)

                                total_trips_created += 1
                                self.stdout.write(f'Created {trip_type} trip for route: {route.name}')

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {total_trips_created} trips')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating trips: {str(e)}')
            )

    def generate_trip_locations(self, trip):
        """Generate location updates every 2 minutes for the trip duration"""
        if trip.actual_start_time and trip.actual_end_time:
            current_time = trip.actual_start_time
            while current_time <= trip.actual_end_time:
                TripLocation.objects.create(
                    trip=trip,
                    latitude=random.uniform(17.3850, 17.4950),  # Example: Hyderabad coordinates
                    longitude=random.uniform(78.3350, 78.4950),
                    timestamp=current_time,
                    speed=random.uniform(0, 40)  # Speed between 0-40 km/h
                )
                current_time += timedelta(minutes=2)

    def generate_trip_events(self, trip):
        """Generate relevant events for the trip"""
        # Create event timestamp based on trip status
        event_time = trip.actual_start_time if trip.status == 'COMPLETED' else trip.scheduled_start_time
        
        # Start event
        TripEvent.objects.create(
            trip=trip,
            event_type='START',
            timestamp=event_time,
            description='Trip started'
        )

        # Random events during trip (20% chance for delay)
        if trip.status == 'COMPLETED' and random.random() < 0.2:
            delay_time = event_time + timedelta(minutes=random.randint(5, 30))
            TripEvent.objects.create(
                trip=trip,
                event_type='DELAY',
                timestamp=delay_time,
                description='Traffic delay'
            )

        # End event
        end_time = trip.actual_end_time if trip.status == 'COMPLETED' else trip.scheduled_end_time
        TripEvent.objects.create(
            trip=trip,
            event_type='END',
            timestamp=end_time,
            description='Trip completed'
        )