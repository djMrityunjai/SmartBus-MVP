from django.core.management.base import BaseCommand
from django.db import transaction
from schools.models import School, Student, Route, RouteStudent
from vehicles.models import Bus
import random

class Command(BaseCommand):
    help = 'Generate sample routes with Indian locations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--routes-per-school',
            type=int,
            default=3,
            help='Number of routes to create per school'
        )

    def handle(self, *args, **options):
        routes_per_school = options['routes_per_school']
        
        # Indian area names and landmarks for different cities
        AREAS = {
            'Mumbai': [
                ('Andheri', ['Lokhandwala Complex', 'Infinity Mall', 'DN Nagar', 'Versova', 'Seven Bungalows']),
                ('Bandra', ['Linking Road', 'Carter Road', 'Bandstand', 'Pali Hill', 'Turner Road']),
                ('Powai', ['Hiranandani Gardens', 'IIT Bombay', 'Powai Plaza', 'Lake Homes', 'Central Avenue'])
            ],
            'Delhi': [
                ('Vasant Kunj', ['C Block', 'DDA Flats', 'Sector A', 'Priya Complex', 'B5-6']),
                ('Dwarka', ['Sector 12', 'Metro Station', 'Vegas Mall', 'Sector 21', 'Pacific Mall']),
                ('South Ex', ['Ring Road', 'Part 1', 'Part 2', 'AIIMS', 'Defence Colony'])
            ],
            'Bangalore': [
                ('Indiranagar', ['100 Feet Road', 'Defence Colony', 'HAL 2nd Stage', '12th Main', 'ESI Hospital']),
                ('Koramangala', ['4th Block', '5th Block', 'Forum Mall', 'Sony Signal', 'ST Bed Layout']),
                ('Whitefield', ['ITPL', 'Phoenix Mall', 'Forum Value', 'Hoodi Circle', 'Hope Farm'])
            ]
        }

        # Route name patterns
        ROUTE_PATTERNS = [
            "Route {area} {number}",
            "{area} Circuit {number}",
            "{area} Loop {number}",
            "Morning {area} {number}",
            "Evening {area} {number}"
        ]

        try:
            schools = School.objects.all()
            if not schools:
                self.stdout.write(self.style.ERROR('No schools found. Please run generate_sample_schools first.'))
                return

            total_routes_created = 0

            with transaction.atomic():
                for school in schools:
                    self.stdout.write(f'Creating routes for school: {school.name}')
                    
                    # Get available buses for this school
                    buses = list(Bus.objects.filter(school=school, status='ACTIVE'))
                    if not buses:
                        self.stdout.write(f'No active buses found for school: {school.name}')
                        continue

                    # Get students for this school
                    students = list(Student.objects.filter(school=school))
                    if not students:
                        self.stdout.write(f'No students found for school: {school.name}')
                        continue

                    # Select a random city and its areas
                    city = random.choice(list(AREAS.keys()))
                    city_areas = AREAS[city]

                    for i in range(routes_per_school):
                        # Select an area and its landmarks
                        area, landmarks = random.choice(city_areas)
                        
                        # Create route name
                        route_pattern = random.choice(ROUTE_PATTERNS)
                        route_name = route_pattern.format(area=area, number=i+1)

                        route = Route.objects.create(
                            name=route_name,
                            school=school,
                            default_bus=random.choice(buses)
                        )

                        # Assign random students to this route (between 10-20 students)
                        route_students = random.sample(students, min(random.randint(10, 20), len(students)))
                        
                        # Create route stops for each student
                        for seq, student in enumerate(route_students, 1):
                            # Create pickup and drop addresses using landmarks
                            landmark1 = random.choice(landmarks)
                            landmark2 = random.choice(landmarks)
                            
                            pickup = f"{random.randint(1, 999)}, {landmark1}, {area}, {city}"
                            drop = f"{random.randint(1, 999)}, {landmark2}, {area}, {city}"

                            RouteStudent.objects.create(
                                route=route,
                                student=student,
                                sequence_number=seq,
                                pickup_address=pickup,
                                drop_address=drop
                            )

                        total_routes_created += 1
                        self.stdout.write(f'Created route: {route_name} with {len(route_students)} students')

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {total_routes_created} routes')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating routes: {str(e)}')
            )