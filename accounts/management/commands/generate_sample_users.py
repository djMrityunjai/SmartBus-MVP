from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from accounts.models import User, Parent, Driver, UserTypes
from schools.models import School, Student
from faker import Faker
import random
from datetime import timedelta
from django.db.models import Count

fake = Faker('en_IN')  # Using Indian locale

class Command(BaseCommand):
    help = 'Generates sample parent and driver users'

    def add_arguments(self, parser):
        parser.add_argument('--parents_percent', type=int, default=70, 
                          help='Percentage of guardians to convert to registered parents (default: 70)')
        parser.add_argument('--drivers', type=int, default=20, 
                          help='Number of drivers to create')

    def create_user(self, user_type, phone, name=None):
        """Create a base user with the given type and phone"""
        email = fake.email() if random.random() < 0.7 else None  # 70% have email
        
        # Generate name if not provided
        if not name:
            first_name = fake.first_name()
            last_name = fake.last_name()
        else:
            # Split provided name into first and last name
            name_parts = name.split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        return User.objects.create(
            phone=phone,
            email=email,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )

    def create_parent_from_guardian(self, phone, student):
        """Create a parent profile from student's guardian information"""
        # Check if a user with this phone already exists
        if User.objects.filter(phone=phone).exists():
            return None
            
        # Use guardian name from student if available
        user = self.create_user(UserTypes.PARENT, phone, name=student.guardian_name)
        
        parent = Parent.objects.create(
            user=user,
            occupation=fake.job(),
            work_address=fake.address(),
            emergency_contact=student.guardian_alternate_phone or fake.phone_number(),
            preferred_language=random.choice(['English', 'Hindi', 'Tamil', 'Telugu'])
        )
        
        # Link this student to the parent
        student.link_to_parent(parent)
        
        # Try to find and link other students with the same guardian phone
        parent.link_children_by_phone()
        
        return parent

    def create_driver(self, school):
        """Create a driver profile"""
        phone = f"+91{fake.msisdn()[3:]}"  # Format: +91XXXXXXXXXX
        user = self.create_user(UserTypes.DRIVER, phone)
        
        # Generate realistic Indian license number
        # Format: SS-RRYYYYNNNNNN (State-RTO-Year-Number)
        states = ['AP', 'TN', 'KA', 'MH', 'DL']
        license_number = f"{random.choice(states)}{random.randint(1,38):02d}{random.randint(2010,2023)}{random.randint(100000,999999)}"
        
        issue_date = fake.date_between(start_date='-10y', end_date='-1y')
        expiry_date = fake.date_between(start_date='+1y', end_date='+10y')
        
        driver = Driver.objects.create(
            user=user,
            school=school,
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=50),
            blood_group=random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']),
            emergency_contact=f"+91{fake.msisdn()[3:]}",
            license_number=license_number,
            license_type=random.choice(['COMMERCIAL', 'HEAVY VEHICLE']),
            license_issue_date=issue_date,
            license_expiry_date=expiry_date,
            license_issuing_authority=f"RTO {random.choice(states)}",
            years_of_experience=random.randint(3, 15),
            previous_employer=fake.company() if random.random() < 0.7 else ''
        )
        return driver

    def handle(self, *args, **options):
        parents_percent = options['parents_percent']
        num_drivers = options['drivers']
        
        self.stdout.write('Starting sample user generation...')
        
        try:
            with transaction.atomic():
                # Get unique guardian phone numbers from students without parents
                # guardian_phones = Student.objects.filter(
                #     parent__isnull=True
                # ).values('guardian_phone').annotate(
                #     student_count=Count('id')
                # ).order_by('-student_count')  # Prioritize guardians with more students
                
                # total_guardians = len(guardian_phones)
                # num_parents_to_create = int(total_guardians * parents_percent / 100)
                
                # self.stdout.write(f'Creating parents for {num_parents_to_create} out of {total_guardians} guardians...')
                
                # parents_created = 0
                # for guardian in guardian_phones[:num_parents_to_create]:
                #     phone = guardian['guardian_phone']
                #     # Get first student for this guardian
                #     student = Student.objects.filter(guardian_phone=phone, parent__isnull=True).first()
                #     if student:
                #         parent = self.create_parent_from_guardian(phone, student)
                #         if parent:
                #             parents_created += 1
                #             self.stdout.write(f'Created parent: {parent} with phone: {phone}')
                
                # # Create drivers for each school
                self.stdout.write(f'Creating {num_drivers} drivers...')
                schools = list(School.objects.all())
                if not schools:
                    self.stdout.write('No schools found. Please run generate_sample_schools first.')
                    return
                
                for _ in range(num_drivers):
                    school = random.choice(schools)
                    driver = self.create_driver(school)
                    self.stdout.write(f'Created driver: {driver} for school: {school}')
                
            self.stdout.write(self.style.SUCCESS(
                f'Successfully generated {parents_created} parents and {num_drivers} drivers'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating sample users: {str(e)}'))