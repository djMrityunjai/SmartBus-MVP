# Generated by Django 5.1.6 on 2025-02-23 16:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_first_name_user_last_name"),
        ("schools", "0004_student_city_student_latitude_student_longitude_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="driver",
            name="school",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="drivers",
                to="schools.school",
            ),
        ),
    ]
