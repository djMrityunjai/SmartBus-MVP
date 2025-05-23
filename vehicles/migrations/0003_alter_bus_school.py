# Generated by Django 5.1.6 on 2025-02-23 16:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0004_student_city_student_latitude_student_longitude_and_more"),
        ("vehicles", "0002_alter_bus_options_remove_bus_gps_device_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bus",
            name="school",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="buses",
                to="schools.school",
            ),
            preserve_default=False,
        ),
    ]
