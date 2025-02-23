from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from schools.models import School, SchoolAdmin, Student
from accounts.models import UserTypes, Profile
import random
from faker import Faker

# Create a Faker instance for India
fake = Faker(['en_IN'])

# Common Indian school types
SCHOOL_TYPES = ['Public', 'Private', 'International', 'CBSE', 'ICSE', 'State Board']

# Common Indian school names
SCHOOL_NAME_PREFIXES = [
    'Delhi', 'Kendriya', 'St.', 'Holy', 'Modern', 'DAV', 'Bharatiya', 'Saraswati',
    'Vidya', 'Shri', 'Sri', 'Maharishi', 'Royal', 'Global', 'National'
]

SCHOOL_NAME_SUFFIXES = [
    'Public School', 'International School', 'Vidyalaya', 'Academy',
    'High School', 'Higher Secondary School', 'Model School', 'Convent'
]

class Command(BaseCommand):
    help = 'Generates sample data for schools, including admins and students'

    def add_arguments(self, parser):
        parser.add_argument('--schools', type=int, default=5, help='Number of schools to create')
        parser.add_argument('--students-per-school', type=int, default=50, help='Number of students per school')

    def generate_school_name(self):
        prefix = random.choice(SCHOOL_NAME_PREFIXES)
        suffix = random.choice(SCHOOL_NAME_SUFFIXES)
        return f"{prefix} {suffix}"

    def generate_phone(self):
        # Generate Indian format phone number (10 digits)
        return f"+91{fake.msisdn()[-10:]}"

    def handle(self, *args, **options):
        User = get_user_model()
        num_schools = options['schools']
        students_per_school = options['students_per_school']

        self.stdout.write('Creating sample schools...')

        # Sample data for schools
        for i in range(num_schools):
            # Create school
            school = School.objects.create(
                name=self.generate_school_name(),
                address=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.postcode(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
                contact_number=self.generate_phone(),
                email=f"info@{fake.domain_name()}",
                website=f"https://www.{fake.domain_name()}",
                established_date=fake.date_between(start_date='-50y', end_date='-1y')
            )

            # Create school admin with more details
            admin_name = fake.name()
            domain = school.website.split('www.')[-1]
            admin_user = User.objects.create_user(
                email=f"admin_{i}@{domain}",
                password='Admin@123',
                phone=self.generate_phone(),
                user_type=UserTypes.SCHOOL_ADMIN,
                is_staff=True,
                is_active=True
            )
            
            # Create admin's profile
            Profile.objects.create(
                user=admin_user,
                address=school.address,  # Same as school address
                city=school.city,
                state=school.state,
                zip_code=school.zip_code,
                latitude=school.latitude,
                longitude=school.longitude,
                bio=f"Principal at {school.name} with extensive experience in education administration."
            )
            
            SchoolAdmin.objects.create(
                user=admin_user,
                school=school,
                designation='Principal',
                is_primary_admin=True
            )

            # Create students
            for j in range(students_per_school):
                grade = random.choice(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'])
                section = random.choice(['A', 'B', 'C', 'D'])
                
                Student.objects.create(
                    school=school,
                    roll_number=f"{grade}{section}{str(j+1).zfill(3)}",
                    student_id=f"{school.id}{str(j+1).zfill(5)}",
                    name=fake.name(),
                    grade=grade,
                    section=section,
                    date_of_birth=fake.date_between(start_date='-18y', end_date='-5y'),
                    gender=random.choice(['Male', 'Female']),
                    guardian_name=fake.name(),
                    guardian_relation=random.choice(['Father', 'Mother', 'Guardian']),
                    guardian_phone=self.generate_phone(),
                    address=f"{fake.street_address()}, {fake.city()}, {fake.state()}, {fake.postcode()}"
                )

            self.stdout.write(self.style.SUCCESS(f'Created school: {school.name} with {students_per_school} students'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_schools} schools with sample data'))