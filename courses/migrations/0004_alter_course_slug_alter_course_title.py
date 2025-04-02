# Generated by Django 4.2.5 on 2025-04-01 11:21

import courses.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0003_enrollment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="slug",
            field=courses.fields.AutoSlugField(),
        ),
        migrations.AlterField(
            model_name="course",
            name="title",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
