# Generated by Django 5.1.6 on 2025-02-23 16:22

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_driver_parent"),
        ("schools", "0004_student_city_student_latitude_student_longitude_and_more"),
        ("trips", "0001_initial"),
        ("vehicles", "0002_alter_bus_options_remove_bus_gps_device_id_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="tripsafetycheck",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="tripsafetycheck",
            name="checked_by",
        ),
        migrations.RemoveField(
            model_name="tripsafetycheck",
            name="safety_item",
        ),
        migrations.RemoveField(
            model_name="tripsafetycheck",
            name="trip",
        ),
        migrations.AlterModelOptions(
            name="trip",
            options={"ordering": ["-scheduled_start_time"]},
        ),
        migrations.AddField(
            model_name="trip",
            name="driver",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trips",
                to="accounts.driver",
            ),
        ),
        migrations.AddField(
            model_name="trip",
            name="scheduled_end_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="trip",
            name="school",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trips",
                to="schools.school",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="trip",
            name="bus",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trips",
                to="vehicles.bus",
            ),
        ),
        migrations.AlterField(
            model_name="trip",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trips",
                to="schools.route",
            ),
        ),
        migrations.AlterField(
            model_name="trip",
            name="scheduled_start_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="trip",
            name="trip_type",
            field=models.CharField(
                choices=[("PICKUP", "Pick Up"), ("DROP", "Drop Off")], max_length=10
            ),
        ),
        migrations.CreateModel(
            name="TripEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("is_active", models.BooleanField(default=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("remarks", models.TextField(blank=True, null=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("START", "Trip Started"),
                            ("END", "Trip Ended"),
                            ("PICKUP", "Student Pick Up"),
                            ("DROP", "Student Drop Off"),
                            ("DELAY", "Delay"),
                            ("BREAKDOWN", "Vehicle Breakdown"),
                            ("ACCIDENT", "Accident"),
                            ("OTHER", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("description", models.TextField()),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="trips.trip",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="TripLocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("is_active", models.BooleanField(default=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("remarks", models.TextField(blank=True, null=True)),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "speed",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="locations",
                        to="trips.trip",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["timestamp"],
            },
        ),
        migrations.CreateModel(
            name="TripStudent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("is_active", models.BooleanField(default=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("remarks", models.TextField(blank=True, null=True)),
                ("scheduled_time", models.DateTimeField()),
                ("actual_time", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SCHEDULED", "Scheduled"),
                            ("PICKED_UP", "Picked Up"),
                            ("DROPPED_OFF", "Dropped Off"),
                            ("ABSENT", "Absent"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="SCHEDULED",
                        max_length=20,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "route_student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schools.routestudent",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trip_students",
                        to="trips.trip",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["route_student__sequence_number"],
            },
        ),
        migrations.DeleteModel(
            name="Attendance",
        ),
        migrations.DeleteModel(
            name="TripSafetyCheck",
        ),
    ]
