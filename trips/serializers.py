from rest_framework import serializers
from trips.models import Trip, TripStudent, TripLocation, TripEvent
from schools.models import RouteStudent, Student
from accounts.models import Driver

class TripLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripLocation
        fields = ['id', 'trip', 'latitude', 'longitude', 'timestamp', 'speed']
        read_only_fields = ['id', 'timestamp']

class TripEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripEvent
        fields = ['id', 'trip', 'event_type', 'timestamp', 'description', 'latitude', 'longitude']
        read_only_fields = ['id', 'timestamp']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'name', 'grade', 'section', 'roll_number']
        read_only_fields = ['id']

class RouteStudentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    
    class Meta:
        model = RouteStudent
        fields = ['id', 'student', 'pickup_address', 'drop_address', 'sequence_number']
        read_only_fields = ['id']

class TripStudentSerializer(serializers.ModelSerializer):
    route_student = RouteStudentSerializer(read_only=True)
    route_student_id = serializers.PrimaryKeyRelatedField(
        queryset=RouteStudent.objects.all(),
        source='route_student',
        write_only=True
    )
    
    class Meta:
        model = TripStudent
        fields = [
            'id', 'trip', 'route_student', 'route_student_id', 'scheduled_time', 
            'actual_time', 'status', 'reported_by'
        ]
        read_only_fields = ['id', 'reported_by']

class TripStudentStatusUpdateSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = TripStudent
        fields = ['id', 'status', 'student_id']
        read_only_fields = ['id']
    
    def validate_student_id(self, value):
        try:
            student = Student.objects.get(student_id=value)
            return value
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student with this ID does not exist")

class DriverTripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'school', 'route', 'bus', 'driver', 'trip_type', 
                 'scheduled_start_time', 'actual_start_time', 'scheduled_end_time', 
                 'actual_end_time', 'status']
        read_only_fields = ['id', 'school', 'route', 'bus', 'driver', 'trip_type', 
                           'scheduled_start_time', 'scheduled_end_time']

class TripSerializer(serializers.ModelSerializer):
    trip_students = TripStudentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'school', 'route', 'bus', 'driver', 'trip_type', 
            'scheduled_start_time', 'actual_start_time', 'scheduled_end_time', 
            'actual_end_time', 'status', 'trip_students'
        ]
        read_only_fields = ['id']