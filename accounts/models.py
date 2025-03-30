from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass


class Student(models.Model):
    class EducationChoices(models.TextChoices):
        High_school = "HIGH_SCHOOL", "High School"
        Bachelors = "BACHELORS", "Bachelors"
        Master = "MASTERS", "Masters"
        Phd = "PHD", "PhD"

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    birth_date = models.DateField()
    education = models.CharField(max_length=255, choices=EducationChoices.choices)
    phone_number = models.CharField(max_length=255)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )


class Instructor(models.Model):
    class EducationChoices(models.TextChoices):
        High_school = "HIGH_SCHOOL", "High School"
        Bachelors = "BACHELORS", "Bachelors"
        Master = "MASTERS", "Masters"
        Phd = "PHD", "PhD"

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField()
    education = models.CharField(max_length=255, choices=EducationChoices.choices)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
