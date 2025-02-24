from django.core.management.base import BaseCommand
from django.utils import timezone
from vehicles.models import Bus, BusDocument
from schools.models import School
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate sample bus data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--buses-per-school',
            type=int,
            default=3,
            help='Number of buses to create per school'
        )

    def handle(self, *args, **options):
        buses_per_school = options['buses_per_school']
        
        # Bus makes and models
        BUS_MAKES = {
            'Tata': ['Starbus', 'Cityride', 'Skool'],
            'Ashok Leyland': ['Sunshine', 'MiTR', 'Lynx'],
            'Force': ['Traveller', 'Cruiser'],
            'Eicher': ['Skyline', 'Starline', 'Pro 2000']
        }
        
        # Get all schools
        schools = School.objects.all()
        if not schools:
            self.stdout.write(self.style.ERROR('No schools found. Please run generate_sample_schools first.'))
            return
            
        total_buses_created = 0
        
        try:
            for school in schools:
                self.stdout.write(f'Creating buses for school: {school.name}')
                
                for i in range(buses_per_school):
                    # Generate registration number
                    state_codes = ['MH', 'KA', 'TN', 'AP', 'TS', 'DL']
                    reg_number = f"{random.choice(state_codes)}-{random.randint(1, 99):02d}-{random.choice(['SC', 'BU'])}-{random.randint(1000, 9999)}"
                    
                    # Select random make and model
                    make = random.choice(list(BUS_MAKES.keys()))
                    model = random.choice(BUS_MAKES[make])
                    
                    # Create bus
                    bus = Bus.objects.create(
                        registration_number=reg_number,
                        school=school,
                        capacity=random.choice([20, 30, 40, 50]),
                        make=make,
                        model=model,
                        year=random.randint(2018, 2024),
                        fuel_type=random.choice(['DIESEL', 'CNG', 'ELECTRIC']),
                        status=random.choice(['ACTIVE', 'MAINTENANCE', 'INACTIVE']),
                        last_maintenance_date=timezone.now().date() - timedelta(days=random.randint(0, 90)),
                        next_maintenance_due=timezone.now().date() + timedelta(days=random.randint(30, 180)),
                        insurance_expiry=timezone.now().date() + timedelta(days=random.randint(180, 365)),
                        fitness_certificate_expiry=timezone.now().date() + timedelta(days=random.randint(180, 365))
                    )
                    
                    # Create documents for the bus
                    for doc_type, _ in BusDocument.DOCUMENT_TYPES:
                        BusDocument.objects.create(
                            bus=bus,
                            document_type=doc_type,
                            document_number=f"DOC{random.randint(10000, 99999)}",
                            issue_date=timezone.now().date() - timedelta(days=random.randint(0, 180)),
                            expiry_date=timezone.now().date() + timedelta(days=random.randint(180, 365)),
                            document_file='sample_document.pdf'  # You'll need to handle actual file upload
                        )
                    
                    total_buses_created += 1
                    self.stdout.write(f'Created bus: {bus.registration_number}')
                    
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {total_buses_created} buses')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating buses: {str(e)}')
            )