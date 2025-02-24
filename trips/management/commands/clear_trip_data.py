from django.core.management.base import BaseCommand
from django.db import transaction
from trips.models import Trip, TripStudent, TripLocation, TripEvent

class Command(BaseCommand):
    help = 'Clear all trip-related data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input('This will delete ALL trip data. Are you sure? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Operation cancelled.')
                return

        try:
            with transaction.atomic():
                # Delete in order to respect foreign key constraints
                trip_locations_count = TripLocation.objects.all().delete()[0]
                trip_events_count = TripEvent.objects.all().delete()[0]
                trip_students_count = TripStudent.objects.all().delete()[0]
                trips_count = Trip.objects.all().delete()[0]

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted:\n'
                        f'- {trips_count} trips\n'
                        f'- {trip_students_count} trip students\n'
                        f'- {trip_locations_count} trip locations\n'
                        f'- {trip_events_count} trip events'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing trip data: {str(e)}')
            )